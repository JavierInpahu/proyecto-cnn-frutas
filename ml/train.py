"""Entrenamiento reproducible de la CNN de FRUIT VISION.

Uso:
    python scripts/train.py --data-dir data/fruits-360-subset --epochs 15

El dataset debe tener la estructura:
    <data-dir>/Training/<nombre de clase>/*.jpg
    <data-dir>/Test/<nombre de clase>/*.jpg

El orden de clases se toma siempre de ``ml/class_manifest.json`` (o del
archivo indicado con --manifiesto) y se guarda en ``ml/class_indices.json``.
La normalización vive únicamente dentro del modelo (Rescaling 1/255).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from dataclasses import replace
from pathlib import Path
from typing import Tuple

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from tensorflow import keras

from ml import config
from ml.class_indices import ClassIndices, save_indices, validate_with_manifest
from ml.class_manifest import load_manifest
from ml.model import build_model


def _fijar_semilla(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def crear_datasets(
    data_dir: Path,
    clases: list[str],
    batch_size: int,
    seed: int,
) -> Tuple[tf.data.Dataset, tf.data.Dataset, tf.data.Dataset]:
    """Crea entrenamiento, validación y prueba; la imagen se entrega en 0-255."""
    entrenamiento_dir = data_dir / "Training"
    prueba_dir = data_dir / "Test"
    for directorio in (entrenamiento_dir, prueba_dir):
        if not directorio.is_dir():
            raise FileNotFoundError(
                f"No existe {directorio}. Ejecuta primero scripts/download_dataset.py "
                "o indica --data-dir con la ruta correcta."
            )
        for clase in clases:
            carpeta = directorio / clase
            if not carpeta.is_dir() or not any(carpeta.iterdir()):
                raise FileNotFoundError(f"Faltan imágenes de '{clase}' en {directorio}")

    argumentos = dict(
        labels="inferred",
        label_mode="categorical",
        class_names=clases,  # evita el orden alfabético por defecto
        image_size=config.IMAGE_SIZE,
        batch_size=batch_size,
        seed=seed,
    )
    train_ds = keras.utils.image_dataset_from_directory(
        entrenamiento_dir,
        validation_split=config.VALIDATION_SPLIT,
        subset="training",
        **argumentos,
    )
    val_ds = keras.utils.image_dataset_from_directory(
        entrenamiento_dir,
        validation_split=config.VALIDATION_SPLIT,
        subset="validation",
        **argumentos,
    )
    test_ds = keras.utils.image_dataset_from_directory(
        prueba_dir,
        shuffle=False,
        **argumentos,
    )
    automatico = tf.data.AUTOTUNE
    return (
        train_ds.prefetch(automatico),
        val_ds.prefetch(automatico),
        test_ds.prefetch(automatico),
    )


def _probabilidades(modelo: keras.Model, dataset: tf.data.Dataset) -> np.ndarray:
    return np.concatenate([modelo.predict(x, verbose=0) for x, _ in dataset], axis=0)


def _etiquetas(dataset: tf.data.Dataset) -> np.ndarray:
    return np.concatenate([np.argmax(y.numpy(), axis=1) for _, y in dataset], axis=0)


def calibrar_umbral(modelo: keras.Model, val_ds: tf.data.Dataset) -> float:
    """Umbral conservative: percentil 5 de la confianza de aciertos en validación.

    La confianza softmax no es una probabilidad calibrada y este rechazo no
    garantiza detectar cualquier imagen fuera de distribución; es una primera
    barrera auditable, no una garantía.
    """
    probabilidades = _probabilidades(modelo, val_ds)
    verdaderas = _etiquetas(val_ds)
    aciertos = probabilidades.max(axis=1)[probabilidades.argmax(axis=1) == verdaderas]
    if aciertos.size == 0:
        return config.DEFAULT_CONFIDENCE_THRESHOLD
    umbral = float(np.percentile(aciertos, 5))
    return float(np.clip(umbral, config.DEFAULT_CONFIDENCE_THRESHOLD, 0.90))


def graficar_curvas(historial: dict, ruta: Path) -> None:
    figuras, ejes = plt.subplots(1, 2, figsize=(12, 4.5))
    ejes[0].plot(historial["accuracy"], label="Entrenamiento")
    ejes[0].plot(historial["val_accuracy"], label="Validación")
    ejes[0].set_title("Accuracy")
    ejes[1].plot(historial["loss"], label="Entrenamiento")
    ejes[1].plot(historial["val_loss"], label="Validación")
    ejes[1].set_title("Pérdida")
    for eje in ejes:
        eje.set_xlabel("Época")
        eje.legend()
        eje.grid(alpha=0.25)
    figuras.tight_layout()
    figuras.savefig(ruta, dpi=140)
    plt.close(figuras)


def graficar_matriz(matriz: list, clases: list[str], ruta: Path) -> None:
    figuras, eje = plt.subplots(figsize=(7, 6))
    imagen = eje.imshow(np.array(matriz), cmap="Blues")
    eje.set_xticks(range(len(clases)), [c.replace(" 1", "") for c in clases], rotation=25)
    eje.set_yticks(range(len(clases)), [c.replace(" 1", "") for c in clases])
    eje.set_xlabel("Predicción")
    eje.set_ylabel("Clase real")
    eje.set_title("Matriz de confusión (Test)")
    for fila in range(len(clases)):
        for columna in range(len(clases)):
            eje.text(columna, fila, str(matriz[fila][columna]), ha="center", va="center")
    figuras.colorbar(imagen, ax=eje, shrink=0.8)
    figuras.tight_layout()
    figuras.savefig(ruta, dpi=140)
    plt.close(figuras)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Entrena y evalúa la CNN de FRUIT VISION.")
    parser.add_argument("--data-dir", default=str(config.DATA_DIR))
    parser.add_argument("--modelo", default=str(config.MODEL_PATH))
    parser.add_argument("--manifiesto", default=str(config.MANIFEST_PATH))
    parser.add_argument("--indices", default=str(config.INDICES_PATH))
    parser.add_argument("--reports-dir", default=str(config.REPORTS_DIR))
    parser.add_argument("--epochs", type=int, default=config.DEFAULT_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--seed", type=int, default=config.SEED)
    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="No reentrena: evalúa el modelo ya guardado y escribe clases, métricas y matriz.",
    )
    args = parser.parse_args(argv)

    _fijar_semilla(args.seed)
    clases = [clase.name for clase in load_manifest(args.manifiesto)]
    print(f"Clases (orden del manifiesto): {clases}")

    train_ds, val_ds, test_ds = crear_datasets(
        Path(args.data_dir), clases, args.batch_size, args.seed
    )
    print(
        "Imágenes: "
        f"train={len(train_ds) * args.batch_size} (aprox.), "
        f"val={len(val_ds) * args.batch_size} (aprox.), "
        f"test={len(test_ds) * args.batch_size} (aprox.)"
    )

    ruta_modelo = Path(args.modelo)
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    ruta_reportes = Path(args.reports_dir)
    ruta_reportes.mkdir(parents=True, exist_ok=True)

    if args.evaluate_only:
        if not ruta_modelo.exists():
            raise FileNotFoundError(
                f"No existe {ruta_modelo}. Entrena primero con python scripts/train.py."
            )
        print(f"Evaluando modelo guardado: {ruta_modelo}")
        modelo = keras.models.load_model(ruta_modelo)
        historial = None
    else:
        modelo = build_model(len(clases))
        modelo.summary()

        callback_mejor = keras.callbacks.ModelCheckpoint(
            filepath=str(ruta_modelo),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        )
        callback_parada = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        )
        callback_lr = keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", patience=2, factor=0.5, min_lr=1e-5
        )

        historial = modelo.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.epochs,
            callbacks=[callback_mejor, callback_parada, callback_lr],
        )
        # ModelCheckpoint guardó el mejor; recargarlo evita evaluar las últimas épocas.
        modelo = keras.models.load_model(ruta_modelo)

    umbral = calibrar_umbral(modelo, val_ds)
    probabilidades = _probabilidades(modelo, test_ds)
    verdaderas = _etiquetas(test_ds)
    predichas = probabilidades.argmax(axis=1)

    matriz = confusion_matrix(verdaderas, predichas, labels=range(len(clases)))
    informe = classification_report(
        verdaderas,
        predichas,
        labels=range(len(clases)),
        target_names=clases,
        output_dict=True,
        zero_division=0,
    )
    metricas = {
        "accuracy": float(accuracy_score(verdaderas, predichas)),
        "precision_weighted": float(precision_score(verdaderas, predichas, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(verdaderas, predichas, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(verdaderas, predichas, average="weighted", zero_division=0)),
        "precision_macro": float(precision_score(verdaderas, predichas, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(verdaderas, predichas, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(verdaderas, predichas, average="macro", zero_division=0)),
        "confusion_matrix": matriz.tolist(),
        "classification_report": informe,
        "test_samples": int(verdaderas.size),
        "confidence_threshold": umbral,
        "history": (
            {k: [float(v) for v in valores] for k, valores in historial.history.items()}
            if historial is not None
            else {}
        ),
        "dataset_source": config.DATASET_SOURCE,
        "normalization": config.NORMALIZATION,
        "class_order": clases,
    }

    with (ruta_reportes / "evaluation.json").open("w", encoding="utf-8") as archivo:
        json.dump(metricas, archivo, indent=2, ensure_ascii=False)
    (ruta_reportes / "classification_report.txt").write_text(
        classification_report(
            verdaderas,
            predichas,
            labels=range(len(clases)),
            target_names=clases,
            zero_division=0,
        ),
        encoding="utf-8",
    )
    if metricas["history"]:
        graficar_curvas(metricas["history"], ruta_reportes / "training_curves.png")
    else:
        print("Modo --evaluate-only: se omite training_curves.png (sin historial de épocas).")
    graficar_matriz(matriz.tolist(), clases, ruta_reportes / "confusion_matrix.png")

    indices = replace(
        ClassIndices.from_names(clases, umbral),
        metrics={
            k: v for k, v in metricas.items() if k not in {"history", "classification_report"}
        },
    )
    validate_with_manifest(indices, args.manifiesto)
    ruta_indices = save_indices(indices, args.indices)

    print("\n=== Evaluación en Test (datos no usados en entrenamiento) ===")
    for clave in ("accuracy", "precision_weighted", "recall_weighted", "f1_weighted"):
        print(f"{clave}: {metricas[clave]:.4f}")
    print(f"Umbral de rechazo: {umbral:.3f}")
    print(f"Modelo: {ruta_modelo.resolve()}")
    print(f"Clases: {ruta_indices.resolve()}")
    print(f"Reportes: {ruta_reportes.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
