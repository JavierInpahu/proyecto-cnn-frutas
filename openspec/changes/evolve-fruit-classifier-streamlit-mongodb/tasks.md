# Tasks

Estado inicial: **ninguna tarea aparece marcada como completada**. La auditoría de planificación ya está documentada en `proposal.md`, pero no existe código nuevo en el repositorio que se pueda marcar como «ya funciona». Los archivos protegidos (`modelo_frutas.keras`, el notebook, `app.py`, `train.py`, `predict.py`, `README.md`) se conservan.

## 1. Auditoría

- **Archivos afectados:** solo lectura de `app.py`, `train.py`, `predict.py`, `requirements.txt`, `.gitignore`, `README.md`, el notebook y `modelo_frutas.keras`; `proposal.md` como referencia.
- **Dependencias:** ninguna.
- **Criterio de aceptación:** el estado real del repositorio coincide con los hallazgos registrados y no se han modificado archivos protegidos.

- [x] 1.1 Repetir `git status`, `git remote -v`, `git branch --show-current` y `git log -5 --oneline`, y verificar que no aparecen cambios inesperados ni archivos modificados solo por fin de línea.
- [x] 1.2 Verificar el contrato del modelo leyendo `config.json` dentro de `modelo_frutas.keras`: entrada `[None,100,100,3]`, capa `Rescaling`, salida `Dense(5, softmax)`; comparar con `proposal.md`.
- [x] 1.3 Confirmar que no existen `backend/`, `scripts/`, `tests/`, `docs/`, `.env.example`, `.gitattributes` ni conexión previa a MongoDB que debamos reutilizar; verificar con listado de directorios.
- [x] 1.4 Confirmar que ningún artefacto del cambio contiene credenciales reales y que el notebook no se modifica; verificar con búsqueda de `REEMPLAZAR_POR_URI_DE_ATLAS` y con `git status --short`.
- [x] 1.5 Crear `git tag pre-refactor` antes de cualquier refactorización (sin commits ni cambios de historial) y verificar que existe con `git tag -l pre-refactor`.
- [x] 1.6 Capturar la línea base de regresión: ejecutar `app.py` heredado con un conjunto de imágenes de referencia y guardar clase y confianza; verificar que las salidas quedan registradas antes de tocar `app.py`.

## 2. Arquitectura y requisitos

- **Archivos afectados:** `design.md`, los nueve archivos de `specs/`, `openspec/config.yaml` (solo lectura).
- **Dependencias:** etapa 1.
- **Criterio de aceptación:** cada RF/RNF tiene un módulo responsable y las decisiones de diseño no contradicen los specs.

- [x] 2.1 Trazar los requisitos RF-01 a RF-41 y RNF-01 a RNF-07 hacia los módulos del árbol definitivo, y verificar que no quede requisito sin destino.
- [x] 2.2 Verificar que las decisiones ya confirmadas están registradas en `design.md`: único `app.py` delgado con tag y línea base, cluster Atlas existente, metadatos en el manifiesto y traslado de modelo/notebook diferido; no volver a preguntarlas.
- [x] 2.3 Verificar que el plan no reentrena, mueve ni sustituye `modelo_frutas.keras` y que `MODEL_PATH` sigue apuntando a la raíz.
- [x] 2.4 Ejecutar `openspec validate evolve-fruit-classifier-streamlit-mongodb --strict` y corregir cualquier aviso antes de tocar código.

## 3. Estructura de paquetes y manifiesto

- **Archivos afectados:** `frontend/`, `backend/`, `ml/` (con sus `__init__.py`), `ml/class_manifest.json`, `ml/class_manifest.py`, `backend/models/exceptions.py`.
- **Dependencias:** etapa 2.
- **Criterio de aceptación:** todos los paquetes importan sin errores y el manifiesto contiene las cinco clases en el orden exacto del modelo.

