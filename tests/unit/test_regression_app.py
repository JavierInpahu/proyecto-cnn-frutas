"""Prueba de regresión contra la aplicación original `app.py`.

Compara la arquitectura evolucionada con la línea base capturada en la etapa 1
(`tests/fixtures/legacy_baseline.json`) para las mismas imágenes de referencia.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.services.classification_service import ClassificationService
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader

BASELINE = Path("tests/fixtures/legacy_baseline.json")
FIXTURES = Path("tests/fixtures")


@pytest.fixture
def servicio_clasificacion():
    return ClassificationService(
        model_loader=ModelLoader(),
        image_processor=ImageProcessor(),
        prediction_service=None,
    )


def test_regresion_reproduce_linea_base_heredada(servicio_clasificacion) -> None:
    if not BASELINE.exists():
        pytest.skip("Línea base no capturada (etapa 1.6)")
    linea_base = json.loads(BASELINE.read_text(encoding="utf-8"))
    for nombre_imagen, esperado in linea_base.items():
        resultado = servicio_clasificacion.classify(
            FIXTURES / nombre_imagen, nombre_imagen, persist=False
        )
        assert resultado.fruit_name == esperado["class"], (
            f"{nombre_imagen}: se esperaba {esperado['class']} "
            f"y se obtuvo {resultado.fruit_name}"
        )
        assert abs(resultado.confidence - esperado["confidence"]) < 1e-4, (
            f"{nombre_imagen}: confianza esperada {esperado['confidence']} "
            f"y obtenida {resultado.confidence}"
        )
