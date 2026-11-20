# Spec Delta

## Purpose

Define la estrategia de pruebas automatizadas que verifica la conexión, el CRUD, el procesamiento de imágenes y la clasificación sin depender de credenciales reales ni de Atlas en las pruebas unitarias.

## ADDED Requirements

### Requirement: RF-36 Pruebas unitarias aisladas
El sistema SHALL ejecutar pruebas unitarias sin conectarse a Atlas, usando dobles de prueba o `mongomock`.

#### Scenario: Repositorio simulado
- **WHEN** se ejecuta una prueba de servicio con un repositorio doble
- **THEN** la prueba no realiza conexiones de red

#### Scenario: Colección simulada
- **WHEN** se ejecuta una prueba de repositorio con `mongomock`
- **THEN** las operaciones CRUD se validan sin un cluster remoto

### Requirement: RF-37 Pruebas de integración separadas
El sistema SHALL disponer de pruebas de integración marcadas con `integration` que utilicen la base `DB_Frutas_Inpahu_test`.

#### Scenario: Base de pruebas
- **WHEN** se ejecuta una prueba con el marcador `integration`
- **THEN** la prueba opera exclusivamente sobre `DB_Frutas_Inpahu_test`

#### Scenario: Ejecución por defecto
- **WHEN** se ejecuta la suite sin configuración de Atlas
- **THEN** las pruebas marcadas como `integration` quedan excluidas o correctamente omitidas

### Requirement: RF-38 Cobertura de pruebas exigida
El sistema SHALL incluir pruebas que cubran conexión, CRUD de frutas, registro y consulta de predicciones, procesamiento de imágenes, carga del modelo, clasificación y regresión contra `app.py`.

#### Scenario: Conexión y errores
- **WHEN** se ejecuta la suite unitaria
- **THEN** existen pruebas para conexión correcta y para los subtipos de `MongoConnectionError`

#### Scenario: Regresión del modelo
- **WHEN** se ejecuta la prueba de regresión con una imagen de referencia
- **THEN** se verifica que la clase y la confianza coinciden con `app.py`

#### Scenario: Preprocesamiento
- **WHEN** se ejecutan las pruebas de imagen
- **THEN** se validan los rechazos de formato y tamaño y la forma `(1, 100, 100, 3)` sin división entre 255

### Requirement: RNF-06 Sin secretos en pruebas
El sistema SHALL no incluir credenciales reales en pruebas ni en archivos de configuración de prueba.

#### Scenario: Configuración de prueba
- **WHEN** una prueba necesita una URI
- **THEN** utiliza un valor simulado o el marcador `REEMPLAZAR_POR_URI_DE_ATLAS`
