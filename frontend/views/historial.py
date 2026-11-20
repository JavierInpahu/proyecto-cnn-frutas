"""Vista de historial de predicciones."""

from __future__ import annotations

from datetime import date

import streamlit as st

from frontend.components.confirm_dialog import confirmar_borrado


def render(prediction_service, class_names) -> None:
    st.title("Historial de predicciones")

    with st.expander("Filtros", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_fruta = st.selectbox(
                "Fruta",
                options=["Todas"] + list(class_names),
                index=0,
            )
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

    if not predicciones:
        st.info("No hay predicciones registradas con los filtros seleccionados.")
        return

    for prediccion in predicciones:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{prediccion.fruit_name}** — {prediccion.confidence:.2f}%")
                st.caption(prediccion.image_name)
                st.caption(str(prediccion.created_at))
            with col2:
                nuevo_nombre = st.text_input(
                    "Corregir fruta",
                    value=prediccion.fruit_name,
                    key=f"corregir_{prediccion.id}",
                )
                if st.button("Guardar corrección", key=f"guardar_{prediccion.id}"):
                    try:
                        prediction_service.correct_fruit_name(prediccion.id, nuevo_nombre)
                        st.success("Corregido.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No se pudo corregir: {exc}")
            with col3:
                if confirmar_borrado(f"borrar_{prediccion.id}", "¿Eliminar esta predicción?"):
                    try:
                        prediction_service.delete(prediccion.id, confirmar=True)
                        st.success("Eliminada.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No se pudo eliminar: {exc}")
            st.divider()
