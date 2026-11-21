"""FRUIT VISION — punto de entrada de la interfaz Streamlit.

Arranque rápido: TensorFlow se importa y el modelo se carga únicamente cuando
el usuario analiza una imagen. El historial vive en MongoDB Atlas: la conexión
se abre de forma diferida en el primer acceso, no al abrir la aplicación.
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


class _RepositorioAtlasDiferido:
    """Repositorio de predicciones en Atlas que conecta solo en el primer uso.

    Reemplaza al historial local en JSON: tanto el guardado como la consulta
    pasan por ``PredictionRepository`` contra la colección configurada en
    ``.env``. Los errores de conexión se propagan a quien llama.
    """

    def __init__(self) -> None:
        self._conexion = None
        self._real = None

    @property
    def real(self):
        if self._real is None:
            from backend.config.settings import Settings
            from backend.database.mongo_connection import MongoConnection
            from backend.repositories.prediction_repository import PredictionRepository

            settings = Settings.from_env()
            self._conexion = MongoConnection(settings)
            self._real = PredictionRepository(
                self._conexion.get_collection(settings.predictions_collection)
            )
        return self._real

    def create(self, prediction):
        return self.real.create(prediction)

    def list_sorted(self, **filtros):
        return self.real.list_sorted(**filtros)

    def get_by_id(self, identificador):
        return self.real.get_by_id(identificador)

    def update_fruit_name(self, identificador, nuevo_nombre):
        return self.real.update_fruit_name(identificador, nuevo_nombre)

    def delete(self, identificador, confirmar=False):
        return self.real.delete(identificador, confirmar=confirmar)


@st.cache_resource(show_spinner="Preparando servicios…")
def componer_servicios():
    """Compila capas y servicios sin cargar el modelo ni conectarse a Atlas."""
    from backend.services.classification_service import ClassificationService
    from backend.services.prediction_service import PredictionService

    repositorio_predicciones = _RepositorioAtlasDiferido()
    servicio_predicciones = PredictionService(repositorio_predicciones)
    cargador = _CargadorDiferido()
    nombres_clase = cargador.class_names()

    servicios = (
        ClassificationService(
            cargador,
            ImageProcessor(),
            nombres_clase,
            servicio_predicciones,
        ),
        servicio_predicciones,
        nombres_clase,
        "atlas",
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
