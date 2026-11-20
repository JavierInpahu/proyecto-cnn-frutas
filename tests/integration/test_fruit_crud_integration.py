"""Pruebas de integración de CRUD de frutas contra DB_Frutas_Inpahu_test.

Se ejecutan únicamente con `pytest -m integration` y requieren la URI de Atlas
configurada fuera del repositorio. Sin URI se omiten.
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from bson import ObjectId

from backend.models.fruit import Fruit
from backend.repositories.fruit_repository import FruitRepository


URI = os.environ.get("MONGODB_URI")

pytestmark = pytest.mark.integration


@pytest.fixture
def coleccion_frutas():
    if not URI:
        pytest.skip("Se requiere MONGODB_URI para pruebas de integración")
    from pymongo import MongoClient

    cliente = MongoClient(URI, serverSelectionTimeoutMS=8000)
    base = cliente["DB_Frutas_Inpahu_test"]
    coleccion = base["fruits"]
    yield coleccion
    cliente.drop_database("DB_Frutas_Inpahu_test")
    cliente.close()


def test_crud_completo(coleccion_frutas) -> None:
    repo = FruitRepository(coleccion_frutas)
    fruta = repo.create(
        Fruit(
            name=f"Integración {uuid4()}",
            scientific_name="Genus species",
            description="Prueba de integración.",
        )
    )
    assert fruta.id is not None

    obtenida = repo.get_by_id(fruta.id)
    assert obtenida.name == fruta.name

    activas = repo.list_all(active_only=True)
    assert any(f.id == fruta.id for f in activas)

    obtenida.description = "actualizada"
    repo.update(obtenida)
    assert repo.get_by_id(fruta.id).description == "actualizada"

    repo.set_active(fruta.id, False)
    assert not any(f.id == fruta.id for f in repo.list_all(active_only=True))

    repo.delete(fruta.id, confirmar=True)
    with pytest.raises(__import__("backend.models.exceptions", fromlist=["NotFoundError"]).NotFoundError):
        repo.get_by_id(fruta.id)
