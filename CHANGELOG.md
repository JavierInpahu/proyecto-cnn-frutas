# Registro de cambios

## [No versionado] - Evolución a monolito modular con Streamlit y MongoDB Atlas

### Añadido
- Arquitectura en capas con dependencias unidireccionales:
  `frontend` → `backend/services` → `backend/repositories` → `backend/database` → Atlas,
  y `backend/services` → `ml` → manifiesto/modelo.
- Manifiesto único de clases en `ml/class_manifest.json` con nombre, nombre científico
  y descripción de las cinco clases (`Apple Golden 1`, `Banana 1`, `Orange 1`,
  `Grape Blue 1`, `Pineapple 1`).
- Catálogo de frutas con CRUD, unicidad de nombre sin distinguir mayúsculas (índice
  único con collation `strength: 2`) y siembra idempotente desde el manifiesto.
- Historial de predicciones con registro, listado descendente, corrección de fruta
  sin alterar `created_at`, filtros combinables y eliminación con confirmación.
- Conexión a MongoDB Atlas (`DB_Frutas_Inpahu`) con clasificación de errores
  (configuración, autenticación, permisos, red) y protección de secretos.
- Comprobación de conexión ejecutable: `scripts/check_mongo_connection.py`.
- Interfaz Streamlit con cinco secciones: Inicio, Reconocimiento, Historial,
  Administración de frutas y Estadísticas.
- Persistencia de predicciones tolerante a fallos: el resultado se muestra aunque
  Atlas no responda.
- Pruebas unitarias con `mongomock` y dobles; pruebas de integración marcadas con
  `integration` sobre `DB_Frutas_Inpahu_test`; prueba de regresión contra `app.py`.
- Scripts corregidos en `scripts/`: `train.py`, `predict.py` y `check_mongo_connection.py`
  (los originales de la raíz se conservan intactos).
- Documentación: `docs/requisitos.md`, `docs/arquitectura.md`, `docs/base_datos.md`,
  `docs/conexion_mongodb.md`, `docs/pruebas.md` y este `CHANGELOG.md`.

### Cambiado
- `app.py` es ahora un entrypoint delgado que delega en `frontend/`; se conserva el
  archivo y el comando `python -m streamlit run app.py`.
- `requirements.txt` añade `pymongo`, `python-dotenv`, `pytest` y `mongomock`.
- `.gitignore` y `.gitattributes` amplían la protección de secretos, cachés y fin de línea.

### No cambiado (archivos protegidos)
- `modelo_frutas.keras`: no se reentrena, mueve ni reemplaza; entrada 100×100×3 con
  `Rescaling` incorporado, sin división entre 255.
- `Proyecto_Final_CNN_Clasificacion_Frutas.ipynb`: sin cambios.
- `train.py` y `predict.py` de la raíz: sin cambios.
- `README.md`: ampliado de forma incremental, contenido original conservado.

### Seguridad
- No se almacena ninguna credencial real; `.env.example` usa únicamente el marcador
  `REEMPLAZAR_POR_URI_DE_ATLAS`.
