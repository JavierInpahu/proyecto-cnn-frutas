"""Estadísticas del historial con tarjetas y gráfico."""

from __future__ import annotations

from collections import Counter

import streamlit as st

from frontend.theme import section_title


def render(prediction_service, class_names) -> None:
    section_title("Estadísticas del historial")
    try:
        predicciones = prediction_service.list()
    except Exception as exc:
        st.error(f"No se pudo consultar el historial: {exc}")
        return

    total = len(predicciones)
    if total == 0:
        st.info("Aún no hay predicciones registradas.")
        return

    conteo = Counter(p.fruit_name for p in predicciones)
    promedio = sum(p.confidence for p in predicciones) / total
    fruta_frecuente, veces = conteo.most_common(1)[0]

    columnas = st.columns(3)
    metricas = [
        ("Total", str(total)),
        ("Confianza media", f"{promedio:.1f}%"),
        ("Más frecuente", f"{fruta_frecuente} ({veces})"),
    ]
    for columna, (etiqueta, valor) in zip(columnas, metricas):
        with columna:
            st.markdown(
                f'<div class="fv-card fv-metric"><span class="fv-kicker">{etiqueta}</span>'
                f"<strong>{valor}</strong></div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="fv-section-title">Conteo por fruta</div>', unsafe_allow_html=True)
    st.bar_chart(
        {nombre.replace(" 1", ""): conteo.get(nombre, 0) for nombre in class_names},
        use_container_width=True,
        height=260,
    )
