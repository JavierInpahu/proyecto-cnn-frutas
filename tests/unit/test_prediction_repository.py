"""Pruebas unitarias de PredictionRepository con mongomock (sin red)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import mongomock
import pytest

from backend.models.exceptions import NotFoundError, ValidationError

from backend.models.exceptions import NotFoundError, ValidationError
from backend.models.prediction import Prediction
from backend.repositories.prediction_repository import PredictionRepository


def _coleccion():
    return mongomock.MongoClient()["DB_Frutas_Inpahu_test"]["predictions"]


def test_registro_almacena_cinco_campos_y_utc() -> None:
    repo = PredictionRepository(_coleccion())
    prediccion = repo.create(
        Prediction(fruit_name="Banana 1", confidence=82.5, image_name="foto.png")
    )
    assert prediccion.id is not None
    documento = repo.collection.find_one({"_id": prediccion.id})
    assert set(documento.keys()) == {"_id", "fruit_name", "confidence", "image_name", "created_at"}
    assert documento["created_at"].replace(microsecond=0) == prediccion.created_at.replace(
        tzinfo=None, microsecond=0
    )


def test_confianza_fuera_de_rango_no_se_almacena() -> None:
    repo = PredictionRepository(_coleccion())
    with pytest.raises(ValidationError):
        repo.create(Prediction(fruit_name="Banana 1", confidence=110, image_name="foto.png"))
    with pytest.raises(ValidationError):
        repo.create(Prediction(fruit_name="Banana 1", confidence=-5, image_name="foto.png"))


def test_listado_es_descendente_por_fecha() -> None:
    repo = PredictionRepository(_coleccion())
    ahora = datetime.now(timezone.utc)
    repo.create(Prediction(fruit_name="A", confidence=50, image_name="a.png", created_at=ahora))
    repo.create(
        Prediction(fruit_name="B", confidence=60, image_name="b.png", created_at=ahora + timedelta(seconds=10))
    )
    lista = repo.list_sorted()
    assert [p.fruit_name for p in lista] == ["B", "A"]


def test_consulta_por_id_inexistente_lanza_notfound() -> None:
    repo = PredictionRepository(_coleccion())
    with pytest.raises(NotFoundError):
        repo.get_by_id(__import__("bson").ObjectId())


def test_correccion_no_modifica_created_at() -> None:
    repo = PredictionRepository(_coleccion())
    prediccion = repo.create(
        Prediction(fruit_name="Uva", confidence=70, image_name="u.png")
    )
    original = prediccion.created_at
    corregida = repo.update_fruit_name(prediccion.id, "Banana 1")
    assert corregida.fruit_name == "Banana 1"
    assert corregida.created_at.replace(tzinfo=None, microsecond=0) == original.replace(
        tzinfo=None, microsecond=0
    )
    almacenada = repo.get_by_id(prediccion.id)
    assert almacenada.created_at.replace(microsecond=0) == original.replace(
        tzinfo=None, microsecond=0
    )


def test_filtros_combinables() -> None:
    repo = PredictionRepository(_coleccion())
    ahora = datetime.now(timezone.utc)
    repo.create(Prediction(fruit_name="Banana 1", confidence=80, image_name="a.png", created_at=ahora))
    repo.create(Prediction(fruit_name="Manzana", confidence=90, image_name="b.png", created_at=ahora + timedelta(days=1)))

    solo_banana = repo.list_sorted(fruit="Banana 1")
    assert [p.fruit_name for p in solo_banana] == ["Banana 1"]

    rango = repo.list_sorted(date_from=ahora + timedelta(hours=12))
    assert [p.fruit_name for p in rango] == ["Manzana"]

    combinado = repo.list_sorted(fruit="Manzana", date_from=ahora)
    assert [p.fruit_name for p in combinado] == ["Manzana"]

    vacio = repo.list_sorted(fruit="Piña")
    assert vacio == []


def test_borrado_requiere_confirmacion() -> None:
    repo = PredictionRepository(_coleccion())
    prediccion = repo.create(Prediction(fruit_name="Kiwi", confidence=40, image_name="k.png"))
    with pytest.raises(TypeError):
        repo.delete(prediccion.id)
    repo.delete(prediccion.id, confirmar=True)
    with pytest.raises(NotFoundError):
        repo.get_by_id(prediccion.id)
