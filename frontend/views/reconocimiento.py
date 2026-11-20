"""Vista de reconocimiento de una imagen."""

from __future__ import annotations

import streamlit as st

from frontend.components.image_uploader import render_image_uploader
from frontend.components.prediction_card import render_prediction_card


def render(classification_service, class_names) -> None:
    st.title("Reconocimiento de frutas")
    archivo = render_image_uploader()
    if archivo is None:
        return
    if st.button("Clasificar imagen", type="primary"):
        with st.spinner("Clasificando..."):
            try:
                resultado = classification_service.classify(
                    archivo, getattr(archivo, "name", "imagen"), persist=True
                )
            except Exception as exc:  # errores de imagen o modelo
                st.error(f"No se pudo procesar la imagen: {exc}")
                return
        render_prediction_card(
            resultado.fruit_name, resultado.confidence, resultado.probabilities, class_names
        )
        if not resultado.saved and resultado.warning:
            st.warning(resultado.warning)
        elif resultado.saved:
            st.caption("Predicción registrada en el historial.")
