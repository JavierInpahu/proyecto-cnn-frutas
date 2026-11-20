# Spec Delta

## Purpose

Define la experiencia de usuario de la aplicación Streamlit, sus cinco secciones y el comportamiento ante fallos de validación o de persistencia durante el reconocimiento.

## ADDED Requirements

### Requirement: RF-22 Cinco secciones de la interfaz
El sistema SHALL presentar las secciones Inicio, Reconocimiento, Historial, Administración de frutas y Estadísticas.

#### Scenario: Navegación
- **WHEN** se abre la aplicación
- **THEN** el usuario puede acceder a las cinco secciones desde la navegación

### Requirement: RF-23 Reconocimiento de una imagen
El sistema SHALL permitir cargar una imagen, validarla, mostrarla y presentar la fruta predicha, la confianza y la probabilidad de cada clase.

#### Scenario: Predicción correcta
- **WHEN** se carga una imagen válida
- **THEN** se muestran la imagen, la fruta predicha, la confianza y las cinco probabilidades

#### Scenario: Imagen inválida
- **WHEN** se carga un archivo con formato no permitido o mayor de 5 MB
- **THEN** se muestra un error comprensible y no se intenta clasificar

### Requirement: RF-24 Advertencia por baja confianza
El sistema SHALL advertir cuando la confianza de la predicción sea inferior al 60 %.

#### Scenario: Confianza baja
- **WHEN** la confianza obtenida es 59,9 %
- **THEN** se muestra una advertencia al usuario

#### Scenario: Confianza suficiente
- **WHEN** la confianza obtenida es 60 % o más
- **THEN** no se muestra la advertencia de baja confianza

### Requirement: RF-25 Persistencia tolerante a fallos
El sistema SHALL guardar cada predicción en MongoDB y SHALL mostrar el resultado aunque la base no responda, avisando que no se pudo guardar.

#### Scenario: Guardado correcto
- **WHEN** la base de datos responde tras una predicción
- **THEN** el resultado se muestra y queda registrado en el historial

#### Scenario: Base no disponible
- **WHEN** la base de datos no responde tras una predicción
- **THEN** se muestra igualmente la predicción y un aviso de que no se pudo guardar

### Requirement: RF-26 Gestión del historial desde la interfaz
El sistema SHALL permitir consultar, filtrar, corregir y eliminar predicciones desde la sección Historial, con confirmación para el borrado.

#### Scenario: Filtrado combinado
- **WHEN** el usuario selecciona una fruta y un rango de fechas
- **THEN** la tabla muestra solo las predicciones que cumplen ambos filtros

#### Scenario: Borrado confirmado
- **WHEN** el usuario confirma la eliminación de una predicción
- **THEN** la predicción desaparece del historial

### Requirement: RF-27 Administración de frutas desde la interfaz
El sistema SHALL permitir crear, listar, editar, activar, desactivar y eliminar frutas desde la sección Administración de frutas.

#### Scenario: Alta y siembra
- **WHEN** el usuario registra una fruta o ejecuta la siembra del catálogo
- **THEN** el listado refleja los cambios sin duplicar nombres

#### Scenario: Borrado cancelado
- **WHEN** el usuario cancela la confirmación de borrado
- **THEN** la fruta permanece en el catálogo

### Requirement: RF-28 Estadísticas
El sistema SHALL mostrar el total de predicciones, el conteo por fruta y la confianza promedio en la sección Estadísticas.

#### Scenario: Histórico con datos
- **WHEN** existen predicciones registradas
- **THEN** se muestran el total, la cantidad por fruta y la confianza media

#### Scenario: Sin datos
- **WHEN** no hay predicciones registradas
- **THEN** las estadísticas se muestran vacías o en cero sin errores
