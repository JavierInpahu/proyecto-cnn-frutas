# Spec Delta

## Purpose

Define el registro y la consulta del historial de predicciones, incluida la corrección de la fruta, los filtros combinables y la eliminación confirmada, sin almacenar imágenes.

## ADDED Requirements

### Requirement: RF-13 Registro de predicciones
El sistema SHALL registrar cada predicción con fruta, confianza entre 0 y 100, nombre de archivo y fecha UTC.

#### Scenario: Registro correcto
- **WHEN** se registra una predicción con fruta y confianza válidas
- **THEN** queda almacenada con `created_at` en UTC y un `_id` de tipo ObjectId

#### Scenario: Confianza fuera de rango
- **WHEN** se intenta registrar una confianza negativa o mayor que 100
- **THEN** el sistema lanza `ValidationError` y no almacena la predicción

### Requirement: RF-14 Listado cronológico
El sistema SHALL listar las predicciones ordenadas por `created_at` de forma descendente.

#### Scenario: Historial completo
- **WHEN** se solicita el historial
- **THEN** se devuelven las predicciones de la más reciente a la más antigua

### Requirement: RF-15 Consulta por identificador
El sistema SHALL permitir consultar una predicción por su `_id`.

#### Scenario: Predicción existente
- **WHEN** se consulta un `_id` almacenado
- **THEN** se devuelven sus campos completos

#### Scenario: Predicción inexistente
- **WHEN** se consulta un `_id` que no existe
- **THEN** el sistema lanza `NotFoundError`

### Requirement: RF-16 Corrección de la fruta predicha
El sistema SHALL permitir corregir `fruit_name` sin modificar `created_at`.

#### Scenario: Corrección aplicada
- **WHEN** se corrige el nombre de la fruta de una predicción existente
- **THEN** el nuevo valor queda almacenado y `created_at` conserva su valor original

#### Scenario: Corrección inválida
- **WHEN** se intenta corregir con un nombre vacío
- **THEN** el sistema lanza `ValidationError` y no modifica la predicción

### Requirement: RF-17 Filtros combinables
El sistema SHALL permitir filtrar el historial por fruta y por rango de fechas, de forma independiente y combinada.

#### Scenario: Filtro por fruta
- **WHEN** se filtra por una fruta concreta
- **THEN** se devuelven solo sus predicciones

#### Scenario: Filtros combinados
- **WHEN** se filtra por una fruta y por un rango de fechas a la vez
- **THEN** se devuelven solo las predicciones que cumplen ambas condiciones

### Requirement: RF-18 Eliminación con confirmación
El sistema SHALL eliminar una predicción solo después de una confirmación explícita.

#### Scenario: Eliminación confirmada
- **WHEN** se confirma la eliminación de una predicción
- **THEN** la predicción deja de estar en la colección

#### Scenario: Eliminación cancelada
- **WHEN** se rechaza la confirmación
- **THEN** la predicción permanece sin cambios

### Requirement: RNF-03 Persistencia sin imágenes
El sistema SHALL almacenar únicamente el nombre del archivo de imagen y SHALL limitar cada predicción a cinco campos, incluido `_id`.

#### Scenario: Estructura almacenada
- **WHEN** se almacena una predicción
- **THEN** sus campos son exclusivamente `_id`, `fruit_name`, `confidence`, `image_name` y `created_at`, y no se guarda el binario de la imagen

#### Scenario: Índice de fechas
- **WHEN** se inicializa la colección de predicciones
- **THEN** existe un índice descendente sobre `created_at`
