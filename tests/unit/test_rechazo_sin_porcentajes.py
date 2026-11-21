"""Un rechazo no debe exponer porcentajes: solo 'No reconocido'."""

from __future__ import annotations

from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


class _ModeloFalso:
    def predict(self, entrada, verbose=0):
        return np.array([[0.10, 0.10, 0.60, 0.10, 0.10]], dtype=np.float32)


class _CargadorFalso:
    manifest_path = "ml/class_manifest.json"

    def __init__(self) -> None:
        self.modelo = _ModeloFalso()

    def get_model(self):
        return self.modelo

    def validate_compatibility(self) -> None:
        return None

    def class_names(self):
        return ["Apple Golden 1", "Banana 1", "Orange 1", "Grape Blue 1", "Pineapple 1"]


class _ProcesadorFalso:
    def process(self, archivo):
        return np.zeros((1, 100, 100, 3), dtype=np.float32)


def test_resultado_rechazado_no_lleva_porcentajes() -> None:
    from ml.predictor import predict

    resultado = predict(
        _CargadorFalso(),
        _ProcesadorFalso(),
        b"imagen",
        threshold=0.90,
        indices_path=ROOT / "ml" / "class_indices.json",
    )
    assert resultado.rejected is True
    assert resultado.fruit_name == "No reconocido"
    assert resultado.confidence == 0.0
    assert resultado.probabilities == []
    assert "%" not in (resultado.reason or "")


class _Columna:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _StFalso:
    def __init__(self) -> None:
        self.markdowns: list[str] = []
        self.advertencias: list[str] = []
        self.graficas = 0

    def markdown(self, texto, *args, **kwargs) -> None:
        self.markdowns.append(texto)

    def columns(self, *args, **kwargs):
        return [_Columna(), _Columna()]

    def container(self, *args, **kwargs):
        return _Columna()

    def caption(self, *args, **kwargs) -> None:
        return None

    def image(self, *args, **kwargs) -> None:
        return None

    def warning(self, texto, *args, **kwargs) -> None:
        self.advertencias.append(texto)

    def bar_chart(self, *args, **kwargs) -> None:
        self.graficas += 1


def _renderizar(monkeypatch, rejected: bool):
    from frontend.components import prediction_card

    falso = _StFalso()
    monkeypatch.setattr(prediction_card, "st", falso)
    nombres = ["Apple Golden 1", "Banana 1", "Orange 1", "Grape Blue 1", "Pineapple 1"]
    prediction_card.render_prediction_card(
        "Pineapple 1",
        99.94,
        [0.0, 0.0, 0.0, 0.0, 1.0],
        nombres,
        rejected=rejected,
        reason="La imagen no se parece a ninguna de las frutas entrenadas.",
    )
    return falso


def test_ui_rechazada_solo_dice_no_reconocido(monkeypatch) -> None:
    falso = _renderizar(monkeypatch, rejected=True)
    texto = " ".join(falso.markdowns)
    assert "No reconocido" in texto
    assert "%" not in texto
    assert "Distribución de probabilidades" not in texto
    assert "Gráfica comparativa" not in texto
    assert falso.graficas == 0
    assert falso.advertencias == []


def test_ui_aceptada_si_muestra_confianza(monkeypatch) -> None:
    falso = _renderizar(monkeypatch, rejected=False)
    texto = " ".join(falso.markdowns)
    assert "Pineapple 1" in texto
    assert "99.9" in texto  # el "%" está en una etiqueta <span> separada
    assert "Confianza del modelo" in texto
    assert "100.0%" in texto
    assert falso.graficas == 1


def test_cli_rechazada_no_imprime_porcentajes(monkeypatch, capsys, tmp_path) -> None:
    from scripts import predict as modulo

    class _Resultado:
        rejected = True
        fruit_name = "No reconocido"
        confidence = 0.0
        probabilities = []
        class_names = ["Apple Golden 1", "Banana 1", "Orange 1", "Grape Blue 1", "Pineapple 1"]
        reason = "La imagen no se parece a ninguna de las frutas entrenadas."

    class _PredictorFalso:
        def __init__(self, *args, **kwargs) -> None:
            return None

        def predict(self, datos):
            return _Resultado()

    monkeypatch.setattr(modulo, "ModelLoader", lambda *a, **k: object())
    monkeypatch.setattr(modulo, "ImageProcessor", lambda *a, **k: object())
    monkeypatch.setattr(modulo, "FruitPredictor", _PredictorFalso)
    imagen = tmp_path / "ruido.png"
    imagen.write_bytes(b"datos")

    assert modulo.main([str(imagen)]) == 0
    salida = capsys.readouterr().out
    assert salida.strip() == "NO RECONOCIDO"
    assert "%" not in salida
