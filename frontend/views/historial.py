"""Historial de predicciones con tarjetas, filtros y mantenimiento."""

from __future__ import annotations

import base64
import io

import streamlit as st

from frontend.components.confirm_dialog import confirmar_borrado
from frontend.theme import section_title


def _miniatura(prediccion):
    dato = getattr(prediccion, "thumbnail", None)
    if not dato:
        return None
    try:
        return io.BytesIO(base64.b64decode(dato))
    except (ValueError, TypeError):
        return None


def render(prediction_service, class_names) -> None:
    section_title("Historial de predicciones")
    with st.expander("Filtros", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_fruta = st.selectbox("Fruta", options=["Todas"] + list(class_names), index=0)
        with col2:
            fecha_desde = st.date_input("Desde", value=None)
        with col3:
            fecha_hasta = st.date_input("Hasta", value=None)

    try:
        predicciones = prediction_service.list(
            fruit=None if filtro_fruta == "Todas" else filtro_fruta,
            date_from=fecha_desde,
            date_to=fecha_hasta,
        )
    except Exception as exc:
        st.error(f"No se pudo consultar el historial: {exc}")
        return

    st.caption(f"{len(predicciones)} predicción(es) registrada(s)")
    if not predicciones:
        st.info("Todavía no hay predicciones con estos filtros. Analiza una imagen para comenzar.")
        return

    for prediccion in predicciones:
        with st.container():
            st.markdown('<div class="fv-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 3])
            with col1:
                imagen = _miniatura(prediccion)
                if imagen is not None:
                    st.image(imagen, use_container_width=True)
                else:
                    st.markdown(
                        '<div class="fv-metric" style="font-size:2rem">🖼️</div>',
                        unsafe_allow_html=True,
                    )
            with col2:
                st.markdown(
                    f"""
                    <div class="fv-kicker">Predicción</div>
                    <div class="fv-fruit-name">{prediccion.fruit_name}</div>
                    <span class="fv-chip">{prediccion.confidence:.1f}% de confianza</span>
                    <div class="fv-muted fv-date">{prediccion.created_at}</div>
                    <div class="fv-muted">{prediccion.image_name}</div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Corregir o eliminar", expanded=False):
                    nuevo_nombre = st.text_input(
                        "Nombre de la fruta",
                        value=prediccion.fruit_name,
                        key=f"corregir_{prediccion.id}",
                    )
                    accion1, accion2 = st.columns(2)
                    with accion1:
                        if st.button("Guardar corrección", key=f"guardar_{prediccion.id}"):
                            try:
                                prediction_service.correct_fruit_name(prediccion.id, nuevo_nombre)
                                st.success("Corrección guardada.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"No se pudo corregir: {exc}")
                    with accion2:
                        if confirmar_borrado(f"borrar_{prediccion.id}", "¿Eliminar esta predicción?"):
                            try:
                                prediction_service.delete(prediccion.id, confirmar=True)
                                st.success("Predicción eliminada.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"No se pudo eliminar: {exc}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
