"""Componente de carga y vista previa de imágenes."""

from __future__ import annotations

import streamlit as st


def render_image_uploader():
    """Muestra el cargador de archivo y devuelve el archivo o None."""
    archivo = st.file_uploader(
        "Selecciona una imagen de manzana, banano, naranja, uva o piña.",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )
    if archivo is not None:
        st.image(archivo, caption="Imagen cargada", use_container_width=True)
    return archivo
