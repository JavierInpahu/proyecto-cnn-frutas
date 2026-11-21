"""FRUIT VISION — punto de entrada de la interfaz Streamlit.

Arranque rápido: TensorFlow se importa y el modelo se carga únicamente cuando
el usuario analiza una imagen. Las vistas de inicio, historial y estadísticas
no cargan el modelo ni consultan Atlas al abrir la aplicación.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from frontend import navigation
from frontend.theme import apply_theme, hero
from frontend.views import estadisticas, historial, inicio
from ml.class_manifest import load_manifest
from ml.image_processor import ImageProcessor

ARCHIVO_MODELO = Path("modelo_frutas.keras")
ARCHIVO_INDICES = Path("ml/class_indices.json")
MANIFIESTO = Path("ml/class_manifest.json")


def _estado_modelo() -> tuple[bool, str]:
    """Comprobación ligera: solo archivos, sin importar TensorFlow."""
    if not ARCHIVO_MODELO.exists():
        return False, "Falta modelo_frutas.keras. Ejecuta python scripts/train.py."
    if not ARCHIVO_INDICES.exists():
        return False, "El modelo se está entrenando; las clases aún no están listas."
    try:
        datos = json.loads(ARCHIVO_INDICES.read_text(encoding="utf-8"))
        esperadas = [clase.name for clase in load_manifest(MANIFIESTO)]
        if datos.get("classes") != esperadas:
            return False, "Las clases guardadas no coinciden con el manifiesto."
    except (OSError, ValueError) as exc:
        return False, f"No se pudo leer la configuración del modelo: {exc}"
    return True, ""


class _CargadorDiferido:
    """Proxy que delega en ModelLoader solo cuando se necesita el modelo."""

    manifest_path = str(MANIFIESTO)

    def __init__(self) -> None:
        self._real = None

    @property
    def real(self):
        if self._real is None:
            self._real = _cargador_real()
        return self._real

    def validate_compatibility(self):
        return self.real.validate_compatibility()

    def get_model(self):
        return self.real.get_model()

    def manifest(self):
        return load_manifest(MANIFIESTO)

    def class_names(self):
        return [clase.name for clase in self.manifest()]


@st.cache_resource(show_spinner="Cargando red neuronal…")
def _cargador_real():
    """Único punto donde se importa TensorFlow en la aplicación."""
    from ml.model_loader import ModelLoader

    return ModelLoader(str(ARCHIVO_MODELO), str(MANIFIESTO))


@st.cache_resource(show_spinner="Preparando servicios…")
def componer_servicios():
    """Compila capas y servicios sin cargar el modelo ni conectarse a Atlas."""
    from backend.repositories.local_fruit_repository import LocalFruitRepository
    from backend.repositories.local_prediction_repository import LocalPredictionRepository
    from backend.services.classification_service import ClassificationService
    from backend.services.prediction_service import PredictionService

    repositorio_predicciones = LocalPredictionRepository("data/history.json")
    repositorio_frutas = LocalFruitRepository("data/fruits.json")
    cargador = _CargadorDiferido()
    nombres_clase = cargador.class_names()

    servicios = (
        ClassificationService(
            cargador,
            ImageProcessor(),
            nombres_clase,
            PredictionService(repositorio_predicciones),
        ),
        PredictionService(repositorio_predicciones),
        nombres_clase,
        "local",
    )
    return servicios


def main() -> None:
    st.set_page_config(
        page_title="FRUIT VISION · Clasificador inteligente de frutas",
        page_icon="🍍",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    hero(
        "FRUIT VISION",
        "Clasificador inteligente de frutas con visión por computadora. "
        "Sube una fotografía y descubre qué fruta es en segundos.",
    )

    try:
        servicio_clasificacion, servicio_predicciones, nombres_clase, modo = componer_servicios()
    except Exception as exc:  # pragma: no cover - fallo inesperado de composición
        st.error(f"No se pudo iniciar la aplicación: {exc}")
        st.stop()

    modelo_activo, detalle = _estado_modelo()
    seccion = navigation.render_navigation(
        modo=modo, modelo_activo=modelo_activo, detalle=detalle
    )

    if seccion == "inicio":
        inicio.render(
            servicio_clasificacion,
            nombres_clase,
            modelo_activo=modelo_activo,
            detalle_modelo=detalle,
        )
    elif seccion == "historial":
        historial.render(servicio_predicciones, nombres_clase)
    elif seccion == "estadisticas":
        estadisticas.render(servicio_predicciones, nombres_clase)


if __name__ == "__main__":
    main()
