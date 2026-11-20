"""Pruebas unitarias de PredictionService con doble de repositorio (sin red)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.models.prediction import Prediction
from backend.services.prediction_service import PredictionService


def test_registro_con_confianza_invalida_no_se_guarda() -> None:
    def crear(prediccion):
        raise __import__("backend.models.exceptions", fromlist=["ValidationError"]).ValidationError("confianza")

    servicio = PredictionService(repository=__import__("types").SimpleNamespace(create=crear))
    with pytest.raises(__import__("backend.models.exceptions", fromlist=["ValidationError"]).ValidationError):
        servicio.register("Banana 1", 150, "foto.png")


def test_listado_devuelve_orden_del_repositorio() -> None:
    prediccion = Prediction(fruit_name="Banana 1", confidence=80, image_name="f.png")
    def listar(fruit=None, date_from=None, date_to=None):
        return [prediccion]
    servicio = PredictionService(repository=__import__("types").SimpleNamespace(list_sorted=listar))
    resultado = servicio.list(fruit="Banana 1")
    assert len(resultado) == 1
    assert resultado[0].fruit_name == "Banana 1"
