"""Descarga únicamente las cinco clases necesarias de Fruits-360 (100x100).

Fuente: https://github.com/fruits-360/fruits-360-100x100 (CC BY-SA 4.0,
Mihai Oltean). No se descarga el dataset completo: solo las carpetas
Training y Test de Apple Golden 1, Banana 1, Orange 1, Grape Blue 1 y
Pineapple 1. Las imágenes se guardan en ``data/fruits-360-subset``.

Uso:
    python scripts/download_dataset.py
    python scripts/download_dataset.py --destino data/fruits-360-subset
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = "fruits-360/fruits-360-100x100"
RAMA = "main"
API = f"https://api.github.com/repos/{REPO}/contents"
CLASES = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1",
]
SUBSETS = ("Training", "Test")


def _get_json(url: str, intentos: int = 3) -> list:
    ultimo = None
    for intento in range(intentos):
        try:
            peticion = urllib.request.Request(
                url, headers={"User-Agent": "fruit-vision-dataset-setup"}
            )
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                return json.load(respuesta)
        except Exception as exc:  # reintentos ante fallos transitorios de red
            ultimo = exc
            time.sleep(1 + intento)
    raise RuntimeError(f"No se pudo consultar {url}: {ultimo}")


def _descargar(url: str, destino: Path, intentos: int = 3) -> None:
    if destino.exists() and destino.stat().st_size > 0:
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    ultimo = None
    for intento in range(intentos):
        try:
            peticion = urllib.request.Request(
                url, headers={"User-Agent": "fruit-vision-dataset-setup"}
            )
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                datos = respuesta.read()
            if not datos:
                raise RuntimeError("respuesta vacía")
            destino.write_bytes(datos)
            return
        except Exception as exc:
            ultimo = exc
            time.sleep(1 + intento)
    raise RuntimeError(f"No se pudo descargar {url}: {ultimo}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destino",
        default="data/fruits-360-subset",
        help="Directorio donde se guardan Training/ y Test/.",
    )
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    raiz = Path(args.destino)
    tareas = []
    for subset in SUBSETS:
        for clase in CLASES:
            ruta = f"{subset}/{urllib.parse.quote(clase)}"
            url = f"{API}/{ruta}?ref={RAMA}"
            entrada = _get_json(url)
            if not isinstance(entrada, list):
                raise RuntimeError(f"Respuesta inesperada para {clase}: {entrada}")
            pagina_num = 1
            while len(entrada) == 1000 * pagina_num:
                pagina_num += 1
                pagina = _get_json(f"{url}&page={pagina_num}")
                if not pagina:
                    break
                entrada.extend(pagina)
            imagenes = [e for e in entrada if e.get("type") == "file"]
            print(f"{subset}/{clase}: {len(imagenes)} imágenes")
            for imagen in imagenes:
                destino = raiz / subset / clase / imagen["name"]
                tareas.append((imagen["download_url"], destino))

    fallos = []
    with ThreadPoolExecutor(max_workers=args.workers) as ejecutor:
        futuros = [ejecutor.submit(_descargar, url, destino) for url, destino in tareas]
        completadas = 0
        for futuro in as_completed(futuros):
            try:
                futuro.result()
            except Exception as exc:
                fallos.append(str(exc))
            completadas += 1
            if completadas % 250 == 0:
                print(f"  descargadas {completadas}/{len(tareas)}")

    if fallos:
        print(f"Errores de descarga: {len(fallos)}", file=sys.stderr)
        for error in fallos[:5]:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"Dataset listo en {raiz.resolve()} ({len(tareas)} imágenes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
