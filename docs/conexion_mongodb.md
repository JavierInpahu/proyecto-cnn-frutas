# Conexión con MongoDB Atlas

## Requisitos

Instale las dependencias:

```bash
pip install -r requirements.txt
```

## Variables de entorno

Copie `.env.example` a `.env` y reemplace únicamente el marcador:

```bash
copy .env.example .env   (Windows)
cp .env.example .env     (Linux/macOS)
```

En `.env` reemplace `REEMPLAZAR_POR_URI_DE_ATLAS` por la URI real del cluster Atlas.
Nunca suba el archivo `.env` al repositorio (está ignorado por `.gitignore`).

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `MONGODB_URI` | `REEMPLAZAR_POR_URI_DE_ATLAS` | URI de conexión de Atlas (obligatorio) |
| `MONGODB_DATABASE` | `DB_Frutas_Inpahu` | Base de datos principal |
| `MONGODB_FRUITS_COLLECTION` | `fruits` | Colección del catálogo de frutas |
| `MONGODB_PREDICTIONS_COLLECTION` | `predictions` | Colección del historial de predicciones |
| `MONGODB_TIMEOUT_MS` | `8000` | Tiempo de espera de conexión en milisegundos |
| `MODEL_PATH` | `modelo_frutas.keras` | Ruta del modelo Keras en la raíz |

## Comprobación de conexión

```bash
python scripts/check_mongo_connection.py
```

Si la conexión es correcta, imprime un mensaje de éxito sin mostrar la URI.
En caso de fallo, informa el subtipo de error (configuración, autenticación,
permisos o red) sin incluir credenciales.

## Índices

Al iniciar la aplicación se crean los índices:

- `fruits.name`: único, sin distinción de mayúsculas (collation `strength: 2`).
- `predictions.created_at`: descendente, para el historial cronológico.

## Base de pruebas

Las pruebas de integración usan la base `DB_Frutas_Inpahu_test` y solo se
ejecutan con el marcador `pytest -m integration`. Requieren un cluster Atlas
con URI configurada fuera del repositorio.
