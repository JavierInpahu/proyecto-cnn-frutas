"""Navegación entre las tres secciones de la aplicación."""

from __future__ import annotations

import streamlit as st

SECCIONES = {
    "inicio": "Inicio",
    "historial": "Historial",
    "estadisticas": "Estadísticas",
}


def render_navigation() -> str:
    """Devuelve la clave de la sección seleccionada por el usuario."""
    with st.sidebar:
        st.title("Menú")
        clave = st.radio(
            "Sección",
            options=list(SECCIONES.keys()),
            format_func=lambda clave: SECCIONES[clave],
            label_visibility="collapsed",
        )
    return clave