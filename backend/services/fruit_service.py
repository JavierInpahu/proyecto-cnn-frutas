"""Servicio de catálogo de frutas con inyección de repositorio y manifiesto."""

from __future__ import annotations

from typing import List, Optional

from bson import ObjectId

from backend.models.exceptions import NotFoundError
from backend.models.fruit import Fruit
from ml.class_manifest import ClaseEntrenada


class FruitService:
    def __init__(self, repository, manifest: Optional[List[ClaseEntrenada]] = None) -> None:
        self.repository = repository
        self.manifest = manifest or []

    def create(self, name: str, scientific_name: str, description: str) -> Fruit:
        fruta = Fruit(name=name, scientific_name=scientific_name, description=description)
        return self.repository.create(fruta)

    def list(self, active_only: bool = False) -> List[Fruit]:
        return self.repository.list_all(active_only=active_only)

    def get(self, identificador: ObjectId) -> Fruit:
        return self.repository.get_by_id(identificador)

    def update(
        self,
        identificador: ObjectId,
        name: Optional[str] = None,
        scientific_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Fruit:
        fruta = self.repository.get_by_id(identificador)
        if name is not None:
            fruta.name = name
        if scientific_name is not None:
            fruta.scientific_name = scientific_name
        if description is not None:
            fruta.description = description
        return self.repository.update(fruta)

    def activate(self, identificador: ObjectId) -> Fruit:
        return self.repository.set_active(identificador, True)

    def deactivate(self, identificador: ObjectId) -> Fruit:
        return self.repository.set_active(identificador, False)

    def delete(self, identificador: ObjectId, confirmar: bool = False) -> None:
        self.repository.delete(identificador, confirmar=confirmar)

    def seed_catalog(self) -> int:
        return self.repository.seed_from_manifest(self.manifest)
