"""Navegación principal de FRUIT VISION.

Se conservan únicamente las tres rutas originales en un solo menú lateral.
La opción activa se resalta en morado; no se duplican botones en el contenido.
"""

from __future__ import annotations

import streamlit as st

SECCIONES = {
    "inicio": "🏠  Inicio",
    "historial": "🕘  Historial",
    "estadisticas": "📊  Estadísticas",
}


def render_navigation(modo: str = "local", modelo_activo: bool = True, detalle: str = "") -> str:
    """Dibuja el menú lateral y devuelve la clave de la sección seleccionada."""
    if "fv_seccion" not in st.session_state:
        st.session_state.fv_seccion = "inicio"

    seleccion = st.session_state.fv_seccion

    with st.sidebar:
        st.markdown(
            """
            <div style="padding:8px 4px 18px 4px">
              <div style="font-size:1.6rem">🍍</div>
              <div style="font-size:1.25rem;font-weight:800;letter-spacing:.12em;color:#4C2A85">FRUIT VISION</div>
              <div style="opacity:.75;font-size:.78rem;color:#75669A">Clasificador inteligente de frutas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("MENÚ PRINCIPAL")
        for clave, etiqueta in SECCIONES.items():
            activo = seleccion == clave
            if st.button(
                ("▶ " if activo else "   ") + etiqueta,
                key=f"fv_nav_{clave}",
                type="primary" if activo else "secondary",
                use_container_width=True,
            ):
                st.session_state.fv_seccion = clave
                st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.caption("ESTADO DEL SISTEMA")
        estado_modelo = "activo" if modelo_activo else "en preparación"
        st.markdown(
            f"""
            <div style="background:#F7F3FF;border:1px solid #E4D8FA;
                        border-radius:14px;padding:12px;font-size:.85rem;color:#2D1B4E">
              <div>🧠 Modelo: {estado_modelo}</div>
              <div>💾 Historial: {"MongoDB Atlas" if modo == "atlas" else "local (JSON)"}</div>
              <div>🍎 Clases: 5 frutas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if detalle:
            st.caption(detalle[:100])
    return seleccion
