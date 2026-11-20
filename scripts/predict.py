"""Script corregido de predicción sobre un archivo de imagen local.

Usa el modelo `modelo_frutas.keras` sin reentrenarlo y lee las clases de
`ml/class_manifest.json`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.class_manifest import load_manifest
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader


def main() -> int:
    parser = argparse.ArgumentParser(description="Clasifica una imagen de fruta local.")
    parser.add_argument("imagen", help="Ruta de la imagen (JPG, JPEG o PNG).")
    parser.add_argument("--modelo", default="modelo_frutas.keras")
    parser.add_argument("--manifiesto", default="ml/class_manifest.json")
    args = parser.parse_args()

    try:
        ruta = Path(args.imagen)
        if not ruta.exists():
            print(f"Error: no se encontró la imagen {ruta}", file=sys.stderr)
            return 1
        loader = ModelLoader(model_path=args.modelo, manifest_path=args.manifiesto)
        loader.validate_compatibility()
        procesador = ImageProcessor()
        entrada = procesador.process(ruta.read_bytes())
        modelo = loader.get_model()
        prediccion = modelo.predict(entrada, verbose=0)[0]
        indice = int(prediccion.argmax())
        clases = load_manifest(args.manifiesto)
        nombre = clases[indice].name
        confianza = float(prediccion[indice]) * 100
        print(f"Fruta predicha: {nombre}")
        print(f"Confianza: {confianza:.2f}%")
        for clase, valor in zip(clases, prediccion):
            print(f"  {clase.name}: {float(valor) * 100:.2f}%")
        return 0
    except Exception as exc:  # pragma: no cover - informe por consola del script
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
