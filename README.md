# Clasificador de Frutas con Redes Neuronales Convolucionales (CNN)

Este proyecto evoluciona un clasificador de frutas con CNN hacia un monolito modular en Python/Streamlit/MongoDB Atlas, conservando el modelo entrenado y el comportamiento original.

## Descripción

El sistema clasifica imágenes de cinco frutas (manzana, banano, naranja, uva y piña) mediante una red neuronal convolucional. La predicción se muestra en una aplicación web construida con Streamlit. La evolución actual introduce:

- Arquitectura en capas con dependencias unidireccionales.
- Persistencia en MongoDB Atlas con modelo de datos de cinco campos.
- CRUD de frutas e historial de predicciones.
- Interfaz Streamlit con cinco secciones (Inicio, Reconocimiento, Historial, Administración de frutas y Estadísticas).
- Manifiesto único de clases (`ml/class_manifest.json`) como fuente de verdad.
- Pruebas automatizadas (unitarias sin red, de integración con Atlas).
- Sin reentrenamiento ni movimiento del modelo original.

## Frutas clasificadas

- **Apple Golden 1** (manzana) — `Malus domestica`
- **Banana 1** (banano) — `Musa acuminata`
- **Orange 1** (naranja) — `Citrus sinensis`
- **Grape Blue 1** (uva) — `Vitis vinifera`
- **Pineapple 1** (piña) — `Ananas comosus`

## Tecnologías utilizadas

- **Python 3.11+**
- **TensorFlow 2.21** y **Keras** — modelo entrenado `modelo_frutas.keras`
- **NumPy** — manipulación de arreglos
- **Pillow** — procesamiento de imágenes
- **Streamlit** — interfaz web interactiva
- **PyMongo** — controlador directo de MongoDB
- **python-dotenv** — lectura de variables de entorno
- **pytest** — suite de pruebas
- **mongomock** — dobles de pruebas para MongoDB sin red

## Estructura del proyecto

El proyecto está organizado en carpetas por responsabilidad:

