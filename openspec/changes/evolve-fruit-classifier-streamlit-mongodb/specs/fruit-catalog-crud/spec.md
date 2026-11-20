# Spec Delta

## Purpose

Define la gestión del catálogo de frutas: alta, consulta, actualización, activación, baja y siembra inicial, garantizando nombres únicos y una representación de datos acotada.

## ADDED Requirements

### Requirement: RF-05 Creación de frutas
El sistema SHALL permitir crear una fruta con nombre, nombre científico y descripción, con `active` en `true` por defecto.

#### Scenario: Alta correcta
- **WHEN** se crea una fruta con nombre, nombre científico y descripción válidos
- **THEN** queda almacenada con `active` en `true` y un `_id` de tipo ObjectId

#### Scenario: Datos incompletos
- **WHEN** falta el nombre o el nombre científico
- **THEN** el sistema lanza `ValidationError` y no almacena la fruta

### Requirement: RF-06 Unicidad de nombre
El sistema SHALL impedir dos frutas con el mismo nombre sin distinguir mayúsculas y minúsculas.

#### Scenario: Duplicado por mayúsculas
- **WHEN** se intenta crear `banana 1` existiendo `Banana 1`
- **THEN** el sistema lanza `DuplicateFruitError` y conserva la fruta original

#### Scenario: Índice único
- **WHEN** se inicializa la colección de frutas
- **THEN** existe un índice único sobre `name`

### Requirement: RF-07 Listado de frutas
El sistema SHALL permitir listar todas las frutas o únicamente las activas.

#### Scenario: Listado completo
- **WHEN** se solicita el catálogo sin filtro
- **THEN** se devuelven frutas activas e inactivas

#### Scenario: Solo activas
- **WHEN** se solicita únicamente el catálogo activo
- **THEN** se devuelven solo las frutas con `active` en `true`

### Requirement: RF-08 Consulta por identificador
El sistema SHALL permitir consultar una fruta por su `_id`.

#### Scenario: Fruta existente
- **WHEN** se consulta un `_id` almacenado
- **THEN** se devuelven sus campos completos

#### Scenario: Fruta inexistente
- **WHEN** se consulta un `_id` que no existe
- **THEN** el sistema lanza `NotFoundError`

### Requirement: RF-09 Actualización de frutas
El sistema SHALL permitir actualizar los campos editables de una fruta existente.

#### Scenario: Actualización correcta
- **WHEN** se actualizan la descripción y el nombre científico de una fruta
- **THEN** los cambios quedan reflejados sin modificar su `_id`

#### Scenario: Actualización a nombre duplicado
- **WHEN** se cambia el nombre por otro ya existente ignorando mayúsculas
- **THEN** el sistema lanza `DuplicateFruitError` y no aplica el cambio

### Requirement: RF-10 Activación y desactivación
El sistema SHALL permitir marcar una fruta como activa o inactiva sin eliminarla.

#### Scenario: Desactivar fruta
- **WHEN** se desactiva una fruta existente
- **THEN** su campo `active` pasa a `false` y deja de aparecer en el listado de activas

#### Scenario: Reactivar fruta
- **WHEN** se reactiva una fruta inactiva
- **THEN** su campo `active` pasa a `true`

### Requirement: RF-11 Eliminación con confirmación
El sistema SHALL eliminar una fruta solo después de una confirmación explícita.

#### Scenario: Confirmación aceptada
- **WHEN** se confirma la eliminación de una fruta existente
- **THEN** la fruta deja de estar en la colección

#### Scenario: Confirmación rechazada
- **WHEN** se rechaza la confirmación
- **THEN** la fruta permanece sin cambios

### Requirement: RF-12 Siembra desde el manifiesto
El sistema SHALL poblar el catálogo desde el manifiesto de clases sin crear duplicados.

#### Scenario: Primera siembra
- **WHEN** se siembra el catálogo con un manifiesto de cinco clases y la colección está vacía
- **THEN** se crean cinco frutas activas, una por clase

#### Scenario: Siembra repetida
- **WHEN** se ejecuta de nuevo la siembra con el mismo manifiesto
- **THEN** no se crean frutas nuevas ni se lanza un error de duplicado

### Requirement: RNF-02 Representación acotada del catálogo
El sistema SHALL almacenar como máximo cinco campos por documento de fruta, incluido `_id`, y SHALL usar ObjectId en lugar de contadores autoincrementales.

#### Scenario: Estructura almacenada
- **WHEN** se almacena una fruta
- **THEN** sus campos son exclusivamente `_id`, `name`, `scientific_name`, `description` y `active`
