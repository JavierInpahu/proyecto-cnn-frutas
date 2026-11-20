# Propuesta: evolución del clasificador de frutas a monolito modular con Streamlit y MongoDB Atlas

## Why

El proyecto actual clasifica cinco frutas desde un único archivo `app.py`: cada predicción se muestra y se pierde, la lista de clases está triplicada, los scripts de entrenamiento y predicación no son ejecutables y no hay catálogo, historial, pruebas ni gestión de secretos. Esto impide mantener el sistema, auditar los resultados y responder preguntas básicas sobre las predicciones realizadas.

La evolución propuesta conserva **exactamente** el modelo entrenado y su comportamiento (misma clase y misma confianza), mientras incorpora una arquitectura en capas, persistencia en MongoDB Atlas, CRUD de frutas y de historial, y una interfaz Streamlit de cinco secciones.

## Hallazgos de la auditoría (solo lectura, 2026-11-19)

Evidencia Git obtenida:

| Comando | Resultado |
| --- | --- |
| `git status --porcelain=v1` | Sin salida; `git status` indica *«nothing to commit, working tree clean»* |
| `git remote -v` | `origin https://github.com/JavierInpahu/proyecto-cnn-frutas.git` (fetch y push) |
| `git branch --show-current` | `main` |
| `git log -5 --oneline` | `e544eea feat: openspec init`, `a1583c3 feat: gitignore create`, `6d401dd Update requirements.txt`, `5fd3734 Update README.md`, `de45adb Add files via upload` |

| Archivo | Función | Problema o hallazgo real |
| --- | --- | --- |
| `app.py` | Interfaz Streamlit y predicción | 63 líneas de un solo bloque. `CLASES` duplicada (líneas 6-12). No valida tipo ni tamaño de archivo. No persiste resultados. No contempla caída de base de datos. No usa `MODEL_PATH` configurable. |
| `train.py` | Entrenamiento | Empieza con `````python` (línea 1) y termina con ````` (línea 112): **no se puede ejecutar**. `CLASES` duplicada. `Dense(5, ...)` y `RUTA_BASE` fijos. Guarda sobre `modelo_frutas.keras`. |
| `predict.py` | Predicción por CLI | Misma cerca de Markdown (líneas 1 y 36): **no se puede ejecutar**. `CLASES` duplicada. Sin validación de imagen ni ruta. |
| `modelo_frutas.keras` | Modelo entrenado | Verificado desde el propio artefacto (ZIP Keras): capa de entrada `[None, 100, 100, 3]`, capa `Rescaling` presente, salida `Dense(5, softmax)`. Entra en rango **0-255**; **no dividir entre 255**. Clases en orden de salida: `Apple Golden 1`, `Banana 1`, `Orange 1`, `Grape Blue 1`, `Pineapple 1`. |
| `requirements.txt` | Dependencias | 8 paquetes sin fijar versión: `tensorflow`, `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, `pillow`, `streamlit`. Faltan `pymongo`, `python-dotenv`, `pytest`, `mongomock`. |
| `.gitignore` | exclusiones | Solo contiene `venv/`. No protege `.env`, `.env.*`, `kaggle.json`, `.kaggle/`, `.streamlit/secrets.toml`, `__pycache__/` ni `.pytest_cache/`. |
| `README.md` | Documentación | Describe solo la app actual. No documenta base de datos, conexión, arquitectura ni pruebas. Las instrucciones `python train.py` y `python predict.py` no funcionan por las cercas de Markdown. |
| `Proyecto_Final_CNN_Clasificacion_Frutas.ipynb` | Notebook de entrenamiento | Usa `kaggle.json`; celdas de Kaggle repetidas (`!pip install -q kaggle`, `!kaggle datasets download -d moltean/fruits` en varios puntos). Sus salidas contienen credenciales de Kaggle incrustadas en texto; **sus valores no se reproducen en estos artefactos**. Mismo orden de clases. |
| Estructura del repositorio | Organización | **No existen** `backend/`, `scripts/check_mongo_connection.py`, `tests/`, `docs/`, `.env.example`, `.gitattributes` ni `CHANGELOG.md`. No hay trabajo previo reutilizable en esas rutas; todo se propone como nuevo. Tampoco existen specs ni cambios OpenSpec previos. |
| Fin de línea | Historial Git | En esta auditoría el árbol está limpio, `core.autocrlf=true` y los archivos de texto están en CRLF en el árbol de trabajo; no hay `.gitattributes`. El aviso de «archivos modificados solo por CRLF/LF» **no se reproduce en este momento**, pero el riesgo de ruido en el diff permanece y se mitiga con `.gitattributes`. |

