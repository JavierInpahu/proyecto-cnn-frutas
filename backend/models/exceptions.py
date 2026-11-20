"""Excepciones de dominio del clasificador de frutas.

Todas las excepciones de negocio e infraestructura viven aquí para evitar
dependencias de frameworks y permitir su sustitución con dobles en pruebas.
"""


class ValidationError(Exception):
    """Datos de entrada no válidos para una operación de dominio."""


class DuplicateFruitError(Exception):
    """Se intenta crear o actualizar una fruta con un nombre ya existente."""

    def __init__(self, nombre: str) -> None:
        super().__init__(f"Ya existe una fruta con el nombre '{nombre}'.")
        self.nombre = nombre


class NotFoundError(Exception):
    """El recurso solicitado no existe en la colección."""

    def __init__(self, tipo: str, identificador) -> None:
        super().__init__(f"No se encontró {tipo} con identificador {identificador}.")
        self.tipo = tipo
        self.identificador = identificador


class InvalidImageError(Exception):
    """La imagen cargada no cumple los requisitos de formato o tamaño."""


class ModelMismatchError(Exception):
    """El modelo cargado no es compatible con el manifiesto de clases."""


class MongoConnectionError(Exception):
    """Fallo al conectar o operar contra MongoDB Atlas."""

    def __init__(self, mensaje: str, codigo: str | None = None) -> None:
        super().__init__(mensaje)
        self.codigo = codigo


class MongoConfigurationError(MongoConnectionError):
    """La configuración de conexión no es válida (por ejemplo, URI sin reemplazar)."""


class MongoAuthenticationError(MongoConnectionError):
    """Atlas rechazó la autenticación."""


class MongoPermissionError(MongoConnectionError):
    """El usuario de Atlas no tiene permisos sobre la base o las colecciones."""


class MongoNetworkError(MongoConnectionError):
    """El cluster no respondió dentro del tiempo de espera configurado."""