- [x] 3.1 Crear la estructura de paquetes del árbol definitivo y comprobar que `python -c "import frontend, backend, ml"` termina sin errores.
- [x] 3.2 Crear `ml/class_manifest.json` con `Apple Golden 1`, `Banana 1`, `Orange 1`, `Grape Blue 1`, `Pineapple 1` en ese orden, incluyendo `scientific_name` y `description` para cada una, y verificar que el orden coincide con la salida `Dense(5, softmax)` y con la lista actual de `app.py`.
- [x] 3.3 Implementar el lector de manifiesto que expone nombre, nombre científico y descripción, y verificar con una prueba unitaria que devuelve cinco clases, conserva el orden y no deja metadatos vacíos.
- [x] 3.4 Implementar `ValidationError`, `DuplicateFruitError`, `NotFoundError`, `InvalidImageError`, `ModelMismatchError`, `MongoConnectionError` y sus cuatro subtipos, y verificar la jerarquía con una prueba unitaria.
- [x] 3.5 Verificar con una búsqueda en el código que no queden listas `CLASES` duplicadas en módulos nuevos.

## 4. Conexión MongoDB

- **Archivos afectados:** `.env.example`, `.gitignore`, `.gitattributes`, `requirements.txt`, `backend/config/settings.py`, `backend/database/mongo_connection.py`, `backend/database/indexes.py`, `scripts/check_mongo_connection.py`, `tests/unit/test_settings.py`, `tests/unit/test_mongo_connection.py`, `docs/conexion_mongodb.md`.
- **Dependencias:** etapas 2 y 3.
- **Criterio de aceptación:** la verificación de conexión funciona con un entorno válido, falla con mensaje claro con el marcador sin reemplazar y nunca imprime la URI.

- [x] 4.1 Añadir `pymongo`, `python-dotenv`, `pytest` y `mongomock` a `requirements.txt` con versiones fijadas y verificar que `pip install -r requirements.txt` termina correctamente.
- [x] 4.2 Crear `.env.example` con las seis variables indicadas y solo `REEMPLAZAR_POR_URI_DE_ATLAS`; verificar con una prueba que un marcador sin reemplazar lanza `MongoConfigurationError`.
- [x] 4.3 Ampliar `.gitignore` y crear `.gitattributes` para normalizar el fin de línea; verificar con `git check-ignore` que `.env`, `kaggle.json`, `.streamlit/secrets.toml`, `__pycache__/` y `.pytest_cache/` quedan ignorados.
- [x] 4.4 Implementar `Settings` con validación y `MongoConnection` con `connect()`, `ping()`, `get_collection()` y `close()`, y verificar con pruebas unitarias los cuatro subtipos de `MongoConnectionError` sin abrir red.
- [x] 4.5 Crear los índices (único en `fruits.name` con collation sin distinción de mayúsculas y descendente en `predictions.created_at`) y verificar su definición con `mongomock` o contra la base de pruebas.
- [x] 4.6 Crear `scripts/check_mongo_connection.py` y documentar su uso en `docs/conexion_mongodb.md`; verificar que una URI inválida produce un mensaje sin secretos.
- [x] 4.7 Verificar el acceso al cluster Atlas existente con la URI entregada fuera del repositorio y confirmar que se pueden crear índices en `DB_Frutas_Inpahu` y operar en `DB_Frutas_Inpahu_test`.

## 5. CRUD de frutas

- **Archivos afectados:** `backend/models/fruit.py`, `backend/repositories/fruit_repository.py`, `backend/services/fruit_service.py`, `tests/unit/test_fruit_repository.py`, `tests/unit/test_fruit_service.py`, `tests/integration/test_fruit_crud_integration.py`, `docs/base_datos.md` (sección de frutas).
- **Dependencias:** etapa 4.
- **Criterio de aceptación:** se pueden crear, listar, consultar, actualizar, activar, desactivar y eliminar frutas; los duplicados por nombre se rechazan y la siembra es idempotente.

- [x] 5.1 Implementar `Fruit` con validación, `_id` ObjectId y `active=true` por defecto, y verificar con pruebas unitarias la conversión desde/hacia documento y los cinco campos exactos.
- [x] 5.2 Implementar `FruitRepository` sobre la colección inyectada, con índice único por collation y manejo de duplicados; verificar con `mongomock` que `banana 1` no se crea si existe `Banana 1`.
- [x] 5.3 Implementar `FruitService` con inyección de repositorio y manifiesto, incluida la siembra sin duplicados de nombre, científico y descripción; verificar con pruebas unitarias que la primera siembra copia los metadatos y que una segunda no crea documentos.
- [x] 5.4 Implementar borrado con confirmación, activación y desactivación, y verificar que el listado de activas excluye las desactivadas.
- [ ] 5.5 Crear las pruebas de integración marcadas con `integration` contra `DB_Frutas_Inpahu_test` y documentar `fruits` en `docs/base_datos.md`; verificar que las unitarias no abren red.

