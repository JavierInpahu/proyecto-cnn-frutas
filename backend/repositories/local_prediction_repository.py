"""Historial local en JSON, usado cuando MongoDB Atlas no está disponible.

 Conserva la misma interfaz que ``PredictionRepository`` y permite ver la
miniatura de la imagen analizada. Los datos existentes de Atlas no se tocan:
si hay conexión se sigue usando el repositorio de MongoDB.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from backend.models.exceptions import NotFoundError, ValidationError
from backend.models.prediction import Prediction


def _fecha_utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


class LocalPredictionRepository:
    def __init__(self, path: str | Path = "data/history.json") -> None:
        self.path = Path(path)

    def _leer(self) -> List[dict]:
        if not self.path.exists():
            return []
        try:
            datos = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return datos if isinstance(datos, list) else []

    def _escribir(self, documentos: List[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporal = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as archivo:
                json.dump(documentos, archivo, indent=2, ensure_ascii=False)
            os.replace(temporal, self.path)
        finally:
            if os.path.exists(temporal):
                os.remove(temporal)

    def create(self, prediction: Prediction) -> Prediction:
        prediction.validate()
        documentos = self._leer()
        prediction.id = uuid4().hex
        if prediction.created_at is None:
            prediction.created_at = datetime.now(timezone.utc)
        documento = prediction.to_document()
        documento["_id"] = prediction.id
        documento["created_at"] = _fecha_utc(prediction.created_at).isoformat()
        documento["thumbnail"] = prediction.thumbnail
        documento["image_data"] = prediction.image_data
        documento["image_meta"] = prediction.image_meta
        documentos.append(documento)
        self._escribir(documentos)
        return prediction

    def list_sorted(
        self,
        fruit: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Prediction]:
        documentos = self._leer()
        if fruit:
            documentos = [d for d in documentos if d.get("fruit_name") == fruit]
        if date_from is not None or date_to is not None:
            filtrados = []
            for documento in documentos:
                try:
                    fecha = datetime.fromisoformat(documento["created_at"])
                except (KeyError, ValueError):
                    continue
                if date_from is not None:
                    inicio = datetime.combine(
                        date_from if isinstance(date_from, date) else date_from.date(),
                        time.min,
                    )
                    if fecha < _fecha_utc(inicio):
                        continue
                if date_to is not None:
                    fin = datetime.combine(
                        date_to if isinstance(date_to, date) else date_to.date(),
                        time.max,
                    )
                    if fecha > _fecha_utc(fin):
                        continue
                filtrados.append(documento)
            documentos = filtrados

        documentos.sort(key=lambda d: d.get("created_at", ""), reverse=True)
        resultados = []
        for documento in documentos:
            copia = dict(documento)
            try:
                copia["created_at"] = datetime.fromisoformat(documento["created_at"])
            except (KeyError, ValueError):
                copia["created_at"] = datetime.now(timezone.utc)
            resultados.append(Prediction.from_document(copia))
        return resultados

    def _buscar(self, identificador) -> tuple[List[dict], int]:
        documentos = self._leer()
        for indice, documento in enumerate(documentos):
            if str(documento.get("_id")) == str(identificador):
                return documentos, indice
        raise NotFoundError("predicción", identificador)

    def get_by_id(self, identificador) -> Prediction:
        documentos, indice = self._buscar(identificador)
        documento = dict(documentos[indice])
        documento["created_at"] = datetime.fromisoformat(documento["created_at"])
        return Prediction.from_document(documento)

    def update_fruit_name(self, identificador, nuevo_nombre: str) -> Prediction:
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValidationError("El nombre de la fruta no puede estar vacío.")
        documentos, indice = self._buscar(identificador)
        documentos[indice]["fruit_name"] = nuevo_nombre.strip()
        self._escribir(documentos)
        return self.get_by_id(identificador)

    def delete(self, identificador, confirmar: bool = False) -> None:
        if not confirmar:
            raise TypeError("La eliminación requiere confirmación explícita.")
        documentos, indice = self._buscar(identificador)
        documentos.pop(indice)
        self._escribir(documentos)
