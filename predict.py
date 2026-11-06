
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

# Cargar modelo
modelo = load_model("modelo_frutas.keras")

# Clases
clases = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1"
]

# Ruta imagen
ruta_imagen = "imagen.jpg"

# Abrir imagen
imagen = Image.open(ruta_imagen)

# Redimensionar
imagen = imagen.resize((100, 100))

# Convertir a array
imagen = np.array(imagen)

# Normalizar
imagen = imagen / 255.0

# Agregar dimensión batch
imagen = np.expand_dims(imagen, axis=0)

# Predicción
prediccion = modelo.predict(imagen)

indice = np.argmax(prediccion)

fruta = clases[indice]

confianza = np.max(prediccion) * 100

print("Clase predicha:", fruta)
print("Confianza:", round(confianza, 2), "%")
