"""Componente de confirmación de borrado."""

from __future__ import annotations

import streamlit as st


def confirmar_borrado(clave: str, mensaje: str = "¿Confirmas la eliminación?") -> bool:
    """Devuelve True solo si el usuario confirma la acción."""
    if st.session_state.get(f"{clave}_confirmado", False):
        st.session_state[f"{clave}_confirmado"] = False
        return True
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sí, eliminar", key=f"{clave}_si", type="primary"):
            st.session_state[f"{clave}_confirmado"] = True
            st.rerun()
    with col2:
        if st.button("Cancelar", key=f"{clave}_no"):
            st.info("Operación cancelada.")
            return False
    return False
