# Spec Delta

## Purpose

Define la documentación y las medidas de higiene del repositorio que acompañan a la evolución, para que cualquier persona pueda instalar, configurar, operar y verificar el sistema sin conocimientos implícitos.

## ADDED Requirements

### Requirement: RF-39 README actualizado
El sistema SHALL mantener un `README.md` que describa la arquitectura modular, la instalación, la configuración por entorno, la ejecución de la interfaz y el estado de los scripts heredados.

#### Scenario: Puesta en marcha
- **WHEN** una persona sigue el README desde un clon limpio
- **THEN** puede identificar las variables necesarias y el comando de ejecución de la interfaz

#### Scenario: Scripts heredados
- **WHEN** el README menciona `train.py` y `predict.py`
- **THEN** aclara que los originales no son ejecutables y que las versiones corregidas están en `scripts/`

### Requirement: RF-40 Documentación técnica
El sistema SHALL incluir `docs/requisitos.md`, `docs/arquitectura.md`, `docs/base_datos.md`, `docs/conexion_mongodb.md`, `docs/pruebas.md` y `CHANGELOG.md`.

#### Scenario: Modelo de datos documentado
- **WHEN** se consulta `docs/base_datos.md`
- **THEN** se describen bases, colecciones, campos, índices y la ausencia de imágenes almacenadas

#### Scenario: Registro de cambios
- **WHEN** se consulta `CHANGELOG.md`
- **THEN** consta la evolución a monolito modular, Atlas y persistencia de historial

### Requirement: RF-41 Protección del repositorio
El sistema SHALL excluir del control de versiones los archivos de entorno, secretos de Kaggle y Streamlit, cachés y archivos compilados de Python, y SHALL normalizar el fin de línea.

#### Scenario: Archivos ignorados
- **WHEN** se crean `.env`, `kaggle.json`, `.streamlit/secrets.toml`, `__pycache__/` o `.pytest_cache/`
- **THEN** Git no los añade al índice

#### Scenario: Excepción de plantilla
- **WHEN** se crea `.env.example`
- **THEN** el archivo sí puede versionarse con el marcador `REEMPLAZAR_POR_URI_DE_ATLAS`

#### Scenario: Fin de línea
- **WHEN** se modifica un archivo de texto en Windows o Linux
- **THEN** `.gitattributes` normaliza el fin de línea y evita diffs espurios

### Requirement: RNF-07 Idioma de la documentación
El sistema SHALL mantener toda la documentación y los artefactos de este cambio en español.

#### Scenario: Revisión de documentación
- **WHEN** se revisan los archivos de documentación del cambio
- **THEN** su contenido está redactado en español
