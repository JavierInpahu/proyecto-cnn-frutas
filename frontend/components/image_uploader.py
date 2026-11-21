"""Componente de carga: zona amplia de arrastrar y soltar con vista previa."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_image_uploader(disabled: bool = False, alerta: str = ""):
    """Muestra la zona de carga. Si está deshabilitada, explica el motivo."""
    alerta_html = ""
    if alerta:
        alerta_html = (
            '<div class="fv-alert">'
            '<span class="fv-alert-icon" aria-hidden="true">⏳</span>'
            "<div>"
            "<strong>Modelo en entrenamiento</strong>"
            f'<div class="fv-muted">{escape(alerta)}</div>'
            "</div>"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="fv-card-soft" style="margin-bottom:14px">
          <div class="fv-kicker">Paso 1 · Imagen</div>
          <div style="font-size:1.05rem;font-weight:650;color:var(--fv-deep)">
            Arrastra y suelta una fotografía o selecciónala desde tu dispositivo
          </div>
          <div class="fv-muted">JPG, JPEG o PNG · máximo 5 MB · una sola fruta, bien enfocada</div>
          {alerta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    archivo = st.file_uploader(
        "Zona de carga",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        disabled=disabled,
        label_visibility="collapsed",
        help=(
            "El análisis estará disponible cuando termine el entrenamiento."
            if disabled
            else "Arrastra la imagen aquí o haz clic para examinar tus archivos."
        ),
    )
    if archivo is not None:
        st.markdown('<div class="fv-kicker" style="margin-top:16px">Vista previa</div>', unsafe_allow_html=True)
        with st.container():
            st.caption(getattr(archivo, "name", "imagen seleccionada"))
            st.image(archivo, use_container_width=True, caption=None)
    return archivo
