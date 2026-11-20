"""Lectura y validación del manifiesto único de clases (fuente de verdad)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

CLASES_ESPERADAS = 5


@dataclass(frozen=True)
class ClaseEntrenada:
    name: str
    scientific_name: str
    description: str


class ManifestError(ValueError):
    """El manifiesto de clases no es válido."""


def load_manifest(path: str | Path = "ml/class_manifest.json") -> List[ClaseEntrenada]:
    """Carga el manifiesto y valida que las clases tengan metadatos completos."""
    archivo = Path(path)
    try:
        datos = json.loads(archivo.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"No se encontró el manifiesto en {archivo}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"El manifiesto no es JSON válido: {exc}") from exc

    if not isinstance(datos, list):
        raise ManifestError("El manifiesto debe ser una lista de clases.")

    clases: List[ClaseEntrenada] = []
    for indice, entrada in enumerate(datos):
        nombre = entrada.get("name", "").strip()
        nombre_cientifico = entrada.get("scientific_name", "").strip()
        descripcion = entrada.get("description", "").strip()
        if not nombre or not nombre_cientifico or not descripcion:
            raise ManifestError(
                f"La clase en la posición {indice} no tiene metadatos completos."
            )
        clases.append(
            ClaseEntrenada(
                name=nombre,
                scientific_name=nombre_cientifico,
                description=descripcion,
            )
        )

    if len(clases) != CLASES_ESPERADAS:
        raise ManifestError(
            f"Se esperaban {CLASES_ESPERADAS} clases y se encontraron {len(clases)}."
        )
    return clases


def class_names(path: str | Path = "ml/class_manifest.json") -> List[str]:
    """Devuelve solo los nombres de clase en el orden del manifiesto."""
    return [clase.name for clase in load_manifest(path)]
