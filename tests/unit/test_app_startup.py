"""Comprobación de que la aplicación compone sus servicios contra Atlas."""

from __future__ import annotations


def test_app_se_compone_y_rutas_son_las_originales() -> None:
    import app
    from backend.repositories.local_prediction_repository import LocalPredictionRepository
    from frontend.navigation import SECCIONES

    app.componer_servicios.clear()
    clasificacion, predicciones, clases, modo = app.componer_servicios()

    assert clasificacion is not None
    assert predicciones is not None
    assert not isinstance(predicciones.repository, LocalPredictionRepository)
    assert clases == [
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1",
    ]
    assert modo == "atlas"
    assert list(SECCIONES) == ["inicio", "historial", "estadisticas"]


def test_historial_se_lee_de_mongo(monkeypatch) -> None:
    """La consulta del historial llega a la colección de Atlas, sin archivo JSON."""
    from unittest.mock import MagicMock

    import app
    from backend.config.settings import Settings
    from backend.database import mongo_connection

    settings = Settings.from_env({"MONGODB_URI": "mongodb://localhost:27017"})
    coleccion = MagicMock()
    coleccion.find.return_value.sort.return_value = []
    conexion = MagicMock()
    conexion.get_collection.return_value = coleccion

    monkeypatch.setattr(Settings, "from_env", classmethod(lambda cls, env=None: settings))
    monkeypatch.setattr(mongo_connection, "MongoConnection", lambda cfg: conexion)

    app.componer_servicios.clear()
    try:
        _, predicciones, _, modo = app.componer_servicios()
        assert modo == "atlas"
        conexion.get_collection.assert_not_called()

        assert predicciones.list() == []
        conexion.get_collection.assert_called_once_with("predictions")
        coleccion.find.assert_called_once_with({})
        coleccion.find.return_value.sort.assert_called_once_with("created_at", -1)
    finally:
        app.componer_servicios.clear()
