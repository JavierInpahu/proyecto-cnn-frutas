"""Vista de inicio."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Clasificador de Frutas con CNN")
    st.write(
        "Sube una imagen para clasificarla entre las cinco clases entrenadas: "
        "Apple Golden 1, Banana 1, Orange 1, Grape Blue 1 y Pineapple 1."
    )
    st.info(
        "Utiliza el menú lateral para navegar a Reconocimiento, Historial, "
        "Administración de frutas o Estadísticas."
    )
