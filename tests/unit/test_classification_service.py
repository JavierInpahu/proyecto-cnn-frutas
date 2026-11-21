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


def test_clasificacion_guarda_miniatura_y_metadatos(imagen_png_valida) -> None:
    """La imagen subida se reduce a miniatura y se describen sus metadatos."""

    class _Archivo:
        name = "foto.png"
        type = "image/png"

        def __init__(self, contenido) -> None:
            self.contenido = contenido

        def getvalue(self):
            return self.contenido

    registros = []

    class _Servicio:
        def register(self, **datos) -> None:
            registros.append(datos)

    servicio = ClassificationService(
        model_loader=_CargadorFalso(),
        image_processor=_ProcesadorFalso(np.zeros((1, 100, 100, 3), dtype=np.float32)),
        prediction_service=_Servicio(),
    )
    resultado = servicio.classify(_Archivo(imagen_png_valida), "foto.png", persist=True)

    import base64

    assert resultado.saved is True
    assert registros[0]["thumbnail"]
    assert base64.b64decode(registros[0]["image_data"]) == imagen_png_valida
    metadatos = registros[0]["image_meta"]
    assert metadatos["width"] == 40
    assert metadatos["height"] == 50
    assert metadatos["format"] == "PNG"
    assert metadatos["size_bytes"] == len(imagen_png_valida)
    assert metadatos["mime_type"] == "image/png"


def test_imagen_rechazada_no_se_guarda_ni_consulta_historial(monkeypatch) -> None:
    """Un rechazo no se persiste y la clasificación nunca lee imágenes guardadas."""
    from backend.services import classification_service as modulo
    from ml.predictor import PredictionOutcome

    class _Historial:
        def __init__(self) -> None:
            self.registros = 0

        def register(self, *args, **kwargs) -> None:
            self.registros += 1

        def list_sorted(self):
            raise AssertionError("La clasificación no debe leer el historial.")

    historial = _Historial()

    def _prediccion_rechazada(*args, **kwargs):
        return PredictionOutcome(
            top_index=-1,
            fruit_name="No reconocido",
            confidence=0.0,
            probabilities=[],
            class_names=["Apple Golden 1", "Banana 1", "Orange 1", "Grape Blue 1", "Pineapple 1"],
            rejected=True,
            reason="La imagen no se parece a ninguna de las frutas entrenadas.",
        )

    monkeypatch.setattr(modulo, "predict_image", _prediccion_rechazada)
    servicio = ClassificationService(
        model_loader=_CargadorFalso(),
        image_processor=_ProcesadorFalso(np.zeros((1, 100, 100, 3), dtype=np.float32)),
        prediction_service=historial,
    )
    resultado = servicio.classify("imagen.jpg", "foto.png", persist=True)
    assert resultado.rejected is True
    assert resultado.saved is False
    assert historial.registros == 0


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
