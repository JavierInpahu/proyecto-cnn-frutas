"""Servicio de clasificación con persistencia tolerante a fallos de Atlas."""

from __future__ import annotations

from typing import Any, List

from backend.models.exceptions import MongoConnectionError
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader
from ml.predictor import predict as predict_image


# Un documento de MongoDB no puede superar los 16 MB; la base64 crece ~33 %.
MAX_IMAGEN_BYTES = 12 * 1024 * 1024


def _datos_imagen(archivo: Any) -> tuple[str | None, str | None, dict | None]:
    """Devuelve miniatura, imagen original en base64 y metadatos del archivo.

    La imagen completa se guarda en Atlas para poder recuperarla desde el
    historial; la miniatura sirve para mostrarla sin descargar todo el dato.
    """
    getter = getattr(archivo, "getvalue", None)
    if getter is None:
        return None, None, None
    try:
        import base64
        import io

        from PIL import Image

        contenido = getter()
        with Image.open(io.BytesIO(contenido)) as imagen:
            ancho, alto = imagen.size
            formato = imagen.format
            rgb = imagen.convert("RGB")
            rgb.thumbnail((180, 180))
            buffer = io.BytesIO()
            rgb.save(buffer, format="JPEG", quality=75)

        metadatos = {
            "width": int(ancho),
            "height": int(alto),
            "format": formato,
            "size_bytes": len(contenido),
            "mime_type": getattr(archivo, "type", None),
        }
        metadatos = {clave: valor for clave, valor in metadatos.items() if valor is not None}
        miniatura = base64.b64encode(buffer.getvalue()).decode("ascii")
        original = (
            base64.b64encode(contenido).decode("ascii")
            if len(contenido) <= MAX_IMAGEN_BYTES
            else None
        )
        return miniatura, original, metadatos
    except Exception:
        return None, None, None


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
            thumbnail, image_data, image_meta = _datos_imagen(archivo)
            try:
                self.prediction_service.register(
                    fruit_name=nombre_fruta,
                    confidence=confianza,
                    image_name=image_name,
                    thumbnail=thumbnail,
                    image_data=image_data,
                    image_meta=image_meta,
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
