"""Pruebas unitarias de la configuración centralizada (sin red)."""

from __future__ import annotations

import pytest

from backend.config.settings import Settings
from backend.models.exceptions import MongoConfigurationError, ValidationError


def test_configuracion_valida_carga_valores_de_entorno() -> None:
    env = {
        "MONGODB_URI": "mongodb+srv://usuario:password@cluster.example.net/test?tls=true",
        "MONGODB_DATABASE": "DB_Frutas_Inpahu_test",
        "MONGODB_FRUITS_COLLECTION": "fruits",
        "MONGODB_PREDICTIONS_COLLECTION": "predictions",
        "MONGODB_TIMEOUT_MS": "5000",
        "MODEL_PATH": "modelo_frutas.keras",
    }
    settings = Settings.from_env(env)
    assert settings.database == "DB_Frutas_Inpahu_test"
    assert settings.timeout_ms == 5000
    assert settings.model_path == "modelo_frutas.keras"
    settings.validate()


def test_uri_marcador_lanza_error_de_configuracion_sin_conectar() -> None:
    env = {"MONGODB_URI": "REEMPLAZAR_POR_URI_DE_ATLAS"}
    with pytest.raises(MongoConfigurationError):
        Settings.from_env(env)


def test_uri_vacia_lanza_error_de_configuracion() -> None:
    env = {"MONGODB_URI": ""}
    with pytest.raises(MongoConfigurationError):
        Settings.from_env(env)


def test_timeout_invalido_lanza_error_de_validacion() -> None:
    env = {"MONGODB_URI": "mongodb://localhost:27017", "MONGODB_TIMEOUT_MS": "abc"}
    with pytest.raises(ValidationError):
        Settings.from_env(env)


def test_validate_rechaza_rutas_vacias() -> None:
    env = {
        "MONGODB_URI": "mongodb://localhost:27017",
        "MODEL_PATH": "",
    }
    settings = Settings.from_env(env)
    with pytest.raises(ValidationError):
        settings.validate()
