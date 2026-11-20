"""Vista de administración del catálogo de frutas."""

from __future__ import annotations

import streamlit as st

from frontend.components.confirm_dialog import confirmar_borrado


def render(fruit_service) -> None:
    st.title("Administración de frutas")

    st.subheader("Siembra del catálogo")
    st.caption(
        "Siembra las cinco clases del manifiesto si aún no existen. "
        "No crea duplicados ni sobrescribe nombres existentes."
    )
    if st.button("Sembrar catálogo desde el manifiesto", type="secondary"):
        try:
            creadas = fruit_service.seed_catalog()
            st.success(f"Siembra completada. Frutas nuevas: {creadas}.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo sembrar el catálogo: {exc}")

    st.divider()

    st.subheader("Registrar fruta nueva")
    with st.form("form_nueva_fruta"):
        nombre = st.text_input("Nombre")
        nombre_cientifico = st.text_input("Nombre científico")
        descripcion = st.text_area("Descripción")
        enviado = st.form_submit_button("Crear")
    if enviado:
        try:
            fruit_service.create(nombre, nombre_cientifico, descripcion)
            st.success("Fruta creada.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo crear la fruta: {exc}")

    st.divider()

    st.subheader("Catálogo")
    try:
        frutas = fruit_service.list()
    except Exception as exc:
        st.error(f"No se pudo consultar el catálogo: {exc}")
        return

    if not frutas:
        st.info("El catálogo está vacío. Ejecuta la siembra desde el manifiesto.")
        return

    for fruta in frutas:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                estado = "Activa" if fruta.active else "Inactiva"
                st.write(f"**{fruta.name}** ({estado})")
                st.caption(fruta.scientific_name)
                st.caption(fruta.description or "Sin descripción")
            with col2:
                if fruta.active:
                    if st.button("Desactivar", key=f"desactivar_{fruta.id}"):
                        try:
                            fruit_service.deactivate(fruta.id)
                            st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo desactivar: {exc}")
                else:
                    if st.button("Reactivar", key=f"reactivar_{fruta.id}"):
                        try:
                            fruit_service.activate(fruta.id)
                            st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo reactivar: {exc}")
            with col3:
                with st.expander("Editar", expanded=False):
                    nuevo_nombre = st.text_input("Nombre", value=fruta.name, key=f"edit_nombre_{fruta.id}")
                    nuevo_cientifico = st.text_input(
                        "Científico", value=fruta.scientific_name, key=f"edit_cientifico_{fruta.id}"
                    )
                    nueva_descripcion = st.text_input(
                        "Descripción", value=fruta.description, key=f"edit_desc_{fruta.id}"
                    )
                    if st.button("Guardar cambios", key=f"guardar_{fruta.id}"):
                        try:
                            fruit_service.update(
                                fruta.id,
                                name=nuevo_nombre or None,
                                scientific_name=nuevo_cientifico or None,
                                description=nueva_descripcion or None,
                            )
                            st.success("Actualizado.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"No se pudo actualizar: {exc}")
            with col4:
                if confirmar_borrado(f"borrar_fruta_{fruta.id}", "¿Eliminar esta fruta?"):
                    try:
                        fruit_service.delete(fruta.id, confirmar=True)
                        st.success("Eliminada.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"No se pudo eliminar: {exc}")
            st.divider()
