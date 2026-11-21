"""Prueba de regresión de la interfaz de clasificación.

Las imágenes de `legacy_baseline.json` son referencias ambiguas del modelo
anterior, que les asignaba una fruta con alta confianza. Tras el reentrenamiento
y la calibración OOD, esas mismas imágenes quedan lejos de los prototipos de las
cinco clases: la regresión verifica que se rechazan sin devolver fruta ni
porcentajes.
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


def test_regresion_rechaza_referencias_ambiguo_sin_porcentajes(
    servicio_clasificacion,
) -> None:
    if not BASELINE.exists():
        pytest.skip("Línea base no capturada (etapa 1.6)")
    linea_base = json.loads(BASELINE.read_text(encoding="utf-8"))
    for nombre_imagen in linea_base:
        resultado = servicio_clasificacion.classify(
            FIXTURES / nombre_imagen, nombre_imagen, persist=False
        )
        assert resultado.rejected is True, (
            f"{nombre_imagen}: la referencia ambigua debería rechazarse"
        )
        assert resultado.fruit_name == "No reconocido"
        assert resultado.confidence == 0.0
        assert resultado.probabilities == []
