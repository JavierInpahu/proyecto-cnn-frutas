"""Modelo de dominio de una fruta del catálogo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from bson import ObjectId

from backend.models.exceptions import DuplicateFruitError, NotFoundError, ValidationError


@dataclass
class Fruit:
    """Fruta con máximo cinco campos de representación: _id, name, scientific_name, description, active."""

    name: str
    scientific_name: str
    description: str
    active: bool = True
    id: Optional[ObjectId] = None

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("El nombre de la fruta es obligatorio.")
        if not self.scientific_name or not self.scientific_name.strip():
            raise ValidationError("El nombre científico de la fruta es obligatorio.")

    def to_document(self) -> dict:
        documento: dict = {
            "name": self.name.strip(),
            "scientific_name": self.scientific_name.strip(),
            "description": self.description.strip(),
            "active": bool(self.active),
        }
        if self.id is not None:
            documento["_id"] = self.id
        return documento

    @classmethod
    def from_document(cls, documento: dict) -> "Fruit":
        return cls(
            id=documento.get("_id"),
            name=documento["name"],
            scientific_name=documento["scientific_name"],
            description=documento.get("description", ""),
            active=documento.get("active", True),
        )

    def set_active(self, activo: bool) -> "Fruit":
        self.active = bool(activo)
        return self
