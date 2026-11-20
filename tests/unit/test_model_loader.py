"""Pruebas unitarias de ModelLoader (modelo real sin reentrenar)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.models.exceptions import ModelMismatchError
from ml.model_loader import ModelLoader


def test_modelo_real_compatible_con_manifiesto() -> None:
    loader = ModelLoader()
    loader.validate_compatibility()
    assert loader.class_names() == [
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1",
    ]


def test_salidas_diferentes_lanzan_model_mismatch_sin_tocar_el_modelo_real() -> None:
    loader = ModelLoader()
    modelo_falso = SimpleNamespace(output_shape=(None, 6))
    loader.get_model = lambda: modelo_falso  # type: ignore[method-assign]
    with pytest.raises(ModelMismatchError):
        loader.validate_compatibility()
