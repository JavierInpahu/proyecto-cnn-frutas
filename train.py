```python
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

CLASES = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1",
]

TAMANO_IMAGEN = (100, 100)
TAMANO_LOTE = 32
SEMILLA = 42

RUTA_BASE = Path("fruits_dataset/fruits-360_100x100/fruits-360")

# Datos de entrenamiento
datos_entrenamiento = keras.utils.image_dataset_from_directory(
    RUTA_BASE / "Training",
    validation_split=0.20,
    subset="training",
    seed=SEMILLA,
    image_size=TAMANO_IMAGEN,
    batch_size=TAMANO_LOTE,
    label_mode="categorical",
    class_names=CLASES
)

# Datos de validación
datos_validacion = keras.utils.image_dataset_from_directory(
    RUTA_BASE / "Training",
    validation_split=0.20,
    subset="validation",
    seed=SEMILLA,
    image_size=TAMANO_IMAGEN,
    batch_size=TAMANO_LOTE,
    label_mode="categorical",
    class_names=CLASES
)

# Datos de prueba
datos_prueba = keras.utils.image_dataset_from_directory(
    RUTA_BASE / "Test",
    image_size=TAMANO_IMAGEN,
    batch_size=TAMANO_LOTE,
    label_mode="categorical",
    class_names=CLASES,
    shuffle=False
)

# Modelo CNN
modelo = keras.Sequential([
    layers.Input(shape=(100, 100, 3)),
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.05),
    layers.RandomZoom(0.1),
    layers.Rescaling(1./255),
    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(5, activation="softmax")
])

modelo.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Control del entrenamiento
parada = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

ajuste = keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss",
    patience=2,
    factor=0.5,
    min_lr=0.00001
)

# Entrenamiento
historial = modelo.fit(
    datos_entrenamiento,
    validation_data=datos_validacion,
    epochs=25,
    callbacks=[parada, ajuste]
)

# Evaluación con datos de prueba
perdida, precision = modelo.evaluate(datos_prueba)

print(f"Precisión en pruebas: {precision * 100:.2f}%")
print(f"Pérdida en pruebas: {perdida:.6f}")

# Guardar modelo
modelo.save("modelo_frutas.keras")

print("Modelo guardado correctamente.")
```

