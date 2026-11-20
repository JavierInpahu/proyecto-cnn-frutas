"""Validación y preprocesamiento de imágenes para el clasificador de frutas.

La entrada entregada al modelo es idéntica a la de la aplicación original
`app.py`: RGB, 100×100, `float32`, forma `(1,100,100,3)`, valores 0-255
y sin división entre 255 (el modelo ya incluye `Rescaling`).
"""

from __future__ import annotations

import io
import os
from typing import Any, BinaryIO, Tuple
from uuid import uuid4

import numpy as np
from PIL import Image, UnidentifiedImageError

from backend.models.exceptions import InvalidImageError

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png"}
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB
TAMAVO_OBJETIVO: Tuple[int, int] = (100, 100)


class ImageProcessor:
    def __init__(
        self,
        extensiones_permitidas: set[str] | None = None,
        max_bytes: int = TAMANO_MAXIMO_BYTES,
        target_size: Tuple[int, int] = TAMAVO_OBJETIVO,
    ) -> None:
        self.extensiones_permitidas = extensiones_permitidas or EXTENSIONES_PERMITIDAS
        self.max_bytes = max_bytes
        self.target_size = target_size

    def _leer_bytes(self, archivo: Any) -> Tuple[bytes, str]:
        """Extrae los datos binarios y el nombre del archivo."""
        nombre = getattr(archivo, "name", "") or str(uuid4())
        if isinstance(archivo, os.PathLike):
            datos = archivo.read_bytes()
        elif hasattr(archivo, "getvalue"):
            datos = archivo.getvalue()
        elif isinstance(archivo, (bytes, bytearray)):
            datos = bytes(archivo)
        elif hasattr(archivo, "read"):
            datos = archivo.read()
        else:
            raise InvalidImageError("No se pudo leer el archivo de imagen.")
        if isinstance(datos, str):
            datos = datos.encode("utf-8")
        return datos, str(nombre)

    def validate(self, archivo: Any) -> None:
        """Valida extensión y tamaño; lanza InvalidImageError en caso contrario."""
        datos, nombre = self._leer_bytes(archivo)
        extension = os_path_splitext(nombre)[1].lower()
        if extension not in self.extensiones_permitidas:
            raise InvalidImageError(
                f"Formato no permitido: {extension or '(desconocido)'}. "
                f"Use {', '.join(sorted(self.extensiones_permitidas))}."
            )
        if len(datos) > self.max_bytes:
            raise InvalidImageError(
                f"La imagen excede los {self.max_bytes // (1024 * 1024)} MB permitidos."
            )

    def process(self, archivo: Any) -> np.ndarray:
        """Devuelve el arreglo `(1, 100, 100, 3)` en `float32`, escala 0-255.

        Pipeline idéntico a `app.py`:
        - `Image.open(...).convert("RGB")`
        - `.resize((100, 100))`
        - `np.asarray(..., dtype=np.float32)`
        - `np.expand_dims(..., axis=0)`
        - **Sin división entre 255** (el modelo incluye `Rescaling`)
        """
        datos, nombre = self._leer_bytes(archivo)
        try:
            imagen = Image.open(io.BytesIO(datos)).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("El archivo no es una imagen válida.") from exc
        imagen = imagen.resize(self.target_size)
        arreglo = np.asarray(imagen, dtype=np.float32)
        return np.expand_dims(arreglo, axis=0)

    def display_ready(self, archivo: Any) -> Image.Image:
        """Devuelve la imagen lista para vista previa en la interfaz."""
        datos, _ = self._leer_bytes(archivo)
        try:
            return Image.open(io.BytesIO(datos)).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("El archivo no es una imagen válida para vista previa.") from exc


def os_path_splitext(nombre: str) -> Tuple[str, str]:
    """Wrapper mínimo para evitar importar `os` solo por esta utilidad."""
    punto = nombre.rfind(".")
    if punto <= 0:
        return nombre, ""
    return nombre[:punto], nombre[punto:]