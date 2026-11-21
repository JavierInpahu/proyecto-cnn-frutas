"""Configuración única de entrenamiento y predicción.

Toda la pipeline usa estos valores: el modelo recibe píxeles RGB en el rango
0-255 y aplica ``Rescaling(1./255)`` **una sola vez**, dentro del grafo.
Ningún script debe dividir la imagen entre 255 antes de llamar al modelo.
"""

from __future__ import annotations

from pathlib import Path

IMAGE_SIZE = (100, 100)
CHANNELS = 3
BATCH_SIZE = 32
SEED = 42
VALIDATION_SPLIT = 0.20
DEFAULT_EPOCHS = 15
DEFAULT_CONFIDENCE_THRESHOLD = 0.60
MIN_CONFIDENCE_MARGIN = 0.05
DATA_DIR = Path("data/fruits-360-subset")
MODEL_PATH = Path("modelo_frutas.keras")
MANIFEST_PATH = Path("ml/class_manifest.json")
INDICES_PATH = Path("ml/class_indices.json")
PROTOTYPES_PATH = Path("ml/class_prototypes.json")
REPORTS_DIR = Path("reports")
# Protección OOD: el softmax por sí solo es sobreconfiado.
EMBEDDING_LAYER = "dense"
MIN_IMAGE_STD = 8.0
# El Test real tiene gradiente máximo 11.51; una foto ajena (perro) dio 18.70.
MAX_IMAGE_GRADIENT = 13.0
# Dominio del dataset: el 100 % de las 980 imágenes del Test tiene al menos un
# 15 % de píxeles con min(R,G,B) >= 240 (fondo claro). Fotos arbitrarias tienen 0 %.
WHITE_PIXEL_VALUE = 240
MIN_WHITE_BACKGROUND = 0.10
NORMALIZATION = "rescaling_1_over_255_inside_model"
INPUT_RANGE = (0, 255)
DATASET_SOURCE = "https://github.com/fruits-360/fruits-360-100x100"
