"""Compatibilidad: el análisis ya vive en la vista de Inicio."""

from __future__ import annotations

from frontend.views.inicio import render as render_inicio


def render(servicio_clasificacion, class_names, modelo_activo: bool = True, detalle_modelo: str = "") -> None:
    render_inicio(
        servicio_clasificacion,
        class_names,
        modelo_activo=modelo_activo,
        detalle_modelo=detalle_modelo,
    )
