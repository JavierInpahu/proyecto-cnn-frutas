"""Tarjeta visual de resultados de clasificación.

Cuando la imagen se rechaza solo se muestra ``No reconocido``: no hay una
clase coincidente, por lo que no se presenta confianza, probabilidades ni
gráfica comparativa.
"""

from __future__ import annotations

import streamlit as st

ETIQUETAS = {
    "Apple Golden 1": "Manzana",
    "Banana 1": "Banano",
    "Orange 1": "Naranja",
    "Grape Blue 1": "Uva",
    "Pineapple 1": "Piña",
}


def _nombre_corto(nombre: str) -> str:
    return ETIQUETAS.get(nombre, nombre.replace(" 1", ""))


def render_prediction_card(
    fruit_name: str,
    confidence: float,
    probabilities,
    class_names,
    rejected: bool = False,
    reason: str | None = None,
    image=None,
    saved: bool | None = None,
) -> None:
    st.markdown('<div class="fv-section-title">Resultado del análisis</div>', unsafe_allow_html=True)

    columnas = st.columns([1, 1.25])
    with columnas[0]:
        if image is not None:
            st.markdown('<div class="fv-card">', unsafe_allow_html=True)
            st.caption("Imagen analizada")
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if rejected:
        with columnas[1]:
            st.markdown(
                '<div class="fv-card-soft">'
                '<div class="fv-fruit-name">No reconocido</div>'
                "</div>",
                unsafe_allow_html=True,
            )
        return

    with columnas[1]:
        st.markdown(
            '<div class="fv-card-soft">'
            '<div class="fv-kicker">Fruta identificada</div>'
            f'<div class="fv-fruit-name">{fruit_name}</div>'
            f'<div class="fv-muted">{_nombre_corto(fruit_name)} · modelo CNN entrenado</div>'
            '<div style="height:12px"></div>'
            f'<div class="fv-big-number">{confidence:.1f}<span style="font-size:1.4rem">%</span></div>'
            '<div class="fv-muted">Confianza del modelo</div>'
            '<div style="height:12px"></div>'
            + (
                '<span class="fv-chip">✓ Predicción registrada</span>'
                if saved is not False
                else '<span class="fv-chip fv-chip-warn">No se pudo guardar en el historial</span>'
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-section-title">Distribución de probabilidades</div>', unsafe_allow_html=True)
    with st.container():
        filas = []
        for nombre, valor in zip(class_names, probabilities):
            porcentaje = float(valor) * 100
            destacada = "fv-bar-top" if nombre == fruit_name else ""
            filas.append(
                f"""
                <div style="margin-bottom:12px">
                  <div class="fv-row" style="margin-bottom:5px">
                    <span style="font-weight:600">{_nombre_corto(nombre)}</span>
                    <span class="fv-muted">{porcentaje:.1f}%</span>
                  </div>
                  <div class="fv-bar {destacada}"><span style="width:{min(porcentaje, 100):.2f}%"></span></div>
                </div>
                """
            )
        st.markdown("".join(filas), unsafe_allow_html=True)

    st.markdown('<div class="fv-kicker" style="margin-top:18px">Gráfica comparativa</div>', unsafe_allow_html=True)
    st.bar_chart(
        {_nombre_corto(nombre): float(valor) for nombre, valor in zip(class_names, probabilities)},
        height=180,
        use_container_width=True,
    )
