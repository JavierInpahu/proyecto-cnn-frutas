"""Arquitectura CNN compartida por entrenamiento y carga.

La capa ``Rescaling`` es el único punto de normalización de todo el sistema.
La entrada del modelo son píxeles RGB 0-255, igual que los produce
``ml.image_processor.ImageProcessor``.
"""

from __future__ import annotations

from tensorflow import keras
from tensorflow.keras import layers

from ml import config


def build_model(num_classes: int = 5) -> keras.Model:
    """Devuelve una CNN compacta con aumentación y normalización internas."""
    aumentacion = keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            # fill_mode="reflect" rellena con el propio borde de la imagen,
            # coherente con el fondo claro de Fruits-360 y sin introducir
            # valores artificiales fuera del rango normalizado [0, 1].
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.10),
            layers.RandomTranslation(0.05, 0.05),
        ],
        name="data_augmentation",
    )

    entradas = keras.Input(shape=(*config.IMAGE_SIZE, config.CHANNELS))
    x = layers.Rescaling(1.0 / 255.0, name="normalizacion_unica")(entradas)
    x = aumentacion(x)

    x = layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(32, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(0.20)(x)

    x = layers.Conv2D(64, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(64, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(0.30)(x)

    x = layers.Conv2D(128, 3, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(0.30)(x)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.40)(x)
    salidas = layers.Dense(num_classes, activation="softmax", name="clase")(x)

    modelo = keras.Model(entradas, salidas, name="fruit_vision_cnn")
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return modelo
