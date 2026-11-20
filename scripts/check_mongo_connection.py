"""Comprobación de conexión con MongoDB Atlas desde línea de comandos.

Lee la configuración de variables de entorno, verifica la conexión e informa
el estado sin mostrar nunca la URI ni credenciales.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config.settings import MongoConfigurationError, Settings
from backend.database.mongo_connection import MongoConnection
from backend.models.exceptions import (
    MongoAuthenticationError,
    MongoConnectionError,
    MongoNetworkError,
    MongoPermissionError,
)


def main() -> int:
    try:
        settings = Settings.from_env()
        connection = MongoConnection(settings)
        connection.ping()
        connection.close()
        print(
            f"Conexión a MongoDB Atlas correcta (base de datos: {settings.database})."
        )
        return 0
    except MongoConfigurationError as exc:
        print(f"Error de configuración: {exc}", file=sys.stderr)
        return 2
    except MongoAuthenticationError as exc:
        print(f"Error de autenticación contra Atlas: {exc}", file=sys.stderr)
        return 3
    except MongoPermissionError as exc:
        print(f"Error de permisos en Atlas: {exc}", file=sys.stderr)
        return 4
    except MongoNetworkError as exc:
        print(f"Error de red alcanzando Atlas: {exc}", file=sys.stderr)
        return 5
    except MongoConnectionError as exc:
        print(f"Error de conexión con MongoDB: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensa del script de comprobación
        print(f"Error inesperado verificando la conexión: {type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
