"""Correspondencia persistente entre índices del modelo y nombres de clase.

El archivo generado ``ml/class_indices.json`` se guarda junto al modelo y es
la única fuente de verdad para interpretar la salida softmax. Evita el error
clásico de asumir el orden alfabético de ``image_dataset_from_directory``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.models.exceptions import ModelMismatchError
from ml import config
from ml.class_manifest import load_manifest


@dataclass(frozen=True)
class ClassIndices:
    classes: List[str]
    class_to_index: Dict[str, int]
    index_to_class: Dict[str, str]
    input_size: List[int]
    input_range: List[int]
    normalization: str
    confidence_threshold: float
    trained_at: str = ""
    metrics: Dict[str, Any] | None = None

    @classmethod
    def from_names(cls, names: List[str], threshold: float) -> "ClassIndices":
        return cls(
            classes=list(names),
            class_to_index={nombre: i for i, nombre in enumerate(names)},
            index_to_class={str(i): nombre for i, nombre in enumerate(names)},
            input_size=list(config.IMAGE_SIZE),
            input_range=list(config.INPUT_RANGE),
            normalization=config.NORMALIZATION,
            confidence_threshold=float(threshold),
            trained_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_document(self) -> dict:
        return {
            "classes": self.classes,
            "class_to_index": self.class_to_index,
            "index_to_class": self.index_to_class,
            "input_size": self.input_size,
            "input_range": self.input_range,
            "normalization": self.normalization,
            "confidence_threshold": self.confidence_threshold,
            "trained_at": self.trained_at,
            "metrics": self.metrics or {},
        }


def save_indices(indices: ClassIndices, path: str | Path = config.INDICES_PATH) -> Path:
    destino = Path(path)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(indices.to_document(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destino


def load_indices(path: str | Path = config.INDICES_PATH) -> ClassIndices:
    archivo = Path(path)
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ModelMismatchError(
            f"No se encontró {archivo}. Vuelve a entrenar con python scripts/train.py."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ModelMismatchError(f"Archivo de clases inválido: {exc}") from exc

    clases = list(datos.get("classes", []))
    if len(clases) != 5 or any(not isinstance(c, str) for c in clases):
        raise ModelMismatchError("El archivo de clases debe contener cinco nombres.")

    indice_a_clase = datos.get("index_to_class", {})
    if indice_a_clase != {str(i): nombre for i, nombre in enumerate(clases)}:
        raise ModelMismatchError("La correspondencia índice → clase es inconsistente.")

    if datos.get("normalization") != config.NORMALIZATION:
        raise ModelMismatchError(
            "La normalización guardada no coincide con la esperada "
            f"({config.NORMALIZATION})."
        )

    try:
        umbral = float(datos.get("confidence_threshold", config.DEFAULT_CONFIDENCE_THRESHOLD))
    except (TypeError, ValueError) as exc:
        raise ModelMismatchError("Umbral de confianza inválido.") from exc

    return ClassIndices(
        classes=clases,
        class_to_index={nombre: i for i, nombre in enumerate(clases)},
        index_to_class=indice_a_clase,
        input_size=list(datos.get("input_size", config.IMAGE_SIZE)),
        input_range=list(datos.get("input_range", config.INPUT_RANGE)),
        normalization=datos["normalization"],
        confidence_threshold=umbral,
        trained_at=str(datos.get("trained_at", "")),
        metrics=datos.get("metrics") or {},
    )


def validate_with_manifest(indices: ClassIndices, manifest_path: str | Path) -> None:
    nombres_manifiesto = [clase.name for clase in load_manifest(manifest_path)]
    if indices.classes != nombres_manifiesto:
        raise ModelMismatchError(
            "El orden de clases del modelo no coincide con el manifiesto. "
            f"Modelo: {indices.classes}. Manifiesto: {nombres_manifiesto}."
        )
