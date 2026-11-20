# Clasificador de Frutas con Redes Neuronales Convolucionales (CNN)

## Descripción

Este proyecto desarrolla un sistema de clasificación de imágenes mediante una red neuronal convolucional (CNN). Su objetivo es identificar cinco tipos de frutas a partir de imágenes.

El sistema permite cargar una imagen desde una aplicación web desarrollada con Streamlit y muestra la fruta identificada junto con el nivel de confianza de la predicción.

## Frutas clasificadas

- Apple Golden 1 (manzana)
- Banana 1 (banano)
- Orange 1 (naranja)
- Grape Blue 1 (uva)
- Pineapple 1 (piña)

## Tecnologías utilizadas

- Python
- TensorFlow y Keras
- NumPy
- Pillow
- Streamlit
- Google Colab
- Dataset Fruits-360

## Estructura del proyecto

```text
proyecto-cnn-frutas/
│
├── Proyecto_Final_CNN_Clasificacion_Frutas.ipynb
├── app.py
├── train.py
├── predict.py
├── modelo_frutas.keras
├── requirements.txt
└── README.md
```

## Arquitectura del modelo

La red neuronal convolucional utiliza:

- Capas de aumento de datos.
- Normalización de imágenes.
- Capas convolucionales Conv2D.
- Capas MaxPooling2D.
- GlobalAveragePooling2D.
- Capa Dense con 128 neuronas.
- Dropout para reducir el sobreajuste.
- Capa de salida Softmax para clasificar las cinco frutas.

## Resultados

El modelo fue evaluado con el conjunto de prueba independiente del dataset Fruits-360.

- Imágenes de prueba: 980.
- Precisión obtenida en pruebas: 100 %.
- Pérdida obtenida: 0.000012788 aproximadamente.

Estos resultados corresponden a las imágenes de prueba del conjunto de datos utilizado.

## Instalación

Se recomienda utilizar Python 3.11 o una versión compatible con las dependencias instaladas.

1. Clonar el repositorio:

```bash
git clone https://github.com/JavierInpahu/proyecto-cnn-frutas.git
```

2. Entrar a la carpeta:

```bash
cd proyecto-cnn-frutas
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar la aplicación

Desde la carpeta del proyecto, ejecutar:

```bash
python -m streamlit run app.py
```

La aplicación abrirá una dirección local en el navegador.

## Ejecutar una predicción

También se puede utilizar el archivo predict.py:

```bash
python predict.py imagen.jpg
```

La imagen debe estar disponible en la carpeta desde donde se ejecuta el comando.

## Entrenamiento

El archivo `train.py` contiene el código para entrenar nuevamente el modelo.

Para ejecutarlo se debe descargar el dataset Fruits-360 y organizarlo en la siguiente estructura:

```text
fruits_dataset/
└── fruits-360_100x100/
    └── fruits-360/
        ├── Training/
        └── Test/
```

Luego ejecutar:

```bash
python train.py
```

El modelo entrenado se guardará como `modelo_frutas.keras`.

## Evolución: monolito modular con MongoDB Atlas

Esta versión reorganiza la aplicación en capas con dependencias unidireccionales:

`frontend` → `backend/services` → `backend/repositories` → `backend/database` → Atlas,
y `backend/services` → `ml` → `modelo_frutas.keras`. Las vistas de Streamlit nunca
importan `pymongo` ni `backend.database`.

### Nuevas carpetas

- `frontend/`: vistas y componentes de las cinco secciones (Inicio, Reconocimiento,
  Historial, Administración de frutas y Estadísticas).
- `backend/`: configuración, conexión MongoDB, modelos de dominio, repositorios y servicios.
- `ml/`: manifiesto único de clases, procesamiento de imágenes y carga del modelo.
- `scripts/`: versiones corregidas de `train.py` y `predict.py`, y comprobación de conexión.
- `tests/`: pruebas unitarias y de integración.
- `docs/`: documentación de requisitos, arquitectura, base de datos, conexión y pruebas.

## Configuración de MongoDB Atlas

1. Copie `.env.example` a `.env` (el archivo `.env` se ignora con `.gitignore`):

   ```bash
   copy .env.example .env   (Windows)
   cp .env.example .env     (Linux/macOS)
   ```

2. Reemplace únicamente `REEMPLAZAR_POR_URI_DE_ATLAS` por la URI real del cluster
   Atlas (el cluster ya debe existir y ser accesible).

3. Ejecute la comprobación de conexión:

   ```bash
   python scripts/check_mongo_connection.py
   ```

Las pruebas de integración usan la base `DB_Frutas_Inpahu_test` y requieren la URI
configurada fuera del repositorio:

```bash
pytest -m integration
```

## Scripts heredados

Los archivos `train.py` y `predict.py` de la raíz contienen cercas de Markdown y no
son ejecutables tal cual. Se conservan intactos por compatibilidad; las versiones
corregidas están en `scripts/train.py` y `scripts/predict.py`.

El modelo `modelo_frutas.keras` y el notebook permanecen en la raíz sin cambios; este
cambio no los reentrena ni los mueve.

## Pruebas automatizadas

```bash
pytest -m "not integration"   # unitarias, sin red ni Atlas
pytest -m integration         # integración sobre DB_Frutas_Inpahu_test (requiere URI)
```

## Reversión

Antes de refactorizar `app.py` se creó el tag `git tag pre-refactor`. Para recuperar
la versión heredada del punto de entrada:

```bash
git checkout pre-refactor -- app.py
```

## Autor

Proyecto académico de Ingeniería de Software.
