"""Pruebas unitarias del manifiesto único de clases."""

from __future__ import annotations

from pathlib import Path

import pytest

from ml.class_manifest import (
    CLASES_ESPERADAS,
    ClaseEntrenada,
    ManifestError,
    class_names,
    load_manifest,
)

MANIFIESTO = Path("ml/class_manifest.json")


def test_manifiesto_devuelve_cinco_clases_en_orden_esperado() -> None:
    clases = load_manifest(MANIFIESTO)
    assert len(clases) == CLASES_ESPERADAS
    assert [c.name for c in clases] == [
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1",
    ]


def test_clases_tienen_metadatos_no_vacios() -> None:
    for clase in load_manifest(MANIFIESTO):
        assert isinstance(clase, ClaseEntrenada)
        assert clase.scientific_name
        assert clase.description


def test_class_names_devuelve_solo_nombres() -> None:
    assert class_names(MANIFIESTO) == [
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1",
    ]


def test_manifiesto_invalido_sin_metadatos_lanza_error() -> None:
    ruta = Path("tests/unit/fixtures/manifiesto_invalido.json")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(
        '[{"name": "Apple Golden 1", "scientific_name": "", "description": ""}]',
        encoding="utf-8",
    )
    with pytest.raises(ManifestError):
        load_manifest(ruta)
