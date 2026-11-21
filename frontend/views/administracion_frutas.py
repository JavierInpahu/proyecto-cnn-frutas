"""Administración del catálogo de frutas (CRUD conservado, presentación mejorada)."""

from __future__ import annotations

import streamlit as st

from frontend.components.confirm_dialog import confirmar_borrado
from frontend.theme import section_title


def render(fruit_service) -> None:
    section_title("Catálogo de frutas")
    with st.container():
        st.markdown('<div class="fv-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(
                '<div class="fv-kicker">Siembra</div>'
                '<div style="font-weight:650;color:var(--fv-deep)">Cargar las cinco clases del manifiesto</div>'
                '<div class="fv-muted">No crea duplicados ni sobrescribe datos existentes.</div>',
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("Sembrar catálogo", type="primary", use_container_width=True):
                try:
                    creadas = fruit_service.seed_catalog()
                    st.success(f"{creadas} fruta(s) nueva(s).")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo sembrar: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    with st.expander("Registrar fruta nueva", expanded=False):
        with st.form("form_nueva_fruta"):
            nombre = st.text_input("Nombre")
            nombre_cientifico = st.text_input("Nombre científico")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Crear fruta"):
                try:
                    fruit_service.create(nombre, nombre_cientifico, descripcion)
                    st.success("Fruta creada.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo crear: {exc}")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    section_title("Frutas registradas")
    try:
        frutas = fruit_service.list()
    except Exception as exc:
        st.error(f"No se pudo consultar el catálogo: {exc}")
        return

    if not frutas:
        st.info("El catálogo está vacío. Usa la siembra del manifiesto.")
        return

    for fruta in frutas:
        with st.container():
            st.markdown('<div class="fv-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1.2])
            with col1:
                estado = "Activa" if fruta.active else "Inactiva"
                st.markdown(
                    f'<div class="fv-fruit-name">{fruta.name}</div>'
                    f'<div class="fv-muted">{fruta.scientific_name}</div>'
                    f'<div class="fv-muted">{fruta.description or "Sin descripción"}</div>'
                    f'<span class="fv-chip">{"●" if fruta.active else "○"} {estado}</span>',
                    unsafe_allow_html=True,
                )
            with col2:
                if fruta.active:
                    if st.button("Desactivar", key=f"desactivar_{fruta.id}"):
                        try:
                            fruit_service.deactivate(fruta.id)
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                else:
                    if st.button("Reactivar", key=f"reactivar_{fruta.id}"):
                        try:
                            fruit_service.activate(fruta.id)
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                with st.expander("Editar / eliminar", expanded=False):
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
                            st.error(str(exc))
                    if confirmar_borrado(f"borrar_fruta_{fruta.id}", "¿Eliminar esta fruta?"):
                        try:
                            fruit_service.delete(fruta.id, confirmar=True)
                            st.success("Eliminada.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
