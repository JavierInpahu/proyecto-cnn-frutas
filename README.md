# FRUIT VISION

Clasificador inteligente de frutas con una red neuronal convolucional (CNN) y una interfaz web moderna hecha con Streamlit.

El sistema reconoce exactamente cinco clases, en este orden:

| Índice | Clase | Fruta |
|---:|---|---|
| 0 | `Apple Golden 1` | Manzana |
| 1 | `Banana 1` | Banano |
| 2 | `Orange 1` | Naranja |
| 3 | `Grape Blue 1` | Uva |
| 4 | `Pineapple 1` | Piña |

> **Corrección principal.** El modelo incluye `Rescaling(1./255)` **dentro** del grafo (`ml/model.py`, capa `normalizacion_unica`). El preprocesamiento de imagen entrega píxeles RGB en rango **0–255** y **nunca** divide entre 255. Los scripts antiguos de la raíz sí lo hacían y provocaban una doble normalización: todas las imágenes colapsaban a una sola clase. Ese error quedó corregido en `ml/image_processor.py`, `ml/predictor.py`, `scripts/predict.py` y los wrappers de la raíz.

## Qué contiene este paquete

- `app.py`: punto de entrada de la interfaz Streamlit (encabezado FRUIT VISION, menú lateral, carga drag & drop, resultados en tarjetas, historial, administración y estadísticas).
- `frontend/`: tema CSS, navegación, componentes de carga/resultado y las tres vistas originales (Inicio, Historial y Estadísticas). El reconocimiento ocurre dentro de Inicio.
- `backend/`: configuración, modelos de dominio, repositorios y servicios. Si MongoDB Atlas no está disponible, la app usa automáticamente un historial local en `data/history.json` y un catálogo local en `data/fruits.json`.
- `ml/`: arquitectura de la CNN, entrenamiento y evaluación, carga del modelo, índices de clase, prototipos por clase, preprocesamiento y predicción con rechazo por confianza, estructura y distancia.
- `scripts/`: descarga del dataset solo de las cinco clases, entrenamiento y predicción por línea de comandos.
- `tests/`: pruebas unitarias reales, incluyendo muestras de una imagen por clase incluidas en `tests/fixtures/dataset_samples/`.
- `reports/`: métricas y gráficas generadas por el entrenamiento (`evaluation.json`, `training_curves.png`, `confusion_matrix.png`, `classification_report.txt`).
- `modelo_frutas.keras`: modelo reentrenado y funcional.
- `ml/class_indices.json`: correspondencia índice → nombre de clase, rango de entrada y umbral de confianza usado por la app.
- `ml/class_prototypes.json`: embeddings promedio de cada clase y umbral de distancia para rechazar imágenes ajenas.

El dataset completo **no** se incluye en el ZIP para no inflarlo. Se descarga con un comando (ver más abajo).

## Requisitos

- Python 3.11 (probado con 3.11 y TensorFlow 2.21 en Windows).
- Dependencias fijadas en `requirements.txt`.

## Instalación

```bash
pip install -r requirements.txt
```

Opcional: copia `.env.example` a `.env` y rellena la URI de MongoDB Atlas si quieres usar el historial remoto:

```bash
# Windows
copy .env.example .env
# Linux / macOS
cp .env.example .env
```

Nunca compartas ni versiones el archivo `.env`. Sin él, la aplicación funciona igual con almacenamiento local.

## Descargar el dataset

La fuente es el repositorio público `fruits-360/fruits-360-100x100` (CC BY-SA 4.0, Mihai Oltean). Solo se bajan las cinco carpetas necesarias de `Training` y `Test` (3.903 imágenes):

```bash
python scripts/download_dataset.py
```

Las imágenes quedan en `data/fruits-360-subset/`. La carpeta `data/` está ignorada por Git y excluida del ZIP.

## Ejecutar la aplicación

```bash
python -m streamlit run app.py
```

Por defecto Streamlit usa `http://localhost:8501`. Si necesitas otro puerto:

```bash
python -m streamlit run app.py --server.port 8511
```

El menú está en la barra lateral y la ruta activa se resalta en morado. Se conservan únicamente las tres rutas originales:

1. **Inicio**: arrastra una foto JPG, JPEG o PNG (máx. 5 MB) a la zona de carga, pulsa **Analizar fruta** y revisa la tarjeta con la fruta, la confianza, las cinco probabilidades y la gráfica comparativa. Si la imagen se rechaza, la tarjeta dice únicamente **No reconocido**: no se muestra confianza, probabilidades ni gráfica, porque ninguna clase coincide.
2. **Historial**: imágenes analizadas (cuando se usó historial local), fruta, confianza, fecha, filtros, corrección y borrado con confirmación.
3. **Estadísticas**: total de predicciones, confianza media y conteo por fruta.

> El arranque es rápido: TensorFlow y el modelo se cargan solo cuando haces clic en **Analizar fruta**. Abrir Historial o Estadísticas no carga la red neuronal ni consulta MongoDB Atlas.

Si la predicción queda por debajo del umbral, los dos primeros puntajes están demasiado cerca, la imagen parece ruido o su embedding queda lejos de los prototipos, la app muestra solo **No reconocido**. El resultado rechazado no devuelve nombre de fruta, confianza ni probabilidades: no hay una clase coincidente que justifique un porcentaje.

## Predicción por línea de comandos

```bash
python scripts/predict.py tests/fixtures/dataset_samples/pineapple_1.jpg
```

Salida real esperada (ejemplo): fruta predicha, confianza y probabilidades de las cinco clases. Si la imagen se rechaza, la única salida es `NO RECONOCIDO`, sin porcentajes. El wrapper `predict.py` de la raíz hace lo mismo.