```text
proyecto-cnn-frutas/
├── app.py                        # entrypoint delgado; delega en frontend/
├── modelo_frutas.keras           # PROTEGIDO: modelo entrenado, sin cambios
├── Proyecto_Final_CNN_Clasificacion_Frutas.ipynb  # PROTEGIDO: sin cambios
├── requirements.txt              # dependencias con versiones fijadas
├── .gitignore                    # archivos y carpetas ignorados por Git
├── .gitattributes                # normalización de fin de línea (LF)
├── pytest.ini                    # configuración de pytest (marcador integration)
├── openspec/                     # root OpenSpec existente
├── frontend/                     # vistas y componentes Streamlit (5 secciones)
│   ├── __init__.py
│   ├── navigation.py             # selección de las cinco secciones
│   ├── components/
│   │   ├── __init__.py
│   │   ├── image_uploader.py     # carga y validación de archivo
│   │   ├── prediction_card.py    # muestra fruta, confianza y probabilidades
│   │   └── confirm_dialog.py     # confirmación de borrado
│   └── views/
│       ├── __init__.py
│       ├── inicio.py             # página de bienvenida
│       ├── reconocimiento.py     # carga de imagen y clasificación
│       ├── historial.py          # listado, filtro, corrección y borrado
│       ├── administracion_frutas.py  # CRUD y siembra del catálogo
│       └── estadisticas.py       # total, conteo por fruta y confianza promedio
├── backend/                      # configuración, modelos, repositorios y servicios
│   ├── __init__.py
│   ├── config/                   # Settings, validación de entorno
│   │   └── settings.py
│   ├── database/                 # MongoConnection, índices
│   │   ├── __init__.py
│   │   ├── mongo_connection.py
│   │   └── indexes.py
│   ├── models/                   # excepciones y dominio (Fruit, Prediction)
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   ├── fruit.py
│   │   └── prediction.py
│   └── services/                 # FruitService, PredictionService, ClassificationService
│       ├── __init__.py
│       ├── fruit_service.py
│       ├── prediction_service.py
│       └── classification_service.py
├── ml/                           # manifiesto, procesado de imágenes, carga del modelo
│   ├── __init__.py
│   ├── class_manifest.json       # ÚNICA fuente: name, scientific_name, description
│   ├── class_manifest.py         # lectura y validación del manifiesto
│   ├── image_processor.py        # validación RGB, resize 100×100, float32, sin /255
│   └── model_loader.py           # caché del modelo, compatibilidad con manifiesto
├── scripts/                      # versiones corregidas de train.py/predict.py y check
│   ├── __init__.py
│   ├── check_mongo_connection.py # comprobación de conexión sin exponer URI
│   ├── train.py                  # versión corregida (solo lectura y validación)
│   └── predict.py                # versión corregida (predicción local por archivo)
├── tests/                        # pruebas automatizadas
│   ├── __init__.py
│   ├── conftest.py               # fixtures: manifest, imágenes, mongomock
│   ├── unit/                     # pruebas aisladas (sin red, mongomock)
│   │   ├── test_class_manifest.py
│   │   ├── test_settings.py
│   │   ├── test_mongo_connection.py
│   │   ├── test_indexes.py
│   │   ├── test_fruit_repository.py
│   │   ├── test_fruit_service.py
│   │   ├── test_prediction_repository.py
│   │   ├── test_prediction_service.py
│   │   ├── test_image_processor.py
│   │   ├── test_model_loader.py
│   │   └── test_classification_service.py
│   └── integration/              # pruebas con marcador `integration` (requiere MONGODB_URI)
│       ├── test_fruit_crud_integration.py
│       └── test_prediction_crud_integration.py
│   └── fixtures/
│       └── legacy_baseline.json  # línea base de regresión (clase y confianza de app.py)
├── docs/                         # documentación operativa
│   ├── requisitos.md
│   ├── arquitectura.md
│   ├── base_datos.md
│   ├── conexion_mongodb.md
│   ├── pruebas.md
│   └── CHANGELOG.md
├── .env.example                  # plantilla: solo REEMPLAZAR_POR_URI_DE_ATLAS
├── README.md                     # este documento (actualizado incremental)
└── CHANGELOG.md                  # registro de cambios del proyecto
```

## Instalación

Recomendado usar **Python 3.11** o una versión compatible con las dependencias instaladas.

### 1. Clonar el repositorio

```bash
git clone https://github.com/JavierInpahu/proyecto-cnn-frutas.git
cd proyecto-cnn-frutas
```

### 2. Instalar las dependencias

```bash
pip install -r requirements.txt
```

El `requirements.txt` incluye (versiones fijadas):

```
tensorflow==2.21.0
numpy==2.4.2
pandas==2.3.3
matplotlib==3.11.2
seaborn==0.13.2
scikit-learn==1.9.1
pillow==12.1.1
streamlit==1.54.0
pymongo==4.20.1
python-dotenv==1.2.4
pytest==9.1.1
mongomock==4.3.0
```

### 3. Configurar MongoDB Atlas

1. Copiar el archivo de plantilla:

   ```bash
   # Windows
   copy .env.example .env
   
   # Linux / macOS
   cp .env.example .env
   ```

2. Reemplazar únicamente el marcador `REEMPLAZAR_POR_URI_DE_ATLAS` con la URI real del cluster Atlas:

   ```dotenv
   MONGODB_URI=mongodb+srv://usuario:password@cluster0.mongodb.net
   MONGODB_DATABASE=DB_Frutas_Inpahu
   MONGODB_FRUITS_COLLECTION=fruits
   MONGODB_PREDICTIONS_COLLECTION=predictions
   MONGODB_TIMEOUT_MS=8000
   MODEL_PATH=modelo_frutas.keras
   ```

   **Importante**: El archivo `.env` se ignora con `.gitignore`; **nunca** lo subas al repositorio.

### 4. Verificar la conexión

```bash
python scripts/check_mongo_connection.py
```

Si la conexión es correcta, imprime un mensaje de éxito sin mostrar la URI. En caso de fallo, informa el subtipo de error (configuración, autenticación, permisos o red) sin incluir credenciales.

## Ejecutar la aplicación

