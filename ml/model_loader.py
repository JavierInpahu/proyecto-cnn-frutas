"""Carga y validación del modelo Keras contra el manifiesto de clases."""

from __future__ import annotations

from typing import List

from tensorflow.keras.models import Model, load_model

from backend.models.exceptions import ModelMismatchError
from ml.class_manifest import ClaseEntrenada, load_manifest


class ModelLoader:
    def __init__(
        self,
        model_path: str = "modelo_frutas.keras",
        manifest_path: str = "ml/class_manifest.json",
    ) -> None:
        self.model_path = model_path
        self.manifest_path = manifest_path
        self._model: Model | None = None
        self._manifest: List[ClaseEntrenada] | None = None

    def load(self) -> Model:
        if self._model is None:
            self._model = load_model(self.model_path)
        return self._model

    def get_model(self) -> Model:
        return self.load()

    def validate_compatibility(self) -> None:
        modelo = self.get_model()
        manifest = self.manifest()
        salidas = int(modelo.output_shape[-1]) if modelo.output_shape else 0
        if salidas != len(manifest):
            raise ModelMismatchError(
                f"El modelo tiene {salidas} salidas pero el manifiesto define "
                f"{len(manifest)} clases."
            )

    def manifest(self) -> List[ClaseEntrenada]:
        if self._manifest is None:
            self._manifest = load_manifest(self.manifest_path)
        return self._manifest

    def class_names(self) -> List[str]:
        return [clase.name for clase in self.manifest()]
