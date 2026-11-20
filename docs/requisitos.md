# Requisitos del sistema

Este documento resume los requisitos funcionales (RF) y no funcionales (RNF)
implementados en la evolución del clasificador de frutas. Los identificadores
corresponden a los specs de `openspec/changes/evolve-fruit-classifier-streamlit-mongodb/specs/`.

## Requisitos funcionales

| ID | Requisito | Destino |
| --- | --- | --- |
| RF-01 | Configuración desde variables de entorno | `backend/config/settings.py` |
| RF-02 | Conexión y verificación con Atlas | `backend/database/mongo_connection.py` |
| RF-03 | Clasificación de errores de conexión | `backend/models/exceptions.py` |
| RF-04 | Comprobación ejecutable de conexión | `scripts/check_mongo_connection.py` |
| RF-05 | Creación de frutas | `backend/models/fruit.py`, `backend/repositories/fruit_repository.py` |
| RF-06 | Unicidad de nombre (case-insensitive) | `backend/repositories/fruit_repository.py` |
| RF-07 | Listado de frutas | `backend/services/fruit_service.py` |
| RF-08 | Consulta de fruta por id | `backend/repositories/fruit_repository.py` |
| RF-09 | Actualización de frutas | `backend/services/fruit_service.py` |
| RF-10 | Activación y desactivación | `backend/services/fruit_service.py` |
| RF-11 | Eliminación con confirmación | `backend/repositories/fruit_repository.py` |
| RF-12 | Siembra desde el manifiesto | `backend/services/fruit_service.py` |
| RF-13 | Registro de predicciones | `backend/models/prediction.py` |
| RF-14 | Listado cronológico descendente | `backend/repositories/prediction_repository.py` |
| RF-15 | Consulta de predicción por id | `backend/repositories/prediction_repository.py` |
| RF-16 | Corrección de fruta predicha | `backend/repositories/prediction_repository.py` |
| RF-17 | Filtros combinables | `backend/services/prediction_service.py` |
| RF-18 | Eliminación de predicción con confirmación | `backend/repositories/prediction_repository.py` |
| RF-19 | Dependencias unidireccionales | Arquitectura en capas |
| RF-20 | Contratos POO con inyección de dependencias | Servicios y repositorios |
| RF-21 | Excepciones de dominio | `backend/models/exceptions.py` |
| RF-22 | Cinco secciones de la interfaz | `frontend/` |
| RF-23 | Reconocimiento de una imagen | `frontend/views/reconocimiento.py` |
| RF-24 | Advertencia por baja confianza | `frontend/views/reconocimiento.py` |
| RF-25 | Persistencia tolerante a fallos | `backend/services/classification_service.py` |
| RF-26 | Gestión del historial desde la interfaz | `frontend/views/historial.py` |
| RF-27 | Administración de frutas desde la interfaz | `frontend/views/administracion_frutas.py` |
| RF-28 | Estadísticas | `frontend/views/estadisticas.py` |
| RF-29 | Manifiesto único de clases | `ml/class_manifest.json` |
| RF-30 | Validación de compatibilidad del modelo | `ml/model_loader.py` |
| RF-31 | Equivalencia con `app.py` | Prueba de regresión (`tests/unit/test_regression_app.py`) |
| RF-32 | Ampliación controlada de clases | `ml/model_loader.py` |
| RF-33 | Validación de formato y tamaño | `ml/image_processor.py` |
| RF-34 | Conversión a RGB y redimensionado | `ml/image_processor.py` |
| RF-35 | Formato de entrada del modelo | `ml/image_processor.py` |
| RF-36 | Pruebas unitarias aisladas | `tests/unit` |
| RF-37 | Pruebas de integración separadas | `tests/integration` |
| RF-38 | Cobertura de pruebas exigida | `tests/` |
| RF-39 | README actualizado | `README.md` |
| RF-40 | Documentación técnica | `docs/` y `CHANGELOG.md` |
| RF-41 | Protección del repositorio | `.gitignore`, `.gitattributes` |

## Requisitos no funcionales

| ID | Requisito | Destino |
| --- | --- | --- |
| RNF-01 | Protección de secretos | `.env.example`, `.gitignore`, mensajes sin URI |
| RNF-02 | Representación acotada del catálogo (5 campos) | `backend/models/fruit.py` |
| RNF-03 | Persistencia sin imágenes (5 campos) | `backend/models/prediction.py` |
| RNF-04 | Configuración centralizada | `backend/config/settings.py` |
| RNF-05 | Conservación del artefacto del modelo | `ml/model_loader.py`, `MODEL_PATH` |
| RNF-06 | Sin secretos en pruebas | `tests/` |
| RNF-07 | Documentación en español | `docs/`, `README.md`, `CHANGELOG.md` |

## Reglas de funcionamiento del modelo

- El modelo `modelo_frutas.keras` **no se reentrena ni se mueve**; permanece en la raíz.
- La entrada del modelo es `(1, 100, 100, 3)`, `float32`, valores 0-255.
- **No se divide entre 255**: el modelo ya incluye una capa `Rescaling`.
- Las cinco clases y sus metadatos se definen exclusivamente en `ml/class_manifest.json`.
