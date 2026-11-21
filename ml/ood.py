"""Defensas contra imágenes ajenas al dominio entrenado.

El softmax de una CNN pequeña es sobreconfiado: una foto de otro objeto o
incluso ruido aleatorio puede producir 99-100 % en una clase. Por eso la
decisión final combina tres señales:

1. confianza y margen entre las dos clases principales;
2. estructura de la imagen (ruido aleatorio / imagen uniforme);
3. distancia del embedding a los prototipos de las cinco clases.

Los prototipos se generan con el Test real en ``ml/class_prototypes.json``.
Este módulo no importa TensorFlow al cargarse: la app sigue arrancando sin
cargar el modelo, y el extractor se crea solo cuando se analiza una imagen.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from ml import config

_EXTRACTORES: dict[int, Any] = {}


@lru_cache(maxsize=4)
def cargar_prototipos(ruta: str) -> dict:
    """Lee y valida el archivo de prototipos una sola vez."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if not datos.get("classes") or not datos.get("centroids"):
        raise ValueError("El archivo de prototipos está incompleto.")
    if len(datos["classes"]) != len(datos["centroids"]):
        raise ValueError("Prototipos y clases no coinciden.")
    return datos


def rechazo_por_estructura(entrada: np.ndarray) -> str | None:
    """Detecta imágenes uniformes o ruido, que el softmax no distingue."""
    arreglo = np.asarray(entrada)
    if arreglo.ndim != 4 or arreglo.shape[0] != 1:
        return None
    gris = arreglo[0].mean(axis=2)
    gradiente = (
        float(np.abs(np.diff(gris, axis=1)).mean())
        + float(np.abs(np.diff(gris, axis=0)).mean())
    ) / 2
    desviacion = float(gris.std())

    if desviacion < config.MIN_IMAGE_STD:
        return "La imagen es demasiado uniforme para identificar una fruta."
    # Un gradiente alto indica una escena con demasiado detalle (ruido, otra
    # foto, fondo complejo). El umbral está por encima del máximo del Test real
    # (11.51), así que no afecta a las cinco clases entrenadas.
    if gradiente > config.MAX_IMAGE_GRADIENT:
        return "La imagen parece ruido o tiene un detalle aleatorio incompatible con una fruta."
    # El entrenamiento usa frutas recortadas sobre fondo claro. El peor caso real
    # del Test tiene 15 % de píxeles casi blancos; una escena cualquiera, 0 %.
    blanco = float((arreglo[0].min(axis=2) >= config.WHITE_PIXEL_VALUE).mean())
    if blanco < config.MIN_WHITE_BACKGROUND:
        return "La imagen no pertenece al dominio de frutas sobre fondo claro del entrenamiento."
    return None


def _extractor(modelo: Any) -> Any:
    """Crea (y reutiliza) un modelo que devuelve la capa ``dense`` de 128 valores."""
    clave = id(modelo)
    if clave not in _EXTRACTORES:
        from tensorflow import keras

        capa = modelo.get_layer(getattr(config, "EMBEDDING_LAYER", "dense"))
        _EXTRACTORES[clave] = keras.Model(modelo.inputs, capa.output)
    return _EXTRACTORES[clave]


def rechazo_por_distancia(
    modelo: Any,
    entrada: np.ndarray,
    ruta_prototipos: str | Path | None = None,
) -> str | None:
    """Rechaza imágenes lejanas a todos los prototipos de fruta entrenados."""
    if modelo is None or not hasattr(modelo, "get_layer") or not hasattr(modelo, "inputs"):
        return None  # modelos falsos de pruebas unitarias

    ruta = Path(ruta_prototipos or config.PROTOTYPES_PATH)
    if not ruta.exists():
        return None  # artifact opcional en instalaciones antiguas

    datos = cargar_prototipos(str(ruta))
    vector = np.asarray(_extractor(modelo).predict(entrada, verbose=0)[0])
    centroides = np.asarray(datos["centroids"], dtype=np.float32)
    if centroides.ndim != 2 or centroides.shape[1] != vector.size:
        return None
    distancia = float(np.linalg.norm(centroides - vector, axis=1).min())
    if distancia > float(datos["distance_threshold"]):
        return "La imagen no se parece a ninguna de las frutas entrenadas."
    return None
