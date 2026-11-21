"""Página principal: carga de imagen y análisis."""

from __future__ import annotations

import streamlit as st

from frontend.components.image_uploader import render_image_uploader
from frontend.components.prediction_card import render_prediction_card
from frontend.theme import section_title


def render(
    servicio_clasificacion,
    nombres_clase,
    modelo_activo: bool = True,
    detalle_modelo: str = "",
) -> None:
    section_title("Bienvenida")
    st.markdown(
        '<div class="fv-card fv-intro">'
        "Sube una fotografía y descubre qué fruta es en segundos con el modelo CNN entrenado."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    section_title("Analizar una fruta")

    modelo_listo = modelo_activo
    archivo = render_image_uploader(
        disabled=not modelo_listo,
        alerta="" if modelo_listo else (detalle_modelo or "El modelo aún está terminando de entrenarse."),
    )
    if archivo is None:
        return

    if st.button(
        "🔍 Analizar fruta",
        type="primary",
        disabled=not modelo_listo,
        use_container_width=True,
    ):
        with st.spinner("Cargando red neuronal y analizando la imagen…"):
            try:
                resultado = servicio_clasificacion.classify(
                    archivo, getattr(archivo, "name", "imagen"), persist=True
                )
            except Exception as exc:  # errores de imagen o modelo
                st.error(f"No se pudo procesar la imagen: {exc}")
                return
        render_prediction_card(
            resultado.fruit_name,
            resultado.confidence,
            resultado.probabilities,
            nombres_clase,
            rejected=resultado.rejected,
            reason=resultado.reason,
            image=archivo,
            saved=resultado.saved,
        )
        if resultado.warning and not resultado.rejected:
            st.warning(resultado.warning)
