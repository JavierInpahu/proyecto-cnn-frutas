# Registro de cambios

## [FRUIT VISION final] - Recuperación, reentrenamiento y rediseño

### Corregido
- **Doble normalización eliminada**: el modelo conserva una única capa `Rescaling(1./255)` (`normalizacion_unica`) y todo el código de imagen/predicción entrega píxeles 0–255. Los antiguos scripts de la raíz (conteniendo cercas Markdown) se reemplazaron por wrappers ejecutables que delegan en `ml/predictor.py`.
- **Modelo subentrenado reemplazado**: el modelo anterior clasificaba mal las imágenes de prueba (piña → Banana 100 %, manzana → Orange 100 %). Se reentrenó con las cinco clases de Fruits-360 y se guardó el mejor modelo por `val_accuracy`.
- **Orden de clases robusto**: `ml/class_indices.json` persiste índice → clase y se valida contra `ml/class_manifest.json` antes de usar el modelo.

### Añadido
- `scripts/download_dataset.py`: descarga legítima y selectiva de las cinco clases desde `fruits-360/fruits-360-100x100` (CC BY-SA 4.0), sin credenciales de Kaggle.
- `ml/config.py`, `ml/model.py`, `ml/train.py`, `ml/predictor.py`, `ml/class_indices.py`: configuración, arquitectura, entrenamiento/evaluación, predicción y persistencia de clases separadas.
- `scripts/train.py`, `train.py`, `scripts/predict.py`, `predict.py`: entradas reproducibles para entrenar y predecir.
- División entrenamiento/validación/prueba, aumento de datos, `EarlyStopping`, `ReduceLROnPlateau`, `ModelCheckpoint`, métricas reales en `reports/` y gráficas de curvas y matriz de confusión.
- Rechazo de predicciones por baja confianza o margen insuficiente, con explicación de limitaciones.
- Repositorios locales JSON (`backend/repositories/local_*_repository.py`) para que la app funcione sin MongoDB Atlas, conservando los repositorios de Atlas y el documento de predicción de cinco campos.
- Rediseño visual completo: encabezado FRUIT VISION, menú con las tres rutas originales, zona de arrastrar y soltar, vista previa, tarjetas de resultado, barras y gráfica de probabilidades, historial con miniaturas y diseño responsive.
- Pruebas: `tests/unit/test_pipeline_consistency.py` y `tests/unit/test_app_startup.py`, además de muestras reales incluidas en `tests/fixtures/dataset_samples/`.

### Cambiado
- `app.py` es ahora un punto de entrada delgado: compone servicios, aplica el tema y delega en `frontend/`.
- `README.md` documenta instalación, dataset, entrenamiento, predicción, métricas reales y limitaciones.
- `.gitignore` excluye `data/` para no versionar el dataset ni el historial local.

### Ajustes según revisión final
- El menú vuelve a las tres rutas originales: Inicio, Historial y Estadísticas. El reconocimiento sigue viviendo dentro de Inicio.
- Arranque rápido: TensorFlow y el modelo se importan de forma diferida solo al analizar una imagen; no se hace ping a Atlas al iniciar.
- Menú único en la barra lateral, visible incluso en pantallas pequeñas.
- Corregido `TypeError: 'DeltaGenerator' object is not iterable` en la vista de Estadísticas.
- El estado del modelo dice “en preparación” mientras termina el entrenamiento, en lugar de mostrar errores en todas las vistas.
- Paleta visual ajustada a blancos, lavanda y morado: se eliminaron los fondos oscuros y los acentos verdes/coral. `.streamlit/config.toml` fija el tema nativo y los colores de las gráficas.
- Menú único en la barra lateral con la ruta activa en morado; se quitaron los botones repetidos del contenido y las tarjetas decorativas del inicio.
- El botón de carga de imagen usa el mismo degradado morado. Mientras el modelo se entrena, el aviso aparece dentro del área de carga y el input queda deshabilitado.
- Corregido `FrozenInstanceError` al guardar métricas sobre `ClassIndices` (dataclass congelada): se usa `dataclasses.replace`.
- Añadido `scripts/train.py --evaluate-only` para recalcular métricas, matriz y artefactos sin repetir el entrenamiento; el historial real de 12 épocas se restauró desde el log.
- Rechazo reforzado con `ml/ood.py` y `ml/class_prototypes.json`: además de confianza/margen, se rechazan ruido/imágenes uniformes y fotos lejanas a los prototipos de las cinco clases. El modelo era sobreconfiado (100 % con ruido y con una foto ajena); ahora ambos casos se marcan como no reconocidos.
- Un rechazo ya no expone porcentajes: `PredictionOutcome` devuelve `fruit_name="No reconocido"`, confianza 0 y probabilidades vacías; la tarjeta muestra solo **No reconocido** (sin distribución ni gráfica) y la CLI imprime únicamente `NO RECONOCIDO`. Se añadió `tests/unit/test_rechazo_sin_porcentajes.py`.
- Verificación ampliada: 30 imágenes reales del Test por clase (150 en total) reconocidas correctamente, con confianza mínima 98.28 %.
- Rechazo por dominio visual: `MAX_IMAGE_GRADIENT=13.0` (máximo real del Test 11.51, foto de perro 18.70) y `MIN_WHITE_BACKGROUND=0.10` (mínimo real del Test 0.15, fotos arbitrarias 0.00). Se midieron siete imágenes ajenas (perro del usuario, Lena, babuino, flores, casa, gato y ruido): las siete se rechazan sin porcentajes.
- Aclaración verificada por pruebas: la predicción usa los bytes de la imagen subida, nunca el historial ni el nombre del archivo; un rechazo no se persiste. Renombrar un perro como `banana_1.jpg` sigue dando `NO RECONOCIDO`.

### Nota
- No se realizaron commits como parte de esta entrega.
