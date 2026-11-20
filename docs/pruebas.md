# Pruebas automatizadas

## Pruebas unitarias (se ejecutan por defecto)

```bash
pytest -m "not integration"
```

Validan configuración, conexión (con dobles y `mongomock`), CRUD de frutas, historial
de predicciones, procesamiento de imágenes, carga del modelo, clasificación y
regresión contra `app.py`. Nunca se conectan a Atlas ni usan credenciales reales.

## Pruebas de integración

```bash
pytest -m integration
```

Requieren la variable de entorno `MONGODB_URI` configurada fuera del repositorio
(y un cluster Atlas con permisos de lectura/escritura). Operan exclusivamente
sobre la base `DB_Frutas_Inpahu_test` y nunca escriben en `DB_Frutas_Inpahu`.

## Estructura

- `tests/unit/`: pruebas aisladas sin red.
- `tests/integration/`: pruebas de integración con el marcador `integration`.
- `tests/fixtures/`: imágenes de referencia y línea base de la versión heredada de `app.py`.
- `pytest.ini`: registra el marcador `integration` y lo excluye por defecto.

## Reglas

- No incluir credenciales reales ni la URI de Atlas en ningún archivo de prueba.
- Una prueba unitaria que intente abrir red se considera fallida por diseño.
