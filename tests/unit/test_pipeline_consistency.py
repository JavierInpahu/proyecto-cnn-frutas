"""Pruebas de consistencia: normalización, clases, rechazo e historial local."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from backend.models.exceptions import InvalidImageError
from backend.repositories.local_prediction_repository import LocalPredictionRepository
from ml.class_indices import load_indices
from ml.class_manifest import load_manifest
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader
from ml.predictor import FruitPredictor, predict

ROOT = Path(__file__).resolve().parents[2]


class _ModeloFalso:
    def __init__(self, vector):
        self.vector = np.asarray(vector, dtype=np.float32)

    def predict(self, entrada, verbose=0):
        return np.expand_dims(self.vector, axis=0)


class _CargadorFalso:
    manifest_path = "ml/class_manifest.json"

    def __init__(self, vector):
        self.modelo = _ModeloFalso(vector)

    def get_model(self):
        return self.modelo

    def validate_compatibility(self):
        return None

    def class_names(self):
        return [c.name for c in load_manifest(ROOT / "ml" / "class_manifest.json")]


class _ProcesadorFalso:
    def __init__(self):
        self.llamadas = 0

    def process(self, archivo):
        self.llamadas += 1
        return np.zeros((1, 100, 100, 3), dtype=np.float32)


def test_modelo_normaliza_dentro_y_procesador_no_divide() -> None:
    from tensorflow import keras

    modelo = keras.models.load_model(ROOT / "modelo_frutas.keras", compile=False)
    capas = [capa for capa in modelo.layers if getattr(capa, "name", "") == "normalizacion_unica"]
    assert len(capas) == 1, "Debe existir exactamente una capa de normalización."
    assert abs(float(capas[0].scale) - 1.0 / 255.0) < 1e-9

    codigo = inspect.getsource(ImageProcessor.process)
    assert "/ 255" not in codigo and "/255" not in codigo

    procesador = ImageProcessor()
    imagen_blanca = np.full((120, 120, 3), 255, dtype=np.uint8)
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.fromarray(imagen_blanca).save(buffer, format="PNG")
    entrada = procesador.process(buffer.getvalue())
    assert entrada.shape == (1, 100, 100, 3)
    assert entrada.max() > 1.0, "La entrada del modelo debe estar en 0-255."


def test_indices_coinciden_con_manifiesto() -> None:
    indices = load_indices(ROOT / "ml" / "class_indices.json")
    manifiesto = [clase.name for clase in load_manifest(ROOT / "ml" / "class_manifest.json")]
    assert indices.classes == manifiesto
    assert indices.normalization == "rescaling_1_over_255_inside_model"
    assert indices.input_size == [100, 100]
    for indice, nombre in enumerate(manifiesto):
        assert indices.index_to_class[str(indice)] == nombre
        assert indices.class_to_index[nombre] == indice


def test_rechazo_por_baja_confianza() -> None:
    vector = [0.24, 0.24, 0.26, 0.13, 0.13]
    procesador = _ProcesadorFalso()
    resultado = predict(
        _CargadorFalso(vector), procesador, "foto.png", threshold=0.90,
        indices_path=ROOT / "ml" / "class_indices.json",
    )
    assert procesador.llamadas == 1
    assert resultado.rejected is True
    assert resultado.reason is not None


def _imagenes_por_clase(nombres):
    """Usa las muestras incluidas en el ZIP; si está el dataset, usa su Test."""
    directorio_dataset = ROOT / "data" / "fruits-360-subset" / "Test"
    incluidas = ROOT / "tests" / "fixtures" / "dataset_samples"
    imagenes = []
    for nombre in nombres:
        if directorio_dataset.exists():
            imagenes.append(next((directorio_dataset / nombre).glob("*.jpg")))
        else:
            imagenes.append(incluidas / _NOMBRES_ARCHIVO[nombre])
    return imagenes


_NOMBRES_ARCHIVO = {
    "Apple Golden 1": "apple_golden_1.jpg",
    "Banana 1": "banana_1.jpg",
    "Orange 1": "orange_1.jpg",
    "Grape Blue 1": "grape_blue_1.jpg",
    "Pineapple 1": "pineapple_1.jpg",
}


def test_prediccion_no_se_concentra_en_una_clase() -> None:
    from tensorflow import keras

    modelo = keras.models.load_model(ROOT / "modelo_frutas.keras", compile=False)
    nombres = [c.name for c in load_manifest(ROOT / "ml" / "class_manifest.json")]
    procesador = ImageProcessor()
    resultados = []
    for nombre, imagen in zip(nombres, _imagenes_por_clase(nombres)):
        assert imagen.exists(), f"Falta la imagen de prueba para {nombre}: {imagen}"
        entrada = procesador.process(imagen.read_bytes())
        vector = modelo.predict(entrada, verbose=0)[0]
        resultados.append(nombres[int(vector.argmax())])
    aciertos = sum(esperado == obtenido for esperado, obtenido in zip(nombres, resultados))
    assert len(set(resultados)) >= 4, f"Predicciones poco diversas: {resultados}"
    assert aciertos >= 4, f"Falló más de una clase: {resultados}"


def test_imagen_ajena_es_rechazada() -> None:
    """El rechazo no garantiza detectar todo OOD, pero sí una imagen sin señal de fruta."""
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (100, 100), (128, 128, 128)).save(buffer, format="PNG")
    procesador = ImageProcessor()
    resultado = predict(
        _CargadorFalso([0.2] * 5),
        procesador,
        buffer.getvalue(),
        threshold=0.60,
        indices_path=ROOT / "ml" / "class_indices.json",
    )
    assert resultado.rejected is True


def _predictor_real() -> FruitPredictor:
    return FruitPredictor(ModelLoader(), ImageProcessor())


def test_cinco_frutas_reconocidas_sin_rechazo() -> None:
    nombres = [c.name for c in load_manifest(ROOT / "ml" / "class_manifest.json")]
    predictor = _predictor_real()
    for esperado, imagen in zip(nombres, _imagenes_por_clase(nombres)):
        resultado = predictor.predict(imagen.read_bytes())
        assert resultado.fruit_name == esperado
        assert resultado.rejected is False, f"{esperado} rechazada: {resultado.reason}"


def test_ruido_aleatorio_es_rechazado() -> None:
    import io

    from PIL import Image

    ruido = np.random.default_rng(20261120).integers(
        0, 256, size=(180, 180, 3), dtype=np.uint8
    )
    buffer = io.BytesIO()
    Image.fromarray(ruido, "RGB").save(buffer, format="PNG")
    resultado = _predictor_real().predict(buffer.getvalue())
    assert resultado.rejected is True
    assert "ruido" in (resultado.reason or "")


def test_imagen_ajena_por_distancia_es_rechazada() -> None:
    """Un degradado sin señal de fruta se rechaza aunque el softmax sea 100 %."""
    import io

    from PIL import Image

    pixeles = np.zeros((100, 100, 3), dtype=np.uint8)
    pixeles[:, :, 0] = np.linspace(0, 255, 100, dtype=np.uint8)[None, :]
    pixeles[:, :, 2] = 255 - pixeles[:, :, 0]
    buffer = io.BytesIO()
    Image.fromarray(pixeles, "RGB").save(buffer, format="PNG")
    resultado = _predictor_real().predict(buffer.getvalue())
    assert resultado.rejected is True
    assert "no se parece" in (resultado.reason or "")


def test_estructura_rechaza_escena_con_mucho_detalle() -> None:
    """Un fondo complejo con gradiente alto se rechaza aunque tenga contraste."""
    from ml.ood import rechazo_por_estructura

    columnas = (np.arange(100) % 2) * 255
    entrada = np.broadcast_to(columnas.reshape(1, 1, 100, 1), (1, 100, 100, 3))
    entrada = entrada.astype(np.float32).copy()
    motivo = rechazo_por_estructura(entrada)
    assert motivo is not None
    assert "ruido" in motivo


def _escena_sin_fondo_claro() -> np.ndarray:
    """Textura suave y contrastada, sin píxeles blancos: no es una fruta del dataset."""
    x = np.arange(100, dtype=np.float32)[None, :]
    y = np.arange(100, dtype=np.float32)[:, None]
    gris = 90 + 35 * np.sin(x / 9) + 20 * np.cos(y / 11)
    rgb = np.stack([gris, gris * 0.95, gris * 0.90], axis=-1)
    return np.clip(rgb, 0, 235).astype(np.float32)[None, ...]


def test_estructura_rechaza_escena_sin_fondo_claro() -> None:
    from ml.ood import rechazo_por_estructura

    entrada = _escena_sin_fondo_claro()
    assert (entrada[0].min(axis=2) >= 240).mean() == 0.0
    motivo = rechazo_por_estructura(entrada)
    assert motivo is not None
    assert "fondo claro" in motivo


def test_estructura_acepta_fruta_sobre_fondo_claro() -> None:
    from ml.ood import rechazo_por_estructura

    rgb = np.full((100, 100, 3), 255, dtype=np.float32)
    rgb[35:65, 35:65] = (180, 120, 60)
    assert rechazo_por_estructura(rgb[None, ...]) is None


def test_el_nombre_del_archivo_no_influye_en_la_prediccion() -> None:
    """La clasificación usa los bytes de la imagen, nunca un historial de nombres."""
    import io

    from PIL import Image

    class _Archivo(io.BytesIO):
        def __init__(self, datos: bytes, nombre: str) -> None:
            super().__init__(datos)
            self.name = nombre

    predictor = _predictor_real()
    fruta = (ROOT / "tests" / "fixtures" / "dataset_samples" / "apple_golden_1.jpg").read_bytes()
    buffer = io.BytesIO()
    Image.fromarray(_escena_sin_fondo_claro()[0].astype(np.uint8), "RGB").save(buffer, format="PNG")
    escena = buffer.getvalue()

    con_nombre_ajeno = predictor.predict(_Archivo(fruta, "cualquiera.png"))
    assert con_nombre_ajeno.rejected is False
    assert con_nombre_ajeno.fruit_name == "Apple Golden 1"

    con_nombre_de_fruta = predictor.predict(_Archivo(escena, "apple_golden_1.jpg"))
    assert con_nombre_de_fruta.rejected is True
    assert con_nombre_de_fruta.fruit_name == "No reconocido"


def test_metricas_reales_generadas() -> None:
    archivo = ROOT / "reports" / "evaluation.json"
    assert archivo.exists(), "Faltan las métricas del entrenamiento."
    metricas = json.loads(archivo.read_text(encoding="utf-8"))
    for clave in ("accuracy", "precision_weighted", "recall_weighted", "f1_weighted",
                  "confusion_matrix", "test_samples", "classification_report"):
        assert clave in metricas
    assert metricas["accuracy"] > 0.85
    assert len(metricas["confusion_matrix"]) == 5
    assert all(len(fila) == 5 for fila in metricas["confusion_matrix"])
    assert metricas["test_samples"] > 0
    assert (ROOT / "reports" / "training_curves.png").exists()
    assert (ROOT / "reports" / "confusion_matrix.png").exists()


def test_historial_local_crud(tmp_path: Path) -> None:
    repo = LocalPredictionRepository(tmp_path / "history.json")
    creada = repo.create(
        __import__("backend.models.prediction", fromlist=["Prediction"]).Prediction(
            fruit_name="Banana 1", confidence=91.5, image_name="banana.jpg", thumbnail="abc"
        )
    )
    assert repo.list_sorted()[0].fruit_name == "Banana 1"
    assert repo.get_by_id(creada.id).thumbnail == "abc"
    repo.update_fruit_name(creada.id, "Apple Golden 1")
    assert repo.list_sorted(fruit="Apple Golden 1")[0].confidence == 91.5
    repo.delete(creada.id, confirmar=True)
    assert repo.list_sorted() == []
