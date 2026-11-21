"""Servicio de clasificación con persistencia tolerante a fallos de Atlas."""

from __future__ import annotations

from typing import Any, List

from backend.models.exceptions import MongoConnectionError
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader
from ml.predictor import predict as predict_image


def _thumbnail(archivo: Any) -> str | None:
    """Miniatura base64 para el historial local; Atlas sigue guardando solo el nombre."""
    getter = getattr(archivo, "getvalue", None)
    if getter is None:
        return None
    try:
        import base64
        import io

        from PIL import Image

        imagen = Image.open(io.BytesIO(getter())).convert("RGB")
        imagen.thumbnail((180, 180))
        buffer = io.BytesIO()
        imagen.save(buffer, format="JPEG", quality=75)
        return base64.b64encode(buffer.getvalue()).decode("ascii")
    except Exception:
        return None


class ClassificationResult:
    """Resultado interno de clasificación; no es una entidad de dominio."""

    def __init__(
        self,
        fruit_name: str,
        confidence: float,
        probabilities: List[float],
        saved: bool = False,
        warning: str | None = None,
        rejected: bool = False,
        reason: str | None = None,
    ) -> None:
        self.fruit_name = fruit_name
        self.confidence = float(confidence)
        self.probabilities = [float(p) for p in probabilities]
        self.saved = bool(saved)
        self.warning = warning
        self.rejected = bool(rejected)
        self.reason = reason


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
        resultado = predict_image(
            self.model_loader,
            self.image_processor,
            archivo,
            manifest=self.manifest,
        )
        confianza = resultado.confidence
        nombre_fruta = resultado.fruit_name

        saved = False
        warning = resultado.reason
        if persist and self.prediction_service is not None and not resultado.rejected:
            try:
                self.prediction_service.register(
                    fruit_name=nombre_fruta,
                    confidence=confianza,
                    image_name=image_name,
                    thumbnail=_thumbnail(archivo),
                )
                saved = True
            except MongoConnectionError as exc:
                saved = False
                warning = f"{warning} No se pudo guardar en el historial: {exc}" if warning else (
                    f"No se pudo guardar en el historial: {exc}"
                )

        return ClassificationResult(
            fruit_name=nombre_fruta,
            confidence=confianza,
            probabilities=resultado.probabilities,
            saved=saved,
            warning=warning,
            rejected=resultado.rejected,
            reason=resultado.reason,
        )
