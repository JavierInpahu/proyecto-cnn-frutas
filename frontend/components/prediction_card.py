"""Tarjeta de resultado de clasificación."""

from __future__ import annotations

import streamlit as st


def render_prediction_card(
    fruit_name: str, confidence: float, probabilities, class_names
) -> None:
    st.success(f"Fruta predicha: {fruit_name}")
    st.info(f"Confianza del modelo: {confidence:.2f}%")
    if confidence < 60:
        st.warning(
            "La confianza es baja. Prueba con una foto donde aparezca una sola "
            "fruta, completa, enfocada y bien iluminada."
        )
    st.subheader("Resultados por fruta")
    for nombre, valor in zip(class_names, probabilities):
        st.write(f"{nombre}: {float(valor) * 100:.2f}%")
        st.progress(float(valor))
