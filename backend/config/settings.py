"""Configuración centralizada leída de variables de entorno."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from dotenv import load_dotenv

from backend.models.exceptions import MongoConfigurationError, ValidationError

MARCADOR_EJEMPLO = "REEMPLAZAR_POR_URI_DE_ATLAS"

DEFAULT_TIMEOUT_MS = 8000
DEFAULT_DATABASE = "DB_Frutas_Inpahu"
DEFAULT_FRUITS_COLLECTION = "fruits"
DEFAULT_PREDICTIONS_COLLECTION = "predictions"
DEFAULT_MODEL_PATH = "modelo_frutas.keras"
DEFAULT_MANIFEST_PATH = "ml/class_manifest.json"


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str
    database: str
    fruits_collection: str
    predictions_collection: str
    timeout_ms: int
    model_path: str
    manifest_path: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        """Lee la configuración del entorno y rechaza el marcador sin reemplazar."""
        if env is None:
            load_dotenv()  # carga .env si existe, sin exponer credenciales
            env = os.environ

        def _valor(clave: str, default: str) -> str:
            if clave in env:
                return env[clave]
            return default

        mongodb_uri = (env.get("MONGODB_URI") or "").strip()
        if not mongodb_uri or mongodb_uri == MARCADOR_EJEMPLO:
            raise MongoConfigurationError(
                "La URI de MongoDB no está configurada. Reemplace "
                "REEMPLAZAR_POR_URI_DE_ATLAS en el archivo .env (nunca versionado)."
            )

        database = _valor("MONGODB_DATABASE", DEFAULT_DATABASE)
        fruits_collection = _valor("MONGODB_FRUITS_COLLECTION", DEFAULT_FRUITS_COLLECTION)
        predictions_collection = _valor(
            "MONGODB_PREDICTIONS_COLLECTION", DEFAULT_PREDICTIONS_COLLECTION
        )

        timeout_raw = env.get("MONGODB_TIMEOUT_MS")
        try:
            timeout_ms = int(timeout_raw) if timeout_raw is not None else DEFAULT_TIMEOUT_MS
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"MONGODB_TIMEOUT_MS debe ser un número entero: {exc}"
            ) from exc
        if timeout_ms <= 0:
            raise ValidationError("MONGODB_TIMEOUT_MS debe ser mayor que cero.")

        model_path = _valor("MODEL_PATH", DEFAULT_MODEL_PATH)
        manifest_path = _valor("MANIFEST_PATH", DEFAULT_MANIFEST_PATH)

        return cls(
            mongodb_uri=mongodb_uri,
            database=database,
            fruits_collection=fruits_collection,
            predictions_collection=predictions_collection,
            timeout_ms=timeout_ms,
            model_path=model_path,
            manifest_path=manifest_path,
        )

    def validate(self) -> None:
        """Valida que los valores actuales sean consistentes."""
        if not self.model_path:
            raise ValidationError("MODEL_PATH no puede estar vacío.")
        if not self.manifest_path:
            raise ValidationError("MANIFEST_PATH no puede estar vacío.")
        if not self.database or not self.fruits_collection or not self.predictions_collection:
            raise ValidationError("Faltan nombres de base de datos o colecciones.")
