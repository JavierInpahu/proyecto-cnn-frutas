import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model

CLASES = [
    "Apple Golden 1",
    "Banana 1",
    "Orange 1",
    "Grape Blue 1",
    "Pineapple 1",
]

@st.cache_resource
def cargar_modelo():
    return load_model("modelo_frutas.keras")

st.title("Clasificador de Frutas con CNN")
st.write("Carga una imagen de manzana, banano, naranja, uva o piña.")

try:
    modelo = cargar_modelo()
except Exception as error:
    st.error(f"No se pudo cargar modelo_frutas.keras: {error}")
    st.stop()

archivo = st.file_uploader(
    "Selecciona una imagen",
    type=["jpg", "jpeg", "png"]
)

if archivo is not None:
    try:
        imagen_original = Image.open(archivo).convert("RGB")
        st.image(imagen_original, caption="Imagen cargada", use_container_width=True)

        imagen = imagen_original.resize((100, 100))
        arreglo = np.asarray(imagen, dtype=np.float32)

        # IMPORTANTE:
        # No dividir entre 255. El modelo ya contiene Rescaling(1./255).
        entrada = np.expand_dims(arreglo, axis=0)

        prediccion = modelo.predict(entrada, verbose=0)[0]
        indice = int(np.argmax(prediccion))
        confianza = float(prediccion[indice]) * 100

        st.success(f"Fruta predicha: {CLASES[indice]}")
        st.info(f"Confianza del modelo: {confianza:.2f}%")

        st.subheader("Resultados por fruta")
        for nombre, valor in zip(CLASES, prediccion):
            st.write(f"{nombre}: {valor * 100:.2f}%")
            st.progress(float(valor))

        if confianza < 60:
            st.warning(
                "La confianza es baja. Prueba con una foto donde aparezca "
                "una sola fruta, completa, enfocada y bien iluminada."
            )

    except Exception as error:
        st.error(f"No se pudo procesar la imagen: {error}")
