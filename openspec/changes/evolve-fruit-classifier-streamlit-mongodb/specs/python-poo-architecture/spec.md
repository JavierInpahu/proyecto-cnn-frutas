# Spec Delta

## Purpose

Define la estructura en capas, los contratos de las clases del dominio y la estrategia de errores que permiten evolucionar el clasificador sin acoplar la interfaz a la base de datos ni al modelo.

## ADDED Requirements

### Requirement: RF-19 Dependencias unidireccionales
El sistema SHALL organizar sus componentes en capas con dependencias únicamente descendentes: frontend, servicios, repositorios, base de datos y, por otra rama, módulo de machine learning.

#### Scenario: Flujo de reconocimiento
- **WHEN** la interfaz solicita una clasificación con guardado
- **THEN** la petición pasa por servicios, que usan repositorios y el módulo de machine learning sin que la interfaz acceda a la base de datos

#### Scenario: Acceso directo prohibido
- **WHEN** se inspecciona el código de las vistas Streamlit
- **THEN** ninguna importa `pymongo` ni `backend.database`

### Requirement: RF-20 Contratos POO con inyección de dependencias
El sistema SHALL exponer `Settings`, `MongoConnection`, `Fruit`, `Prediction`, `FruitRepository`, `PredictionRepository`, `FruitService`, `PredictionService`, `ClassificationService`, `ImageProcessor` y `ModelLoader` con dependencias inyectables.

#### Scenario: Construcción de servicios
- **WHEN** se construye un servicio
- **THEN** sus repositorios o colaboradores se reciben como parámetros en lugar de crearse internamente

#### Scenario: Sustitución en pruebas
- **WHEN** una prueba necesita simular la base de datos
- **THEN** puede proporcionar un doble del repositorio sin modificar el servicio

### Requirement: RF-21 Excepciones de dominio
El sistema SHALL representar sus fallos con `ValidationError`, `DuplicateFruitError`, `NotFoundError`, `InvalidImageError`, `ModelMismatchError` y `MongoConnectionError`, con subtipos de configuración, autenticación, permisos y red para esta última.

#### Scenario: Error de dominio
- **WHEN** una operación de catálogo recibe datos inválidos
- **THEN** se lanza `ValidationError` en lugar de una excepción genérica

#### Scenario: Error de infraestructura
- **WHEN** falla la autenticación contra Atlas
- **THEN** se lanza el subtipo de autenticación de `MongoConnectionError`

### Requirement: RNF-04 Configuración centralizada
El sistema SHALL concentrar la lectura de rutas, nombres de colección y tiempos de espera en un único objeto de configuración, sin valores literales repetidos en los servicios.

#### Scenario: Ruta del modelo
- **WHEN** se cambia `MODEL_PATH` en el entorno
- **THEN** la carga del modelo utiliza la nueva ruta sin cambios en el código de los servicios
