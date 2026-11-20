"""Creación centralizada de índices de las colecciones de Atlas."""

from __future__ import annotations

from pymongo import ASCENDING, DESCENDING

from backend.models.exceptions import MongoConnectionError


def create_indexes(fruits_collection, predictions_collection) -> None:
    """Crea los índices requeridos por el modelo de datos.

    - `fruits.name`: único, sin distinción de mayúsculas (collation strength 2).
    - `predictions.created_at`: descendente para el listado cronológico.
    """
    try:
        fruits_collection.create_index(
            [("name", ASCENDING)],
            unique=True,
            collation={"locale": "en", "strength": 2},
            name="ux_fruits_name_case_insensitive",
        )
        predictions_collection.create_index(
            [("created_at", DESCENDING)],
            name="ix_predictions_created_at_desc",
        )
    except Exception as exc:  # pragma: no cover - depende del driver de MongoDB
        raise MongoConnectionError(f"No se pudieron crear los índices: {exc}") from exc
