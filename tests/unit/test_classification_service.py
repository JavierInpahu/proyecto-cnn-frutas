"""Pruebas unitarias de ClassificationService con dobles (sin red)."""

from __future__ import annotations

import numpy as np
import pytest

from backend.services.classification_service import ClassificationService, ClassificationResult


class _ModeloFalso:
    def predict(self, entrada, verbose=0):
        arreglo = np.zeros((1, 5), dtype=np.float32)
        arreglo[0, 2] = 1.0
        return arreglo


class _CargadorFalso:
    def __init__(self) -> None:
        self.model = _ModeloFalso()

    def get_model(self):
        return self.model

    def validate_compatibility(self):
        return None

    def class_names(self):
        return ["Apple Golden 1", "Banana 1", "Orange 1", "Grape Blue 1", "Pineapple 1"]


class _ProcesadorFalso:
    def __init__(self, entrada):
        self.entrada = entrada

    def process(self, archivo):
        return self.entrada


class _ServicioPrediccionFalso:
    def __init__(self) -> None:
        self.registros = []

    def register(self, fruit_name, confidence, image_name):
        self.registros.append((fruit_name, confidence, image_name))


def test_clasificacion_devuelve_resultado_esperado() -> None:
    entrada = np.zeros((1, 100, 100, 3), dtype=np.float32)
    servicio = ClassificationService(
        model_loader=_CargadorFalso(),
        image_processor=_ProcesadorFalso(entrada),
    )
    resultado = servicio.classify("imagen.jpg", "foto.png", persist=False)
    assert resultado.fruit_name == "Orange 1"
    assert abs(resultado.confidence - 100.0) < 1e-6
    assert resultado.probabilities[2] == 1.0
    assert resultado.saved is False


def test_fallo_de_atlas_no_oculta_la_prediccion() -> None:
    entrada = np.zeros((1, 100, 100, 3), dtype=np.float32)
    servicio_prediccion = _ServicioPrediccionFalso()
    servicio_prediccion.register = lambda *a, **k: (_ for _ in ()).throw(
        __import__("backend.models.exceptions", fromlist=["MongoConnectionError"]).MongoConnectionError("red")
    )
    servicio = ClassificationService(
        model_loader=_CargadorFalso(),
        image_processor=_ProcesadorFalso(entrada),
        prediction_service=servicio_prediccion,
    )
    resultado = servicio.classify("imagen.jpg", "foto.png", persist=True)
    assert resultado.fruit_name == "Orange 1"
    assert resultado.saved is False
    assert resultado.warning is not None
    assert "No se pudo guardar" in resultado.warning
