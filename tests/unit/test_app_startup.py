"""Comprobación de que la aplicación compone sus servicios sin Atlas."""

from __future__ import annotations


def test_app_se_compone_y_rutas_son_las_originales() -> None:
    import app
    from frontend.navigation import SECCIONES

    clasificacion, predicciones, clases, modo = app.componer_servicios()

    assert clasificacion is not None
    assert predicciones is not None
    assert clases == [
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1",
    ]
    assert modo == "local"
    assert list(SECCIONES) == ["inicio", "historial", "estadisticas"]
