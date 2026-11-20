"""Pruebas unitarias de MongoConnection con dobles (sin red)."""

from __future__ import annotations

from types import SimpleNamespace

import pymongo.errors
import pytest

from backend.config.settings import Settings
from backend.database.mongo_connection import MongoConnection
from backend.models.exceptions import (
    MongoAuthenticationError,
    MongoConnectionError,
    MongoNetworkError,
    MongoPermissionError,
)


def _settings() -> Settings:
    return Settings.from_env({"MONGODB_URI": "mongodb://localhost:27017"})


class _BaseDatosFalso:
    def __init__(self, comportamiento: str) -> None:
        if comportamiento == "ok":
            self._command = lambda nombre: {"ok": 1}
        elif comportamiento == "autenticacion":
            self._command = lambda nombre: (_ for _ in ()).throw(
                pymongo.errors.OperationFailure("Auth failed", code=18)
            )
        elif comportamiento == "permisos":
            self._command = lambda nombre: (_ for _ in ()).throw(
                pymongo.errors.OperationFailure("not authorized", code=13)
            )
        elif comportamiento == "red":
            self._command = lambda nombre: (_ for _ in ()).throw(
                pymongo.errors.ServerSelectionTimeoutError("timeout")
            )
        else:
            raise ValueError(comportamiento)
        self.admin = SimpleNamespace(command=self._command)

    def __getitem__(self, nombre: str):
        return SimpleNamespace(name=nombre)


class _ClienteFalso:
    def __init__(self, comportamiento: str = "ok") -> None:
        self._base = _BaseDatosFalso(comportamiento)
        self.admin = self._base.admin

    def __getitem__(self, nombre: str):
        return self._base

    def close(self) -> None:
        return None


def test_ping_con_cluster_respuesta_devuelve_true(monkeypatch: pytest.MonkeyPatch) -> None:
    import backend.database.mongo_connection as modulo

    monkeypatch.setattr(
        modulo.pymongo, "MongoClient", lambda uri, **kwargs: _ClienteFalso("ok")
    )
    conexion = MongoConnection(_settings())
    assert conexion.ping() is True
    conexion.close()


def test_fallo_autenticacion_lanza_subtipo(monkeypatch: pytest.MonkeyPatch) -> None:
    import backend.database.mongo_connection as modulo

    monkeypatch.setattr(
        modulo.pymongo, "MongoClient", lambda uri, **kwargs: _ClienteFalso("autenticacion")
    )
    conexion = MongoConnection(_settings())
    with pytest.raises(MongoAuthenticationError):
        conexion.ping()


def test_fallo_permisos_lanza_subtipo(monkeypatch: pytest.MonkeyPatch) -> None:
    import backend.database.mongo_connection as modulo

    monkeypatch.setattr(
        modulo.pymongo, "MongoClient", lambda uri, **kwargs: _ClienteFalso("permisos")
    )
    conexion = MongoConnection(_settings())
    with pytest.raises(MongoPermissionError):
        conexion.ping()


def test_fallo_red_lanza_subtipo(monkeypatch: pytest.MonkeyPatch) -> None:
    import backend.database.mongo_connection as modulo

    monkeypatch.setattr(
        modulo.pymongo, "MongoClient", lambda uri, **kwargs: _ClienteFalso("red")
    )
    conexion = MongoConnection(_settings())
    with pytest.raises(MongoNetworkError):
        conexion.ping()


class _BaseParaColeccion:
    def __getitem__(self, clave: str):
        return SimpleNamespace(name="fruits")


class _ClienteParaColeccion:
    def __init__(self) -> None:
        self.admin = SimpleNamespace(command=lambda nombre: {"ok": 1})

    def __getitem__(self, nombre: str):
        return _BaseParaColeccion()

    def close(self) -> None:
        return None


def test_get_collection_devuelve_coleccion(monkeypatch: pytest.MonkeyPatch) -> None:
    import backend.database.mongo_connection as modulo

    monkeypatch.setattr(modulo.pymongo, "MongoClient", lambda uri, **kwargs: _ClienteParaColeccion())
    conexion = MongoConnection(_settings())
    resultado = conexion.get_collection("fruits")
    assert resultado.name == "fruits"
    conexion.close()
