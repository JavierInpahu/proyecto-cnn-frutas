
import tensorflow as tf
from tensorflow.keras.utils import image_dataset_from_directory
from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Rescaling,
    RandomFlip,
    RandomRotation,
    RandomZoom,
    RandomTranslation,
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Dropout
)

# Ruta del dataset
ruta_train = "fruits_dataset/fruits-360_100x100/fruits-360/Training"

# Dataset entrenamiento
train_ds = image_dataset_from_directory(
    ruta_train,
    validation_split=0.30,
    subset="training",
    seed=42,
    image_size=(100,100),
    batch_size=32,
    label_mode="categorical",
    class_names=[
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1"
    ]
)

# Dataset validación
val_ds = image_dataset_from_directory(
    ruta_train,
    validation_split=0.30,
    subset="validation",
    seed=42,
    image_size=(100,100),
    batch_size=32,
    label_mode="categorical",
    class_names=[
        "Apple Golden 1",
        "Banana 1",
        "Orange 1",
        "Grape Blue 1",
        "Pineapple 1"
    ]
)

# Data augmentation
data_augmentation = Sequential([
    RandomFlip("horizontal"),
    RandomRotation(0.1),
    RandomZoom(0.1),
    RandomTranslation(0.1,0.1)
])

# Modelo CNN
modelo = Sequential([

    data_augmentation,

    Rescaling(1./255),

    Conv2D(32,(3,3),activation="relu"),
    MaxPooling2D(2,2),

    Conv2D(64,(3,3),activation="relu"),
    MaxPooling2D(2,2),

    Conv2D(128,(3,3),activation="relu"),
    MaxPooling2D(2,2),

    Flatten(),

    Dense(128,activation="relu"),

    Dropout(0.3),

    Dense(5,activation="softmax")
])

# Compilar
modelo.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Entrenar
historial = modelo.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

# Guardar modelo
modelo.save("modelo_frutas.keras")

print("Entrenamiento finalizado")