Desde la carpeta del proyecto:

```bash
python -m streamlit run app.py
```

La aplicación se abrirá en el navegador en `http://localhost:8511` (o el puerto que indique Streamlit).

### Flujo de trabajo

1. Al abrir la app, el menú lateral permite elegir una de las cinco secciones.
2. **Inicio**: información general del sistema.
3. **Reconocimiento**: subir una imagen (JPG, JPEG o PNG, máximo 5 MB) y obtener la predicción de la fruta, la confianza y las cinco probabilidades. Si la confianza es inferior al 60 %, se muestra una advertencia.
4. **Historial**: consultar, filtrar (por fruta y rango de fechas), corregir el nombre de la fruta y eliminar predicciones (requiere confirmación).
5. **Administración de frutas**: siembra del catálogo desde el manifiesto, crear frutas nuevas, editar datos, activar/desactivar y borrar (con confirmación).
6. **Estadísticas**: total de predicciones, confianza promedio, conteo por fruta y gráfico de barras.

## Ejecutar una predicción sin la interfaz

También es posible clasificar una imagen desde la línea de comandos usando el script corregido:

```bash
python scripts/predict.py ruta/de/imagen.jpg
```

El script muestra la fruta predicha, la confianza y las probabilidades de cada clase. Requiere que `modelo_frutas.keras` y `ml/class_manifest.json` estén en la raíz.

## Entrenamiento

**No se reentrena el modelo** en este cambio. El archivo `modelo_frutas.keras` permanece en la raíz sin modificaciones.

El archivo `scripts/train.py` sirve únicamente para validar la compatibilidad del modelo con el manifiesto; no realiza entrenamiento nuevo.

Los archivos `train.py` y `predict.py` de la **raíz** contienen cercas de Markdown y no son ejecutables tal cual. Se conservan intactos por compatibilidad; las versiones corregidas están en `scripts/`.

## Pruebas automatizadas

```bash
# Pruebas unitarias (sin red, sin Atlas)
pytest -m "not integration"

# Pruebas de integración (requiere MONGODB_URI configurado en .env)
pytest -m integration
```

### ¿Qué cubren?

- **Suite unitaria** (45 tests): configuración, conexión con dobles y `mongomock`, CRUD de frutas, historial de predicciones, procesamiento de imágenes, carga del modelo, clasificación y regresión contra `app.py`. Nunca se conecta a Atlas ni usan credenciales reales.
- **Suite de integración** (marcador `integration`): opera exclusivamente sobre la base `DB_Frutas_Inpahu_test`. Requiere la `MONGODB_URI` configurada fuera del repositorio. Se verifica que no se escriba en `DB_Frutas_Inpahu` y que las predicciones almacenen solo nombre de archivo, nunca binarios.

### Escaneo de secretos

El cambio incluye una verificación (task 9.6) que busca credenciales reales en todos los archivos. El único valor que aparece es el marcador `REEMPLAZAR_POR_URI_DE_ATLAS` en `.env.example`.

## Reversión

Antes de refactorizar `app.py` se creó el tag `git tag pre-refactor`. Para recuperar la versión heredada del punto de entrada:

```bash
git checkout pre-refactor -- app.py
```

Esto restaura `app.py` desde el tag sin hacer commits ni reescribir historial. Los demás archivos modificados durante la evolución se pueden revertir con los comandos correspondientes del control de versiones.

## Referencias

- **Clúster Atlas**: confirmado por el solicitante; URI entregada fuera del repositorio.
- **Sin reentrenamiento**: el modelo `modelo_frutas.keras` se conserva tal cual; entrada 100×100×3, `Rescaling` incorporado, **no dividir entre 255**.
- **Manifiesto único**: `ml/class_manifest.json` define las cinco clases con nombre, nombre científico y descripción; es la única fuente para modelo, entrenamiento, predicción y siembra de Atlas.
- **Índice único case-insensitive**: `fruits.name` con collation `strength: 2` (sin campo auxiliar de normalización).

## Autor

Proyecto académico de Ingeniería de Software. Evolución OpenSpec: `evolve-fruit-classifier-streamlit-mongodb`.