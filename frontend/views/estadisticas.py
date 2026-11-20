"""Vista de estadísticas del historial."""

from __future__ import annotations

from collections import Counter

import streamlit as st


def render(prediction_service, class_names) -> None:
    st.title("Estadísticas")

    try:
        predicciones = prediction_service.list()
    except Exception as exc:
        st.error(f"No se pudo consultar el historial: {exc}")
        return

    total = len(predicciones)
    st.metric("Total de predicciones", total)

    if total == 0:
        st.info("No hay datos suficientes para mostrar estadísticas.")
        return

    conteo = Counter(p.fruit_name for p in predicciones)
    promedio = sum(p.confidence for p in predicciones) / total

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Confianza promedio", f"{promedio:.2f}%")
    with col2:
        fruta_mas_frecuente, veces = conteo.most_common(1)[0]
        st.metric("Fruta más clasificada", f"{fruta_mas_frecuente} ({veces})")

    st.subheader("Conteo por fruta")
    for clase in class_names:
        st.write(f"{clase}: {conteo.get(clase, 0)}")
    st.bar_chart({clase: [conteo.get(clase, 0)] for clase in class_names})
