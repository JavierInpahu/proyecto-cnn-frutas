"""Pruebas unitarias de FruitService con doble de repositorio (sin red)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.models.exceptions import DuplicateFruitError, NotFoundError
from backend.models.fruit import Fruit
from backend.services.fruit_service import FruitService
from ml.class_manifest import ClaseEntrenada


def _repositorio_doble() -> SimpleNamespace:
    almacenados = []

    def crear(fruta):
        fruta.id = "id-falsa"
        almacenados.append(fruta)
        return fruta

    def listar(active_only=False):
        return [f for f in almacenados if not active_only or f.active]

    def obtener(identificador):
        for f in almacenados:
            if f.id == identificador:
                return f
        raise NotFoundError("fruta", identificador)

    return SimpleNamespace(create=crear, list_all=listar, get_by_id=obtener, update=lambda f: f, set_active=lambda i, a: None, delete=lambda i, confirmar=False: None, seed_from_manifest=lambda clases: 0)


def test_servicio_usa_manifiesto_en_siembra(monkeypatch: pytest.MonkeyPatch) -> None:
    llamadas = []

    def seed(clases):
        llamadas.append(clases)
        return len(clases)

    repo = _repositorio_doble()
    repo.seed_from_manifest = seed
    servicio = FruitService(
        repository=repo,
        manifest=[ClaseEntrenada(name="Banana 1", scientific_name="Musa acuminata", description="d")],
    )
    assert servicio.seed_catalog() == 1
    assert llamadas[0][0].name == "Banana 1"


def test_crear_propaga_error_de_duplicado() -> None:
    def crear(fruta):
        raise DuplicateFruitError(fruta.name)

    servicio = FruitService(repository=SimpleNamespace(create=crear, list_all=lambda active_only=False: [], get_by_id=lambda i: None, update=lambda f: f, set_active=lambda i, a: None, delete=lambda i, confirmar=False: None))
    with pytest.raises(DuplicateFruitError):
        servicio.create("Banana 1", "Musa acuminata", "d")