## 6. CRUD de predicciones

- **Archivos afectados:** `backend/models/prediction.py`, `backend/repositories/prediction_repository.py`, `backend/services/prediction_service.py`, `tests/unit/test_prediction_repository.py`, `tests/integration/test_prediction_crud_integration.py`, `docs/base_datos.md` (sección de predicciones).
- **Dependencias:** etapa 4; la etapa 5 solo si se quiere validar nombres contra el catálogo (no obligatorio).
- **Criterio de aceptación:** el historial se ordena por fecha descendente, se puede corregir la fruta sin alterar `created_at`, admite filtros combinables y nunca guarda imágenes.

- [x] 6.1 Implementar `Prediction` con `confidence` entre 0 y 100, `created_at` UTC y `image_name` como sola cadena, y verificar con pruebas unitarias los rangos y la estructura de cinco campos.
- [x] 6.2 Implementar `PredictionRepository` con registro, listado descendente, consulta por id, corrección de `fruit_name` y borrado, y verificar con `mongomock` que `created_at` no cambia al corregir.
- [x] 6.3 Implementar `PredictionService` con filtros combinables por fruta y rango de fechas; verificar con pruebas unitarias el filtro conjunto y el caso sin resultados.
- [x] 6.4 Verificar el borrado con confirmación y el índice descendente de `created_at`, y completar `docs/base_datos.md` con la estructura de `predictions`.
- [ ] 6.5 Crear las pruebas de integración marcadas con `integration` contra `DB_Frutas_Inpahu_test` y verificar que no almacenan binarios de imagen.

## 7. Integración CNN

- **Archivos afectados:** `ml/image_processor.py`, `ml/model_loader.py`, `backend/services/classification_service.py`, `scripts/train.py`, `scripts/predict.py`, `tests/unit/test_image_processor.py`, `tests/unit/test_model_loader.py`, `tests/unit/test_classification_service.py`, `tests/unit/test_regression_app.py`, `docs/requisitos.md`, `docs/arquitectura.md`.
- **Dependencias:** etapa 1 (tag y línea base de regresión), etapas 3 y 4; etapa 6 para el guardado opcional del resultado.
- **Criterio de aceptación:** la nueva clasificación devuelve la misma clase y confianza que `app.py`, y el modelo original permanece intacto.

- [x] 7.1 Implementar `ImageProcessor` con validación JPG/JPEG/PNG de hasta 5 MB, RGB, 100×100, `float32`, forma `(1,100,100,3)` y sin división entre 255; verificar con pruebas unitarias los formatos rechazados y la forma del arreglo.
- [x] 7.2 Implementar `ModelLoader` con caché, lectura de `MODEL_PATH` y validación de salidas contra el manifiesto; verificar con una prueba que un modelo de seis salidas lanza `ModelMismatchError` (sin reentrenar ni reemplazar el modelo real).
- [x] 7.3 Implementar `ClassificationService` con inyección de colaboradores, resultado con `saved`/`warning` y captura de `MongoConnectionError`; verificar con dobles que un fallo de Atlas conserva la predicción.
- [x] 7.4 Crear `scripts/train.py` y `scripts/predict.py` sin cercas de Markdown y leyendo el manifiesto; verificar que `python scripts/predict.py --help` (o la ruta definida) no produce error de sintaxis y que los originales siguen sin cambios.
- [x] 7.5 Escribir la prueba de regresión con las imágenes de referencia de la etapa 1 y verificar primero que reproduce la línea base de `app.py` heredado y después que coincide exactamente con la arquitectura evolucionada.
- [x] 7.6 Documentar requisitos y flujo ML en `docs/requisitos.md` y `docs/arquitectura.md`, y verificar que no se menciona normalización manual entre 255.

## 8. Interfaz Streamlit

- **Archivos afectados:** `app.py`, `frontend/navigation.py`, `frontend/components/`, `frontend/views/`, `README.md` (sección de ejecución).
- **Dependencias:** etapa 1 (tag y línea base capturada antes del refactor), etapas 5, 6 y 7.
- **Criterio de aceptación:** las cinco secciones son accesibles, el reconocimiento funciona y un fallo de Atlas no oculta la predicción.

