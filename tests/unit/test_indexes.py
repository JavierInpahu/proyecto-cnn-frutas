"""Pruebas de definición de índices con mongomock (sin red).

mongomock no persiste la collation en list_indexes; por ello se verifica el
nombre, la unicidad y las claves del índice. La collation se valida contra el
cluster real en la tarea de integración.
"""

from __future__ import annotations

import mongomock

from backend.database.indexes import create_indexes


def test_indices_frutas_y_predicciones_definidos() -> None:
    cliente = mongomock.MongoClient()
    base = cliente["DB_Frutas_Inpahu_test"]
    frutas = base["fruits"]
    predicciones = base["predictions"]

    create_indexes(frutas, predicciones)

    indices_frutas = list(frutas.list_indexes())
    nombres_frutas = {indice["name"] for indice in indices_frutas}
    assert "ux_fruits_name_case_insensitive" in nombres_frutas
    unico = next(
        i for i in indices_frutas if i["name"] == "ux_fruits_name_case_insensitive"
    )
    assert unico["unique"] is True
    assert unico["key"] == {"name": 1}

    indices_predicciones = list(predicciones.list_indexes())
    nombres_predicciones = {indice["name"] for indice in indices_predicciones}
    assert "ix_predictions_created_at_desc" in nombres_predicciones
    fecha = next(
        i
        for i in indices_predicciones
        if i["name"] == "ix_predictions_created_at_desc"
    )
    assert fecha["key"] == {"created_at": -1}
