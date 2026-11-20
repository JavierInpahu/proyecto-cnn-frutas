# Spec Delta

## Purpose

Define la configuración, el establecimiento de la conexión con MongoDB Atlas y la clasificación de fallos para que el resto del sistema pueda persistir frutas y predicciones sin exponer secretos.

## ADDED Requirements

### Requirement: RF-01 Configuración desde variables de entorno
El sistema SHALL obtener la URI, la base de datos, los nombres de colección y el tiempo de espera de variables de entorno, y SHALL rechazar una URI que conserve el marcador de ejemplo.

#### Scenario: Configuración válida
- **WHEN** están definidas `MONGODB_URI`, `MONGODB_DATABASE`, `MONGODB_FRUITS_COLLECTION`, `MONGODB_PREDICTIONS_COLLECTION` y `MONGODB_TIMEOUT_MS`
- **THEN** la configuración queda disponible para la capa de conexión con esos valores

#### Scenario: URI de ejemplo sin reemplazar
- **WHEN** `MONGODB_URI` es `REEMPLAZAR_POR_URI_DE_ATLAS`
- **THEN** el sistema lanza un error de configuración y no intenta conectarse

### Requirement: RF-02 Conexión y verificación
El sistema SHALL conectarse a Atlas con el tiempo de espera configurado y SHALL verificar la disponibilidad antes de operar sobre las colecciones.

#### Scenario: Verificación correcta
- **WHEN** la URI es válida y el cluster responde dentro de `MONGODB_TIMEOUT_MS`
- **THEN** la verificación informa que la conexión está disponible

#### Scenario: Cluster inalcanzable
- **WHEN** el cluster no responde dentro del tiempo de espera configurado
- **THEN** el sistema lanza `MongoConnectionError` de red sin incluir la URI en el mensaje

### Requirement: RF-03 Clasificación de errores de conexión
El sistema SHALL distinguir los fallos de configuración, autenticación, permisos y red mediante subtipos de `MongoConnectionError`.

#### Scenario: Credenciales rechazadas
- **WHEN** Atlas rechaza la autenticación
- **THEN** el sistema lanza el subtipo de autenticación de `MongoConnectionError`

#### Scenario: Permisos insuficientes
- **WHEN** el usuario de Atlas carece de permisos sobre la base o las colecciones
- **THEN** el sistema lanza el subtipo de permisos de `MongoConnectionError`

### Requirement: RF-04 Comprobación ejecutable de conexión
El sistema SHALL ofrecer una comprobación desde línea de comandos que informe el estado de la conexión sin imprimir credenciales.

#### Scenario: Comprobación correcta
- **WHEN** se ejecuta la comprobación con una configuración válida
- **THEN** se informa que la conexión a la base configurada es correcta

#### Scenario: Comprobación fallida
- **WHEN** se ejecuta la comprobación con una URI inválida
- **THEN** se informa el subtipo de error y no se muestra la URI

### Requirement: RNF-01 Protección de secretos
El sistema SHALL impedir que la URI y cualquier credencial aparezcan en mensajes, registros o archivos versionados.

#### Scenario: Mensaje de error
- **WHEN** falla una operación de conexión
- **THEN** el mensaje expuesto no contiene usuario, contraseña ni URI completa

#### Scenario: Archivo de ejemplo
- **WHEN** se versiona la plantilla de entorno
- **THEN** el valor de la URI es únicamente `REEMPLAZAR_POR_URI_DE_ATLAS`