- [x] 8.1 Comprobar que el tag `pre-refactor` y la línea base de la etapa 1 existen; solo entonces refactorizar `app.py` como único entrypoint delgado que delega en `frontend/`, sin borrarlo ni renombrarlo, y verificar que `python -m streamlit run app.py` inicia sin errores de importación.
- [x] 8.2 Implementar la navegación y las cinco vistas, y verificar manualmente que Inicio, Reconocimiento, Historial, Administración de frutas y Estadísticas están disponibles.
- [x] 8.3 Implementar el componente de carga con validación, vista previa, fruta, confianza y probabilidades; verificar que una confianza inferior al 60 % muestra la advertencia.
- [x] 8.4 Implementar guardado tolerante a fallos y verificar con un doble que falla que la predicción se muestra igual y aparece el aviso correspondiente.
- [x] 8.5 Implementar las vistas de historial y administración con filtros, corrección y borrado confirmado; verificar que una cancelación no elimina el registro.
- [x] 8.6 Implementar estadísticas de total, conteo por fruta y confianza promedio, y verificar que con cero predicciones se muestran valores vacíos o en cero sin excepciones.

## 9. Pruebas

- **Archivos afectados:** `pytest.ini`, `tests/conftest.py`, todas las carpetas de pruebas, comprobación de secretos.
- **Dependencias:** etapas 4 a 8.
- **Criterio de aceptación:** la suite unitaria pasa sin Atlas, la de integración usa solo `DB_Frutas_Inpahu_test` y se ejecuta con el marcador `integration`.

- [x] 9.1 Crear `pytest.ini` con el registro del marcador `integration` y exclusión por defecto, y verificar que `pytest -m "not integration"` no intenta conectarse a Atlas.
- [x] 9.2 Crear `tests/conftest.py` con dobles, `mongomock` y datos de imagen de referencia, y verificar que todas las pruebas unitarias usan esas fixtures.
- [x] 9.3 Ejecutar la suite unitaria completa y verificar que pasa sin variables de entorno reales ni red.
- [ ] 9.4 Ejecutar las pruebas de integración contra `DB_Frutas_Inpahu_test` y verificar que nunca escriben en `DB_Frutas_Inpahu`.
- [x] 9.5 Verificar la cobertura exigida: conexión, CRUD de frutas, registro y consulta de predicciones, imágenes, carga del modelo, clasificación y regresión contra `app.py`.
- [x] 9.6 Buscar credenciales reales en todos los archivos del cambio y verificar que solo aparece `REEMPLAZAR_POR_URI_DE_ATLAS`.

## 10. Documentación

- **Archivos afectados:** `README.md`, `docs/requisitos.md`, `docs/arquitectura.md`, `docs/base_datos.md`, `docs/conexion_mongodb.md`, `docs/pruebas.md`, `CHANGELOG.md`.
- **Dependencias:** etapas 1 a 9.
- **Criterio de aceptación:** la documentación permite instalar, configurar, ejecutar, probar y revertir el sistema sin conocimiento implícito.

- [x] 10.1 Actualizar `README.md` de forma incremental con arquitectura, variables de entorno, comando de ejecución y advertencia sobre los scripts originales; verificar que los comandos funcionan tal como están escritos.
- [x] 10.2 Completar `docs/arquitectura.md` con el diagrama de capas y la tabla de clases, y verificar que las vistas no importan `pymongo` ni `backend.database`.
- [x] 10.3 Completar `docs/requisitos.md`, `docs/base_datos.md` y `docs/conexion_mongodb.md`, documentando que el manifiesto es la fuente de la siembra inicial y que las descripciones se ajustan en Atlas desde la interfaz; verificar que coinciden con los requisitos RF/RNF implementados.
- [x] 10.4 Crear `docs/pruebas.md` con los comandos unitarios y de integración, y verificar que ambos comandos se ejecutan correctamente.
- [x] 10.5 Crear `CHANGELOG.md` con la evolución a monolito modular, Atlas e historial, y verificar que no incluye credenciales ni datos sensibles.
- [x] 10.6 Revisar todos los artefactos y la documentación en español, verificar que el tag `pre-refactor` sigue disponible, confirmar con `git status --short` que no se hicieron commits ni se movió el modelo o el notebook, y comprobar que los archivos protegidos solo cambiaron de forma autorizada.

## Workflow follow-up

- Archivar el cambio OpenSpec una vez superada la revisión.
- Verificar el resultado archivado.
