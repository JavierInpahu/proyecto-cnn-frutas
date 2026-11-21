"""Clasifica una imagen local con la pipeline compartida de FRUIT VISION."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml import config
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader
from ml.predictor import FruitPredictor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clasifica una imagen de fruta local.")
    parser.add_argument("imagen", help="Ruta de la imagen (JPG, JPEG o PNG).")
    parser.add_argument("--modelo", default=str(config.MODEL_PATH))
    parser.add_argument("--manifiesto", default=str(config.MANIFEST_PATH))
    parser.add_argument("--indices", default=str(config.INDICES_PATH))
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args(argv)

    try:
        ruta = Path(args.imagen)
        if not ruta.exists():
            print(f"Error: no se encontró la imagen {ruta}", file=sys.stderr)
            return 1
        cargador = ModelLoader(model_path=args.modelo, manifest_path=args.manifiesto)
        resultado = FruitPredictor(
            cargador,
            ImageProcessor(),
            indices_path=args.indices,
            threshold=args.threshold,
        ).predict(ruta.read_bytes())

        if resultado.rejected:
            # No hay coincidencia con ninguna clase: no se informa ningún porcentaje.
            print("NO RECONOCIDO")
            return 0
        print(f"Fruta predicha: {resultado.fruit_name}")
        print(f"Confianza: {resultado.confidence:.2f}%")
        for clase, valor in zip(resultado.class_names, resultado.probabilities):
            print(f"  {clase}: {valor * 100:.2f}%")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
