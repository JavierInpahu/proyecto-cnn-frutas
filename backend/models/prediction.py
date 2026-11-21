"""Modelo de dominio de una predicción almacenada en el historial."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from backend.models.exceptions import NotFoundError, ValidationError

CAMPOS_PREDICCION = {"_id", "fruit_name", "confidence", "image_name", "created_at"}


@dataclass
class Prediction:
    """Predicción con cinco campos exactamente: _id, fruit_name, confidence, image_name, created_at."""

    fruit_name: str
    confidence: float
    image_name: str
    created_at: Optional[datetime] = None
    id: Optional[ObjectId] = None
    thumbnail: Optional[str] = None  # solo historial local; nunca se envía a Atlas

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
        )

    def change_fruit_name(self, nuevo_nombre: str) -> "Prediction":
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValidationError("El nombre de la fruta no puede estar vacío.")
        self.fruit_name = nuevo_nombre.strip()
        # created_at se conserva sin modificar.
        return self
