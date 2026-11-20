"""Script corregido de entrenamiento (solo lectura y validación).

El modelo `modelo_frutas.keras` no se reentrena ni se modifica en este cambio.
Este script verifica la compatibilidad del modelo con el manifiesto de clases.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.class_manifest import load_manifest
from ml.model_loader import ModelLoader


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida el modelo contra el manifiesto.")
    parser.add_argument("--modelo", default="modelo_frutas.keras")
    parser.add_argument("--manifiesto", default="ml/class_manifest.json")
    args = parser.parse_args()

    try:
        clases = load_manifest(args.manifiesto)
        loader = ModelLoader(model_path=args.modelo, manifest_path=args.manifiesto)
        loader.validate_compatibility()
        print(f"Modelo compatible: {args.modelo} con {len(clases)} clases del manifiesto.")
        for indice, clase in enumerate(clases):
            print(f"  {indice}: {clase.name} ({clase.scientific_name})")
        return 0
    except Exception as exc:  # pragma: no cover - informe por consola del script
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
