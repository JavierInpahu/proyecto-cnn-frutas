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

Máximo cinco campos por documento, incluido `_id`. Nunca se almacena el binario de la imagen, solo su nombre.

| Campo | Tipo | Restricción |
| --- | --- | --- |
| `_id` | ObjectId | Generado por MongoDB |
| `fruit_name` | String | Nombre de la clase predicha |
| `confidence` | Double | Entre 0 y 100 |
| `image_name` | String | Solo el nombre del archivo de imagen |
| `created_at` | Date | UTC; índice descendente |

Índices:
- `ix_predictions_created_at_desc`: descendente sobre `created_at`.

## Siembra inicial

El catálogo se siembra idempotentemente desde `ml/class_manifest.json`: nombre, nombre científico y descripción provienen del manifiesto. Las descripciones pueden ajustarse después desde la interfaz (Administración de frutas) sin modificar el manifiesto ni el código.

## Ausencia de imágenes

El sistema no almacena imágenes ni archivos binarios en la base de datos.
