"""Servicio de clasificación con persistencia tolerante a fallos de Atlas."""

from __future__ import annotations

from typing import Any, List

from backend.models.exceptions import InvalidImageError, ModelMismatchError, MongoConnectionError
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader


class ClassificationResult:
    """Resultado interno de clasificación; no es una entidad de dominio."""

    def __init__(
        self,
        fruit_name: str,
        confidence: float,
        probabilities: List[float],
        saved: bool = False,
        warning: str | None = None,
    ) -> None:
        self.fruit_name = fruit_name
        self.confidence = float(confidence)
        self.probabilities = [float(p) for p in probabilities]
        self.saved = bool(saved)
        self.warning = warning


class ClassificationService:
    def __init__(
        self,
        model_loader: ModelLoader,
        image_processor: ImageProcessor,
        manifest: List[str] | None = None,
        prediction_service: Any = None,
    ) -> None:
        self.model_loader = model_loader
        self.image_processor = image_processor
        self.manifest = manifest or model_loader.class_names()
        self.prediction_service = prediction_service

    def classify(
        self, archivo: Any, image_name: str, persist: bool = True
    ) -> ClassificationResult:
        self.model_loader.validate_compatibility()
        entrada = self.image_processor.process(archivo)
        modelo = self.model_loader.get_model()
        prediccion = modelo.predict(entrada, verbose=0)[0]
        indice = int(prediccion.argmax())
        confianza = float(prediccion[indice]) * 100
        nombre_fruta = self.manifest[indice]
        probabilidades = [float(valor) for valor in prediccion]

        saved = False
        warning = None
        if persist and self.prediction_service is not None:
            try:
                self.prediction_service.register(
                    fruit_name=nombre_fruta,
                    confidence=confianza,
                    image_name=image_name,
                )
                saved = True
            except MongoConnectionError as exc:
                saved = False
                warning = f"No se pudo guardar en el historial: {exc}"

        return ClassificationResult(
            fruit_name=nombre_fruta,
            confidence=confianza,
            probabilities=probabilidades,
            saved=saved,
            warning=warning,
        )