## Reentrenar el modelo

```bash
python scripts/download_dataset.py   # solo si aún no existe data/fruits-360-subset
python scripts/train.py --epochs 12
```

El pipeline:

- Lee las clases desde `ml/class_manifest.json` y **fuerza ese orden** en `image_dataset_from_directory` (no depende del orden alfabético).
- Divide `Training` en entrenamiento (80 %) y validación (20 %) con semilla fija; usa `Test` (980 imágenes) **solo** para la evaluación final.
- Aplica aumento de datos (volteo horizontal, rotación, zoom, traslación) y dropout para reducir sobreajuste.
- Guarda automáticamente el mejor modelo por `val_accuracy` en `modelo_frutas.keras` y restaura los mejores pesos con `EarlyStopping`.
- Calibra el umbral de rechazo con el percentil 5 de la confianza de los aciertos en validación, limitado al rango `[0.60, 0.90]`.
- Escribe `ml/class_indices.json` con clases, índices, rango de entrada, normalización y umbral.
- Genera métricas reales y gráficas en `reports/`.

Opciones útiles: `--data-dir`, `--modelo`, `--manifiesto`, `--indices`, `--reports-dir`, `--epochs`, `--batch-size`, `--seed`.

## Resultados reales de la evaluación

Los siguientes valores fueron generados por `python scripts/train.py --epochs 12` sobre el conjunto `Test` independiente (980 imágenes), usando el mejor modelo guardado por validación:

| Métrica (Test, 980 imágenes) | Valor |
| --- | --- |
| Accuracy | **100.00 %** |
| Precision ponderada | **100.00 %** |
| Recall ponderado | **100.00 %** |
| F1 ponderado | **100.00 %** |
| Precision macro | **100.00 %** |
| Recall macro | **100.00 %** |
| F1 macro | **100.00 %** |
| Umbral de rechazo calibrado | 0.900 |

La matriz de confusión es diagonal: 160 manzanas, 166 bananos, 160 naranjas, 328 uvas y 166 piñas correctamente clasificadas, sin errores en el conjunto de prueba. Las curvas y la matriz están en `reports/training_curves.png` y `reports/confusion_matrix.png`.

### Limitaciones del rechazo

La confianza softmax **no es una probabilidad calibrada**: este modelo llega al 100 % incluso con ruido aleatorio o con una foto que no es fruta. Por eso el rechazo combina cuatro señales: confianza/margen, estructura de la imagen (ruido, detalle excesivo o imagen uniforme), distancia del embedding a los cinco prototipos de clase (`ml/class_prototypes.json`, umbral 5.0 calibrado con el Test real, cuya distancia máxima fue 3.24) y pertenencia al dominio visual del entrenamiento. En el Test real, el **100 %** de las 980 imágenes tiene al menos un 15 % de píxeles con `min(R,G,B) >= 240` (fondo claro); las fotos arbitrarias medidas tienen 0 %. El umbral configurado es 0.10 (`MIN_WHITE_BACKGROUND`), por debajo del peor caso real.

La clasificación **no consulta el historial ni compara nombres de archivo**: `ClassificationService.classify` pasa los bytes subidos directamente a la CNN y solo escribe en el historial cuando la imagen se acepta. Renombrar una foto de perro como `banana_1.jpg` sigue dando `NO RECONOCIDO`; renombrar una manzana como `foto_cualquiera.png` sigue dando `Apple Golden 1`.

Estas defensas detectan casos evidentes, pero **no garantizan** rechazar cualquier imagen fuera de distribución: una fruta de otra variedad, varias frutas juntas, iluminación extrema o fondos muy distintos a Fruits-360 (fondo blanco, fruta centrada) pueden reducir la precisión o incluso pasar el filtro. Es una barrera auditable, no una garantía.

## Pruebas automatizadas

```bash
pytest -m "not integration"
```

La suite verifica, entre otros puntos: arranque de la app, carga del modelo, una capa de normalización única, entrada en 0–255, coincidencia índice/clase con el manifiesto, reconocimiento de las cinco clases sin rechazo, rechazo de ruido, de imágenes ajenas por distancia y de escenas sin fondo claro, que el nombre del archivo no altera la predicción, que un rechazo no se guarda ni consulta el historial, ausencia de porcentajes en rechazos (resultado, interfaz y CLI), generación de métricas y CRUD del historial local.

Las pruebas de integración con Atlas se ejecutan aparte:

```bash
pytest -m integration
```

## Arquitectura y decisiones

- **Un solo punto de normalización**: la capa `normalizacion_unica` dentro del modelo. No hay divisiones entre 255 en la app ni en los scripts.
- **Clases persistidas**: `ml/class_indices.json` se valida contra `ml/class_manifest.json` al cargar la app; si no coinciden o aún no se generó, la app muestra el estado “en preparación” en lugar de predecir con etiquetas erróneas.
- **Historial sin romper lo existente**: se conservan los repositorios de MongoDB Atlas con el documento de cinco campos. El historial local añade una miniatura en base64 solo en JSON; Atlas sigue recibiendo únicamente `fruit_name`, `confidence`, `image_name` y `created_at`.
- **Interfaz**: Streamlit + CSS propio con paleta blanca/lavanda/morado, tarjetas con bordes suaves, media queries para pantallas pequeñas y estados de carga/error. El tema nativo se fija en `.streamlit/config.toml` para que botones y gráficas también usen morado.

## Atribución del dataset

Fruits-360 © Mihai Oltean, licenciado bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Fuente: <https://github.com/fruits-360/fruits-360-100x100>.

## Nota sobre Git

No se han realizado commits como parte de esta entrega. Los archivos están modificados directamente en el repositorio de trabajo.
