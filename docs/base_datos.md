# Modelo de datos

## Bases de datos

| Base | Uso |
| --- | --- |
| `DB_Frutas_Inpahu` | Producción: catálogo de frutas e historial de predicciones |
| `DB_Frutas_Inpahu_test` | Pruebas de integración (marcador `integration`) |

## Colección `fruits` (catálogo de frutas)

Máximo cinco campos por documento, incluido `_id`. Sin contadores autoincrementales.

| Campo | Tipo | Restricción |
| --- | --- | --- |
| `_id` | ObjectId | Generado por MongoDB |
| `name` | String | Único sin distinguir mayúsculas (índice único con collation `strength: 2`) |
| `scientific_name` | String | Obligatorio, no vacío |
| `description` | String | Texto libre |
| `active` | Boolean | `true` por defecto |

Índices:
- `ux_fruits_name_case_insensitive`: único sobre `name`, collation `strength: 2`.

## Colección `predictions` (historial de predicciones)

Cinco campos obligatorios más dos opcionales para recuperar la imagen del historial. Nunca se almacena el binario original.

| Campo | Tipo | Restricción |
| --- | --- | --- |
| `_id` | ObjectId | Generado por MongoDB |
| `fruit_name` | String | Nombre de la clase predicha |
| `confidence` | Double | Entre 0 y 100 |
| `image_name` | String | Solo el nombre del archivo de imagen |
| `created_at` | Date | UTC; índice descendente |
| `thumbnail` | String | Opcional; JPEG base64 de hasta 180×180 (calidad 75) |
| `image_data` | String | Opcional; imagen original en base64 (máx. 12 MB para no superar el límite de documento) |
| `image_meta` | Document | Opcional; `width`, `height`, `format`, `size_bytes`, `mime_type` |

Índices:
- `ix_predictions_created_at_desc`: descendente sobre `created_at`.

## Siembra inicial

El catálogo se siembra idempotentemente desde `ml/class_manifest.json`: nombre, nombre científico y descripción provienen del manifiesto. Las descripciones pueden ajustarse después desde la interfaz (Administración de frutas) sin modificar el manifiesto ni el código.

## Imágenes en el historial

Se guarda la imagen original en base64 (`image_data`) para poder recuperarla y descargarla desde el historial, junto con una miniatura JPEG reducida (180×180, calidad 75) para mostrarla sin cargar todo el dato y sus metadatos (dimensiones, formato, peso y tipo MIME). El cargador de la interfaz limita el archivo a 5 MB; con el tope adicional de 12 MB del código, el documento no supera el límite de 16 MB de MongoDB.
