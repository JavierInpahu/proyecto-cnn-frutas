"""Conexión con MongoDB Atlas y clasificación de errores de infraestructura."""

from __future__ import annotations

from typing import Any

import pymongo
from pymongo.collection import Collection

from backend.config.settings import Settings
from backend.models.exceptions import (
    MongoAuthenticationError,
    MongoConnectionError,
    MongoConfigurationError,
    MongoNetworkError,
    MongoPermissionError,
)


class MongoConnection:
    """Gestiona el cliente de PyMongo y el acceso a las colecciones."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Any = None
        self._database: Any = None

    def connect(self) -> None:
        """Establece la conexión y verifica que el cluster responde."""
        if self._client is not None:
            return
        try:
            self._client = pymongo.MongoClient(
                self.settings.mongodb_uri,
                serverSelectionTimeoutMS=self.settings.timeout_ms,
            )
            self._client.admin.command("ping")
            self._database = self._client[self.settings.database]
        except pymongo.errors.ConfigurationError as exc:
            raise MongoConfigurationError(str(exc)) from exc
        except pymongo.errors.OperationFailure as exc:
            codigo = getattr(exc, "code", None)
            if codigo == 18:
                raise MongoAuthenticationError(str(exc)) from exc
            raise MongoPermissionError(str(exc)) from exc
        except (pymongo.errors.ServerSelectionTimeoutError, pymongo.errors.ConnectionFailure) as exc:
            raise MongoNetworkError(str(exc)) from exc
        except pymongo.errors.PyMongoError as exc:
            raise MongoConnectionError(str(exc)) from exc

    def ping(self) -> bool:
        """Devuelve True si el cluster responde al comando ping."""
        self.connect()
        assert self._client is not None
        self._client.admin.command("ping")
        return True

    def get_collection(self, name: str) -> Collection:
        """Devuelve una colección de la base de datos configurada."""
        self.connect()
        assert self._database is not None
        return self._database[name]

    def close(self) -> None:
        """Cierra el cliente si está abierto."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
