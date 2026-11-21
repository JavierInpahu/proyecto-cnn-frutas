"""Modelo de dominio de una predicción almacenada en el historial."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from backend.models.exceptions import NotFoundError, ValidationError

CAMPOS_PREDICCION = {
    "_id",
    "fruit_name",
    "confidence",
    "image_name",
    "created_at",
    "thumbnail",
    "image_data",
    "image_meta",
}


@dataclass
class Prediction:
    """Predicción con sus campos de historial y los datos recuperables de la imagen."""

    fruit_name: str
    confidence: float
    image_name: str
    created_at: Optional[datetime] = None
    id: Optional[ObjectId] = None
    thumbnail: Optional[str] = None  # miniatura JPEG en base64, también en Atlas
    image_data: Optional[str] = None  # imagen original en base64, recuperable del historial
    image_meta: Optional[dict] = None  # ancho, alto, formato, peso y MIME del archivo

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def validate(self) -> None:
        if not self.fruit_name or not self.fruit_name.strip():
            raise ValidationError("El nombre de la fruta predicha es obligatorio.")
        try:
            confianza = float(self.confidence)
        except (TypeError, ValueError) as exc:
            raise ValidationError("La confianza debe ser un número.") from exc
        if not 0 <= confianza <= 100:
            raise ValidationError("La confianza debe estar entre 0 y 100.")
        if not self.image_name or not self.image_name.strip():
            raise ValidationError("El nombre de archivo de imagen es obligatorio.")

    def to_document(self) -> dict:
        documento: dict = {
            "fruit_name": self.fruit_name.strip(),
            "confidence": float(self.confidence),
            "image_name": self.image_name.strip(),
            "created_at": self.created_at,
        }
        if self.id is not None:
            documento["_id"] = self.id
        if self.thumbnail is not None:
            documento["thumbnail"] = self.thumbnail
        if self.image_data is not None:
            documento["image_data"] = self.image_data
        if self.image_meta is not None:
            documento["image_meta"] = self.image_meta
        return documento

    @classmethod
    def from_document(cls, documento: dict) -> "Prediction":
        return cls(
            id=documento.get("_id"),
            fruit_name=documento["fruit_name"],
            confidence=documento["confidence"],
            image_name=documento["image_name"],
            created_at=documento["created_at"],
            thumbnail=documento.get("thumbnail"),
            image_data=documento.get("image_data"),
            image_meta=documento.get("image_meta"),
        )

    def change_fruit_name(self, nuevo_nombre: str) -> "Prediction":
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValidationError("El nombre de la fruta no puede estar vacío.")
        self.fruit_name = nuevo_nombre.strip()
        # created_at se conserva sin modificar.
        return self