Hechos proporcionados por el solicitante que **sí se confirmaron**: cercas de Markdown en `train.py` y `predict.py`, `CLASES` duplicada, orden de las cinco clases, entrada 100×100×3 en 0-255 con `Rescaling`, `.gitignore` insuficiente, notebook con Kaggle repetido. Único hecho que no coincide: el estado «modificados por fin de línea», que hoy no aparece en `git status`.

## What Changes

- Reestructurar el proyecto como **monolito modular en capas** con dependencias unidireccionales: `frontend` → `backend/services` → `backend/repositories` → `backend/database` → Atlas, y `backend/services` → `ml` → `modelo_frutas.keras`. Las vistas de Streamlit no importarán `pymongo` ni `backend.database`.
- Centralizar las cinco clases en `ml/class_manifest.json`, con `name`, `scientific_name` y `description` por clase en el orden de salida del modelo. El entrenamiento, la predicción, el catálogo y la interfaz lo leerán de ahí; desde el manifiesto se sembrará Atlas y las descripciones se podrán ajustar después desde la interfaz sin tocar código. `ModelLoader` validará que el número de salidas coincida con el manifiesto y lanzará `ModelMismatchError` si no coincide.
- Añadir `Settings`, `MongoConnection` y configuración por variables de entorno con `.env.example` usando únicamente `REEMPLAZAR_POR_URI_DE_ATLAS`.
- Crear el modelo de dominio POO (`Fruit`, `Prediction`), repositorios y servicios con inyección de dependencias, y las excepciones de dominio solicitadas.
- Implementar CRUD de frutas (incluye activar/desactivar, duplicados por nombre ignorando mayúsculas y siembra desde el manifiesto) y CRUD de historial de predicciones (incluye corrección de `fruit_name` sin tocar `created_at`, filtros combinables por fruta y rango de fechas, y borrado con confirmación).
- Mantener el pipeline de imagen de `app.py`: JPG/JPEG/PNG ≤ 5 MB, RGB, 100×100, `float32`, forma `(1,100,100,3)`, **sin dividir entre 255**.
- Sustituir la pantalla única por cinco secciones Streamlit: Inicio, Reconocimiento, Historial, Administración de frutas y Estadísticas. Si Atlas falla, la predicción se muestra igual y se avisa que no se pudo guardar.
- Corregir los scripts en `scripts/train.py` y `scripts/predict.py` (sin cercas de Markdown, leyendo el manifiesto), dejando los originales intactos en la raíz.
- Añadir pruebas pytest (unitarias con dobles/`mongomock`; integración con `DB_Frutas_Inpahu_test` y marcador `integration`), incluida una prueba de regresión contra `app.py`.
- Crear el tag de Git `pre-refactor` antes de tocar `app.py` y capturar previamente una línea base de clase y confianza con imágenes de referencia, de modo que la versión heredada se recupere en un comando y la regresión se ejecute antes y después del refactor.
- Ampliar `.gitignore`, proponer `.gitattributes`, crear `docs/`, `CHANGELOG.md` y actualizar `README.md` de forma incremental.
- **BREAKING** para el despliegue: la aplicación pasa a requerir una URI de Atlas y variables de entorno; sin ellas, se degradará con avisos claros en lugar de fallar sin mensaje.

## Capabilities

### New Capabilities

