"""Repositorio de frutas sobre la colección inyectada de MongoDB."""

from __future__ import annotations

from typing import List, Optional

from bson import ObjectId

from backend.models.exceptions import DuplicateFruitError, NotFoundError
from backend.models.fruit import Fruit

COLLATION_INSENSITIVA = {"locale": "en", "strength": 2}


class FruitRepository:
    def __init__(self, collection) -> None:
        self.collection = collection

    def _buscar_por_nombre(self, nombre: str) -> Optional[dict]:
        nombre = nombre.strip()
        documento = self.collection.find_one(
            {"name": nombre},
            collation=COLLATION_INSENSITIVA,
        )
        if documento is not None:
            return documento
        # Fallback para controladores (p. ej. mongomock) que no aplican collation.
        nombre_bajo = nombre.lower()
        for candidato in self.collection.find({}, {"name": 1}):
            if str(candidato.get("name", "")).strip().lower() == nombre_bajo:
                return candidato
        return None

    def create(self, fruit: Fruit) -> Fruit:
        fruit.validate()
        existente = self._buscar_por_nombre(fruit.name)
        if existente is not None:
            raise DuplicateFruitError(fruit.name)
        resultado = self.collection.insert_one(fruit.to_document())
        fruit.id = resultado.inserted_id
        return fruit

    def list_all(self, active_only: bool = False) -> List[Fruit]:
        filtro: dict = {}
        if active_only:
            filtro["active"] = True
        documentos = self.collection.find(filtro).sort("name", 1)
        return [Fruit.from_document(documento) for documento in documentos]

    def get_by_id(self, identificador: ObjectId) -> Fruit:
        documento = self.collection.find_one({"_id": identificador})
        if documento is None:
            raise NotFoundError("fruta", identificador)
        return Fruit.from_document(documento)

    def update(self, fruit: Fruit) -> Fruit:
        fruit.validate()
        existente = self._buscar_por_nombre(fruit.name)
        if existente is not None and existente.get("_id") != fruit.id:
            raise DuplicateFruitError(fruit.name)
        self.collection.replace_one({"_id": fruit.id}, fruit.to_document())
        return fruit

    def set_active(self, identificador: ObjectId, activo: bool) -> Fruit:
        fruit = self.get_by_id(identificador)
        fruit.set_active(activo)
        self.collection.replace_one({"_id": identificador}, fruit.to_document())
        return fruit

    def delete(self, identificador: ObjectId, confirmar: bool = False) -> None:
        if not confirmar:
            raise TypeError("La eliminación requiere confirmación explícita.")
        resultado = self.collection.delete_one({"_id": identificador})
        if resultado.deleted_count == 0:
            raise NotFoundError("fruta", identificador)

    def seed_from_manifest(self, clases) -> int:
        """Siembra idempotente desde el manifiesto; devuelve frutas creadas."""
        creadas = 0
        for entrada in clases:
            if self._buscar_por_nombre(entrada.name) is None:
                fruta = Fruit(
                    name=entrada.name,
                    scientific_name=entrada.scientific_name,
                    description=entrada.description,
                    active=True,
                )
                self.create(fruta)
                creadas += 1
        return creadas
