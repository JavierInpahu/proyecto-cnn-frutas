"""Catálogo local en JSON, alternativa sin Atlas para ejecutar la app."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List
from uuid import uuid4

from backend.models.exceptions import DuplicateFruitError, NotFoundError
from backend.models.fruit import Fruit


class LocalFruitRepository:
    def __init__(self, path: str | Path = "data/fruits.json") -> None:
        self.path = Path(path)

    def _leer(self) -> List[dict]:
        if not self.path.exists():
            return []
        try:
            datos = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return datos if isinstance(datos, list) else []

    def _escribir(self, documentos: List[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporal = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as archivo:
                json.dump(documentos, archivo, indent=2, ensure_ascii=False)
            os.replace(temporal, self.path)
        finally:
            if os.path.exists(temporal):
                os.remove(temporal)

    def _buscar_por_nombre(self, nombre: str) -> dict | None:
        objetivo = nombre.strip().lower()
        return next(
            (d for d in self._leer() if str(d.get("name", "")).strip().lower() == objetivo),
            None,
        )

    def create(self, fruit: Fruit) -> Fruit:
        fruit.validate()
        if self._buscar_por_nombre(fruit.name) is not None:
            raise DuplicateFruitError(fruit.name)
        documentos = self._leer()
        fruit.id = uuid4().hex
        documento = fruit.to_document()
        documento["_id"] = fruit.id
        documentos.append(documento)
        self._escribir(documentos)
        return fruit

    def list_all(self, active_only: bool = False) -> List[Fruit]:
        documentos = self._leer()
        if active_only:
            documentos = [d for d in documentos if d.get("active", True)]
        documentos.sort(key=lambda d: str(d.get("name", "")))
        return [Fruit.from_document(d) for d in documentos]

    def _buscar(self, identificador) -> tuple[List[dict], int]:
        documentos = self._leer()
        for indice, documento in enumerate(documentos):
            if str(documento.get("_id")) == str(identificador):
                return documentos, indice
        raise NotFoundError("fruta", identificador)

    def get_by_id(self, identificador) -> Fruit:
        documentos, indice = self._buscar(identificador)
        return Fruit.from_document(documentos[indice])

    def update(self, fruit: Fruit) -> Fruit:
        fruit.validate()
        documentos, indice = self._buscar(fruit.id)
        existente = self._buscar_por_nombre(fruit.name)
        if existente is not None and str(existente.get("_id")) != str(fruit.id):
            raise DuplicateFruitError(fruit.name)
        documento = fruit.to_document()
        documento["_id"] = fruit.id
        documentos[indice] = documento
        self._escribir(documentos)
        return fruit

    def set_active(self, identificador, activo: bool) -> Fruit:
        documentos, indice = self._buscar(identificador)
        documentos[indice]["active"] = bool(activo)
        self._escribir(documentos)
        return self.get_by_id(identificador)

    def delete(self, identificador, confirmar: bool = False) -> None:
        if not confirmar:
            raise TypeError("La eliminación requiere confirmación explícita.")
        documentos, indice = self._buscar(identificador)
        documentos.pop(indice)
        self._escribir(documentos)

    def seed_from_manifest(self, clases) -> int:
        creadas = 0
        for entrada in clases:
            if self._buscar_por_nombre(entrada.name) is None:
                self.create(
                    Fruit(
                        name=entrada.name,
                        scientific_name=entrada.scientific_name,
                        description=entrada.description,
                        active=True,
                    )
                )
                creadas += 1
        return creadas
