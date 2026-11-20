"""Pruebas de integración de historial contra DB_Frutas_Inpahu_test.

Requieren `MONGODB_URI` configurada fuera del repositorio; sin ella se omiten.
Nunca almacenan binarios de imagen.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId

from backend.models.prediction import Prediction
from backend.repositories.prediction_repository import PredictionRepository


URI = os.environ.get("MONGODB_URI")

pytestmark = pytest.mark.integration


@pytest.fixture
def coleccion_predicciones():
    if not URI:
        pytest.skip("Se requiere MONGODB_URI para pruebas de integración")
    from pymongo import MongoClient

    cliente = MongoClient(URI, serverSelectionTimeoutMS=8000)
    base = cliente["DB_Frutas_Inpahu_test"]
    coleccion = base["predictions"]
    yield coleccion
    cliente.drop_database("DB_Frutas_Inpahu_test")
    cliente.close()


def test_registro_y_consulta_sin_imagenes(coleccion_predicciones) -> None:
    repo = PredictionRepository(coleccion_predicciones)
    ahora = datetime.now(timezone.utc)
    prediccion = repo.create(
        Prediction(fruit_name="Banana 1", confidence=82.5, image_name="foto.png", created_at=ahora)
    )
    assert prediccion.id is not None

    almacenada = repo.get_by_id(prediccion.id)
    assert almacenada.fruit_name == "Banana 1"
    assert almacenada.confidence == 82.5
    assert almacenada.image_name == "foto.png"
    assert set(almacenada.to_document().keys()) <= {
        "_id",
        "fruit_name",
        "confidence",
        "image_name",
        "created_at",
    }

    lista = repo.list_sorted()
    assert len(lista) == 1
    assert lista[0].id == prediccion.id

    corregida = repo.update_fruit_name(prediccion.id, "Manzana")
    assert corregida.fruit_name == "Manzana"
    assert corregida.created_at == ahora

    repo.delete(prediccion.id, confirmar=True)
    with pytest.raises(__import__("backend.models.exceptions", fromlist=["NotFoundError"]).NotFoundError):
        repo.get_by_id(prediccion.id)
