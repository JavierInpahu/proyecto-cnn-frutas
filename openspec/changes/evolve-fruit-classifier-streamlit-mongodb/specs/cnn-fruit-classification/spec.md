# Spec Delta

## Purpose

Define la fuente única de verdad de las clases, la validación de compatibilidad del modelo cargado y la equivalencia de resultados con la aplicación original, sin reentrenar ni sustituir el modelo actual.

## ADDED Requirements

### Requirement: RF-29 Manifiesto único de clases
El sistema SHALL definir exclusivamente en `ml/class_manifest.json` el nombre, el nombre científico y la descripción de las cinco clases, en el orden de salida del modelo, y SHALL hacer que el entrenamiento, la predicción, el catálogo y la interfaz lean ese manifiesto.

#### Scenario: Orden y metadatos de clases
- **WHEN** se consulta el manifiesto
- **THEN** el orden es `Apple Golden 1`, `Banana 1`, `Orange 1`, `Grape Blue 1`, `Pineapple 1` y cada clase incluye `scientific_name` y `description`

#### Scenario: Siembra desde el manifiesto
- **WHEN** se siembra el catálogo por primera vez
- **THEN** los tres campos de texto de cada fruta proceden del manifiesto sin inventar valores

#### Scenario: Sin listas duplicadas
- **WHEN** se inspeccionan los módulos nuevos de entrenamiento, predicción, catálogo e interfaz
- **THEN** ninguno define su propia lista de clases y todos consumen el manifiesto

### Requirement: RF-30 Validación de compatibilidad del modelo
El sistema SHALL comprobar que el número de salidas del modelo sea igual al número de clases del manifiesto antes de clasificar.

#### Scenario: Modelo compatible
- **WHEN** el modelo tiene cinco salidas y el manifiesto cinco clases
- **THEN** el modelo se carga y queda listo para clasificar

#### Scenario: Modelo incompatible
- **WHEN** el número de salidas difiere del número de clases del manifiesto
- **THEN** el sistema lanza `ModelMismatchError` y no realiza predicciones

### Requirement: RF-31 Equivalencia con la aplicación original
El sistema SHALL devolver exactamente la misma clase y la misma confianza que `app.py` para una misma imagen.

#### Scenario: Regresión de predicción
- **WHEN** la misma imagen se clasifica con `app.py` y con la nueva arquitectura
- **THEN** ambos devuelven idéntico índice de clase e idéntico valor de confianza

#### Scenario: Línea base antes del refactor
- **WHEN** se registran las salidas de `app.py` para un conjunto de imágenes de referencia antes de modificar el archivo
- **THEN** esos valores se conservan como línea base y la arquitectura evolucionada debe reproducirlos exactamente

### Requirement: RF-32 Ampliación controlada de clases
El sistema SHALL no reconocer clases ausentes del modelo actual y SHALL exigir reentrenamiento, evaluación y validación antes de reemplazar el modelo para ampliar el catálogo.

#### Scenario: Clase no entrenada
- **WHEN** se solicita clasificar una fruta que no está entre las cinco clases
- **THEN** el sistema no afirma reconocerla y devuelve una de las clases entrenadas con su confianza

#### Scenario: Nuevo manifiesto
- **WHEN** se propone un manifiesto con clases adicionales
- **THEN** el modelo actual se mantiene hasta que un modelo reentrenado sea evaluado, validado y acepte el nuevo manifiesto

### Requirement: RNF-05 Conservación del artefacto
El sistema SHALL conservar `modelo_frutas.keras` en la raíz y SHALL utilizar `MODEL_PATH` para localizarlo, sin reentrenarlo ni reemplazarlo en este cambio.

#### Scenario: Ruta configurada
- **WHEN** `MODEL_PATH` apunta a `modelo_frutas.keras`
- **THEN** el cargador abre ese archivo sin copiarlo ni moverlo

#### Scenario: Artefactos en su ubicación actual
- **WHEN** se revisa la ubicación del modelo y del notebook durante este cambio
- **THEN** ambos permanecen en la raíz y cualquier traslado a `models/` o `notebooks/` queda para un cambio posterior

#### Scenario: Archivo ausente
- **WHEN** el archivo configurado no existe
- **THEN** el sistema informa el error de carga sin crear un modelo de reemplazo
