# Spec Delta

## Purpose

Define la validación y el preprocesamiento de las imágenes cargadas para garantizar que el modelo reciba exactamente el mismo tipo de entrada que en la aplicación original.

## ADDED Requirements

### Requirement: RF-33 Validación de formato y tamaño
El sistema SHALL aceptar únicamente archivos JPG, JPEG y PNG de hasta 5 MB y SHALL lanzar `InvalidImageError` para cualquier otro caso.

#### Scenario: Formato permitido
- **WHEN** se carga un archivo PNG de 4 MB
- **THEN** el archivo se acepta para procesamiento

#### Scenario: Formato rechazado
- **WHEN** se carga un archivo GIF
- **THEN** el sistema lanza `InvalidImageError`

#### Scenario: Tamaño excedido
- **WHEN** se carga un archivo JPG de 6 MB
- **THEN** el sistema lanza `InvalidImageError`

### Requirement: RF-34 Conversión a RGB y redimensionado
El sistema SHALL convertir la imagen a RGB y redimensionarla a 100×100 píxeles.

#### Scenario: Imagen con canal alfa
- **WHEN** se carga un PNG con canal alfa
- **THEN** se convierte a RGB antes de redimensionar

#### Scenario: Imagen grande
- **WHEN** se carga una imagen de 1200×800
- **THEN** se obtiene una imagen de 100×100 píxeles

### Requirement: RF-35 Formato de entrada del modelo
El sistema SHALL entregar un arreglo `float32` con forma `(1, 100, 100, 3)` y valores en rango 0-255, sin dividir entre 255.

#### Scenario: Preparación de la entrada
- **WHEN** se procesa una imagen válida
- **THEN** el arreglo entregado al modelo es `float32`, de forma `(1, 100, 100, 3)` y conserva la escala 0-255

#### Scenario: Sin normalización duplicada
- **WHEN** se inspecciona la preparación de la entrada
- **THEN** no existe una división entre 255 porque el modelo incluye `Rescaling`
