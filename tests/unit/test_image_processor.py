"""Pruebas unitarias de ImageProcessor (sin red, sin modelo)."""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ml.image_processor import ImageProcessor


def test_imagen_png_valida_devuelve_arreglo_entrenamiento() -> None:
    procesador = ImageProcessor()
    arreglo = np.zeros((60, 80, 3), dtype=np.uint8)
    arreglo[:, :, 1] = 200
    imagen = Image.fromarray(arreglo)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    entrada = procesador.process(buffer.getvalue())
    assert entrada.shape == (1, 100, 100, 3)
    assert entrada.dtype == np.float32
    assert entrada.min() >= 0 and entrada.max() <= 255


def test_imagen_con_canal_alfa_se_convierte_a_rgb() -> None:
    procesador = ImageProcessor()
    arreglo = np.zeros((30, 30, 4), dtype=np.uint8)
    arreglo[:, :, 3] = 128
    imagen = Image.fromarray(arreglo, mode="RGBA")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    entrada = procesador.process(buffer.getvalue())
    assert entrada.shape == (1, 100, 100, 3)


def test_formato_gif_rechazado() -> None:
    procesador = ImageProcessor()
    datos = (
        b"GIF89a\x01\x00\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02D\x01\x00;"
    )
    with pytest.raises(__import__("ml.image_processor", fromlist=["InvalidImageError"]).InvalidImageError):
        procesador.validate(__import__("types").SimpleNamespace(name="anim.gif", getvalue=lambda: datos))


def test_texto_como_imagen_rechazado() -> None:
    procesador = ImageProcessor()
    with pytest.raises(__import__("ml.image_processor", fromlist=["InvalidImageError"]).InvalidImageError):
        procesador.validate(b"esto no es una imagen")


def test_imagen_muy_grande_rechazada() -> None:
    procesador = ImageProcessor(max_bytes=100)
    datos = b"x" * 1000
    with pytest.raises(__import__("ml.image_processor", fromlist=["InvalidImageError"]).InvalidImageError):
        procesador.validate(__import__("types").SimpleNamespace(name="grande.png", getvalue=lambda: datos))


def test_display_ready_devuelve_imagen_rgb() -> None:
    procesador = ImageProcessor()
    arreglo = np.full((40, 40, 3), 10, dtype=np.uint8)
    imagen = Image.fromarray(arreglo)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    previa = procesador.display_ready(buffer.getvalue())
    assert previa.mode == "RGB"
