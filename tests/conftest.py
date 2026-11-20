"""Fixtures compartidas: dobles, mongomock e imágenes de referencia (sin red)."""

from __future__ import annotations

import io
import os
from pathlib import Path

os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import numpy as np
import pytest
from PIL import Image

from ml.class_manifest import load_manifest

FIXTURES = Path("tests/fixtures")
MANIFIESTO = Path("ml/class_manifest.json")


@pytest.fixture(scope="session")
def clases_manifest():
    return load_manifest(MANIFIESTO)


@pytest.fixture
def imagen_png_valida():
    """Imagen PNG válida de referencia como bytes."""
    arreglo = np.zeros((50, 40, 3), dtype=np.uint8)
    arreglo[:, :, 0] = 120
    imagen = Image.fromarray(arreglo)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def archivo_gif():
    return (
        b"GIF89a\x01\x00\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02D\x01\x00;"
    )


@pytest.fixture
def conexion_mongomock():
    """Base de datos sobre mongomock para pruebas de repositorio sin red."""
    from mongomock import MongoClient as MockClient
    from backend.database.indexes import create_indexes

    cliente = MockClient()
    base = cliente["DB_Frutas_Inpahu_test"]
    create_indexes(base["fruits"], base["predictions"])
    yield base
    cliente.close()
