"""Pruebas unitarias de FruitRepository con mongomock (sin red)."""

from __future__ import annotations

import mongomock
import pytest

from backend.models.exceptions import DuplicateFruitError, NotFoundError, ValidationError
from backend.models.fruit import Fruit
from backend.repositories.fruit_repository import FruitRepository


def _coleccion():
    return mongomock.MongoClient()["DB_Frutas_Inpahu_test"]["fruits"]


def test_crear_fruta_almacena_cinco_campos_con_objectid() -> None:
    repo = FruitRepository(_coleccion())
    fruta = repo.create(
        Fruit(name="Banana 1", scientific_name="Musa acuminata", description="Plátano.")
    )
    assert fruta.id is not None
    documento = repo.collection.find_one({"_id": fruta.id})
    assert set(documento.keys()) == {"_id", "name", "scientific_name", "description", "active"}
    assert documento["active"] is True


def test_duplicado_ignorando_mayusculas_lanza_error() -> None:
    repo = FruitRepository(_coleccion())
    repo.create(Fruit(name="Banana 1", scientific_name="Musa acuminata", description="x"))
    with pytest.raises(DuplicateFruitError):
        repo.create(Fruit(name="banana 1", scientific_name="Musa acuminata", description="y"))


def test_datos_incompletos_lanzan_validation_error() -> None:
    repo = FruitRepository(_coleccion())
    with pytest.raises(ValidationError):
        repo.create(Fruit(name="", scientific_name="X", description="x"))


def test_listado_activas_excluye_desactivadas() -> None:
    repo = FruitRepository(_coleccion())
    repo.create(Fruit(name="Manzana", scientific_name="Malus", description="x", active=True))
    repo.create(Fruit(name="Pera", scientific_name="Pyrus", description="y", active=False))
    activas = repo.list_all(active_only=True)
    assert {f.name for f in activas} == {"Manzana"}


def test_consulta_por_id_inexistente_lanza_notfound() -> None:
    repo = FruitRepository(_coleccion())
    with pytest.raises(NotFoundError):
        repo.get_by_id(__import__("bson").ObjectId())


def test_actualizacion_no_cambia_id() -> None:
    repo = FruitRepository(_coleccion())
    fruta = repo.create(Fruit(name="Uva", scientific_name="Vitis", description="x"))
    fruta.description = "descripcion nueva"
    actualizada = repo.update(fruta)
    assert actualizada.id == fruta.id
    assert repo.get_by_id(fruta.id).description == "descripcion nueva"


def test_borrado_requiere_confirmacion() -> None:
    repo = FruitRepository(_coleccion())
    fruta = repo.create(Fruit(name="Kiwi", scientific_name="Actinidia", description="x"))
    with pytest.raises(TypeError):
        repo.delete(fruta.id)
    repo.delete(fruta.id, confirmar=True)
    with pytest.raises(NotFoundError):
        repo.get_by_id(fruta.id)


def test_siembra_es_idempotente_y_copia_metadatos() -> None:
    from ml.class_manifest import ClaseEntrenada

    clases = [
        ClaseEntrenada(name="Banana 1", scientific_name="Musa acuminata", description="Plátano."),
        ClaseEntrenada(name="Manzana", scientific_name="Malus", description="Manzana."),
    ]
    repo = FruitRepository(_coleccion())
    assert repo.seed_from_manifest(clases) == 2
    assert repo.seed_from_manifest(clases) == 0
    assert repo.collection.count_documents({}) == 2
    doc = repo.collection.find_one({"name": "Banana 1"})
    assert doc["scientific_name"] == "Musa acuminata"
    assert doc["description"] == "Plátano."
