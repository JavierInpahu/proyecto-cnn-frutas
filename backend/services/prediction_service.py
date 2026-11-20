"""Servicio de historial de predicciones con filtros combinables."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from backend.models.exceptions import NotFoundError, ValidationError
from backend.models.prediction import Prediction


class PredictionService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def register(self, fruit_name: str, confidence: float, image_name: str) -> Prediction:
        prediccion = Prediction(
            fruit_name=fruit_name,
            confidence=confidence,
            image_name=image_name,
        )
        return self.repository.create(prediccion)

    def list(
        self,
        fruit: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Prediction]:
        return self.repository.list_sorted(fruit=fruit, date_from=date_from, date_to=date_to)

    def get(self, identificador: ObjectId) -> Prediction:
        return self.repository.get_by_id(identificador)

    def correct_fruit_name(self, identificador: ObjectId, nuevo_nombre: str) -> Prediction:
        return self.repository.update_fruit_name(identificador, nuevo_nombre)

    def delete(self, identificador: ObjectId, confirmar: bool = False) -> None:
        self.repository.delete(identificador, confirmar=confirmar)