- `mongodb-atlas-connection`: configuración, conexión, verificación y clasificación de errores de MongoDB Atlas.
- `fruit-catalog-crud`: ciclo de vida del catálogo de frutas, unicidad de nombre y siembra desde el manifiesto.
- `prediction-history-crud`: registro, consulta, corrección, filtrado y borrado del historial de predicciones.
- `python-poo-architecture`: capas, clases, contratos, inyección de dependencias y excepciones de dominio.
- `streamlit-frontend`: las cinco secciones de la interfaz y el manejo de fallos de persistencia.
- `cnn-fruit-classification`: carga del modelo, manifiesto de clases, validación de compatibilidad y equivalencia con `app.py`.
- `image-upload-processing`: validación y preprocesamiento de imágenes cargadas.
- `automated-testing`: estrategia pytest, dobles de prueba, marcador `integration` y cobertura exigida.
- `project-documentation`: documentación de requisitos, arquitectura, base de datos, conexión, pruebas y cambios.

### Modified Capabilities

- Ninguna. No existen specs previas en `openspec/specs/` (verificado con `openspec list --specs`).

## Impact

- **Archivos protegidos (no eliminar, renombrar, mover ni reemplazar de forma destructiva):** `modelo_frutas.keras`, `Proyecto_Final_CNN_Clasificacion_Frutas.ipynb`, `app.py`, `train.py`, `predict.py`, `README.md`. `app.py` se refactorizará como entrypoint delgado que delega en `frontend/`; `README.md` se ampliará de forma incremental. El modelo y el notebook no se tocarán; tampoco se reentrenará ni se sustituirá el modelo actual.
- **Archivos nuevos:** paquetes `frontend/`, `backend/`, `ml/`, `scripts/`, `tests/`, `docs/`; `ml/class_manifest.json`; `.env.example`; `.gitattributes`; `CHANGELOG.md`; specs de este cambio.
- **Archivos existentes modificados de forma controlada:** `app.py`, `requirements.txt`, `.gitignore`, `README.md`.
- **Dependencias nuevas previstas:** `pymongo`, `python-dotenv`, `pytest`, `mongomock` (y `streamlit` ya presente). Las versiones se fijarán en `requirements.txt` durante la implementación.
- **Sistemas externos:** MongoDB Atlas (base `DB_Frutas_Inpahu`, colecciones `fruits` y `predictions`; base de pruebas `DB_Frutas_Inpahu_test`). El solicitante confirmó que el cluster existe y hay acceso, así que no se aprovisiona nada; la URI se entrega fuera del repositorio. No se escriben credenciales reales en ningún artefacto.

## Riesgos

- **Deriva del modelo:** cualquier cambio en el preprocesamiento o en el orden de clases alteraría la confianza. Mitigación: prueba de regresión contra `app.py` y validación `ModelMismatchError`.
- **Seguridad de secretos:** el notebook contiene credenciales de Kaggle en salidas y `.gitignore` no las cubre. Mitigación: exclusiones nuevas y advertencia documentada sin reproducir valores.
- **Fallo de Atlas:** la experiencia de usuario no debe desaparecer si la base no responde. Mitigación: predicción visible + aviso, con `MongoConnectionError` y sus subtipos.
- **Cambios de fin de línea:** ruido en diffs y conflictos. Mitigación: `.gitattributes`.
- **Dos puntos de entrada desincronizados:** mantener `app.py` y un `streamlit_app.py` paralelo duplicaría lógica y clases. Mitigación: un único `app.py` delgado, tag `pre-refactor` y línea base de regresión antes del cambio.

## Fuera de alcance

- Reentrenar, reemplazar o mover `modelo_frutas.keras` ni el notebook; reconocer clases distintas a las cinco entrenadas.
- Mover el modelo a `models/` o el notebook a `notebooks/`: se deja para un cambio posterior y aparte, una vez que las pruebas de este cambio pasen.
- Limpiar o reescribir el notebook, descargar el dataset, aprovisionar Atlas ni escribir credenciales reales.
- Autenticación de usuarios, control de acceso, API HTTP, despliegue, migraciones automáticas de datos ni borrado de la base de producción.
- Cambios de commits, remotos o historial de Git.
