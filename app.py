
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

modelo = load_model("modelo_frutas.keras")

clases = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1"
]

st.title("Clasificador de Frutas con CNN")

st.write(
    "Carga una imagen para obtener una predicción."
)

archivo = st.file_uploader(
    "Selecciona una imagen",
    type=["jpg", "jpeg", "png"]
)

if archivo is not None:

    imagen = Image.open(archivo)

    st.image(
        imagen,
        caption="Imagen cargada",
        use_container_width=True
    )

    imagen = imagen.resize((100, 100))

    imagen = np.array(imagen)

    imagen = imagen / 255.0

    imagen = np.expand_dims(
        imagen,
        axis=0
    )

    prediccion = modelo.predict(
        imagen,
        verbose=0
    )

    indice = np.argmax(prediccion)

    fruta = clases[indice]

    confianza = (
        np.max(prediccion) * 100
    )

    st.success(
        f"Fruta predicha: {fruta}"
    )

    st.info(
        f"Confianza: {confianza:.2f}%"
    )
