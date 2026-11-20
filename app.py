import streamlit as st

from backend.config.settings import MongoConfigurationError, Settings
from backend.database.mongo_connection import MongoConnection
from backend.models.exceptions import ModelMismatchError, MongoConnectionError
from backend.repositories.fruit_repository import FruitRepository
from backend.repositories.prediction_repository import PredictionRepository
from backend.services.classification_service import ClassificationService
from backend.services.fruit_service import FruitService
from backend.services.prediction_service import PredictionService
from frontend import navigation
from frontend.views import administracion_frutas, estadisticas, historial, inicio, reconocimiento
from ml.image_processor import ImageProcessor
from ml.model_loader import ModelLoader


@st.cache_resource
def componer_servicios():
    """Compila capas y servicios; el modelo se carga una vez por sesión."""
    settings = Settings.from_env()
    connection = MongoConnection(settings)

    try:
        connection.ping()
        base_disponible = True
    except MongoConnectionError as exc:  # pragma: no cover - depende de la red
        base_disponible = False
        st.warning(f"Atlas no disponible: {exc}")

    cargador = ModelLoader(settings.model_path, settings.manifest_path)
    try:
        cargador.validate_compatibility()
    except ModelMismatchError as exc:
        st.error(str(exc))
        st.stop()

    procesador = ImageProcessor()
    nombres_clase = cargador.class_names()
    manifiesto = cargador.manifest()

    if base_disponible:
        repositorio_frutas = FruitRepository(
            connection.get_collection(settings.fruits_collection)
        )
        repositorio_predicciones = PredictionRepository(
            connection.get_collection(settings.predictions_collection)
        )
    else:  # pragma: no cover - sin red, las vistas informan el error al usarlo
        repositorio_frutas = None
        repositorio_predicciones = None

    servicio_frutas = FruitService(repositorio_frutas, manifiesto)
    servicio_predicciones = PredictionService(repositorio_predicciones)
    servicio_clasificacion = ClassificationService(
        cargador,
        procesador,
        nombres_clase,
        servicio_predicciones if base_disponible else None,
    )
    return (
        servicio_clasificacion,
        servicio_frutas,
        servicio_predicciones,
        nombres_clase,
    )


def main() -> None:
    st.set_page_config(
        page_title="Clasificador de Frutas con CNN", page_icon="🍎"
    )
    st.title("Clasificador de Frutas con CNN")

    try:
        (
            servicio_clasificacion,
            servicio_frutas,
            servicio_predicciones,
            nombres_clase,
        ) = componer_servicios()
    except MongoConfigurationError as exc:
        st.error(
            "Configuración inválida: revise el archivo .env. "
            "La URI debe ser la real de Atlas (no el marcador de ejemplo)."
        )
        st.stop()
    except Exception as exc:  # pragma: no cover - arranque de aplicación
        st.error(f"No se pudo iniciar la aplicación: {exc}")
        st.stop()

    seccion = navigation.render_navigation()

    if seccion == "inicio":
        inicio.render()
    elif seccion == "reconocimiento":
        reconocimiento.render(servicio_clasificacion, nombres_clase)
    elif seccion == "historial":
        historial.render(servicio_predicciones, nombres_clase)
    elif seccion == "administracion_frutas":
        administracion_frutas.render(servicio_frutas)
    elif seccion == "estadisticas":
        estadisticas.render(servicio_predicciones, nombres_clase)


if __name__ == "__main__":
    main()
