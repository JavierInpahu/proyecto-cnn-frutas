"""Repositorio de historial de predicciones sobre la colección inyectada."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from backend.models.exceptions import NotFoundError, ValidationError
from backend.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, collection) -> None:
        self.collection = collection

    def create(self, prediction: Prediction) -> Prediction:
        prediction.validate()
        resultado = self.collection.insert_one(prediction.to_document())
        prediction.id = resultado.inserted_id
        return prediction

    def list_sorted(
        self,
        fruit: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Prediction]:
        filtro: dict = {}
        if fruit:
            filtro["fruit_name"] = fruit
        if date_from is not None or date_to is not None:
            filtro_fecha: dict = {}
            if date_from is not None:
                filtro_fecha["$gte"] = date_from
            if date_to is not None:
                filtro_fecha["$lte"] = date_to
            filtro["created_at"] = filtro_fecha
        documentos = self.collection.find(filtro).sort("created_at", -1)
        return [Prediction.from_document(documento) for documento in documentos]

    def get_by_id(self, identificador: ObjectId) -> Prediction:
        documento = self.collection.find_one({"_id": identificador})
        if documento is None:
            raise NotFoundError("predicción", identificador)
        return Prediction.from_document(documento)

    def update_fruit_name(self, identificador: ObjectId, nuevo_nombre: str) -> Prediction:
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValidationError("El nombre de la fruta no puede estar vacío.")
        prediction = self.get_by_id(identificador)
        prediction.change_fruit_name(nuevo_nombre)
        self.collection.replace_one({"_id": identificador}, prediction.to_document())
        return prediction

    def delete(self, identificador: ObjectId, confirmar: bool = False) -> None:
        if not confirmar:
            raise TypeError("La eliminación requiere confirmación explícita.")
        resultado = self.collection.delete_one({"_id": identificador})
        if resultado.deleted_count == 0:
            raise NotFoundError("predicción", identificador)
