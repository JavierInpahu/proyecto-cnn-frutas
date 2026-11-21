"""Predicción única: mismo preprocesamiento, mismas clases, umbral de rechazo.

La imagen se convierte a RGB, 100×100, float32 en rango 0-255. **No se divide
entre 255**: el modelo ya contiene ``Rescaling(1./255)``. La función de esta
capa se usa desde la interfaz, desde ClassificationService y desde scripts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from backend.models.exceptions import ModelMismatchError
from ml import config
from ml.class_indices import load_indices, validate_with_manifest
from ml.ood import rechazo_por_distancia, rechazo_por_estructura


@dataclass(frozen=True)
class PredictionOutcome:
    top_index: int
    fruit_name: str
    confidence: float  # porcentaje 0-100
    probabilities: List[float]
    class_names: List[str]
    rejected: bool
    reason: str | None


def predict(
    model_loader,
    image_processor,
    archivo: Any,
    manifest: List[str] | None = None,
    threshold: float | None = None,
    indices_path: str | Path | None = None,
) -> PredictionOutcome:
    """Clasifica un archivo/imagen y aplica rechazo por baja confianza."""
    model_loader.validate_compatibility()
    entrada = image_processor.process(archivo)
    modelo = model_loader.get_model()
    prediccion = modelo.predict(entrada, verbose=0)[0]
    vector = [float(valor) for valor in prediccion]
    indice = max(range(len(vector)), key=vector.__getitem__)
    nombres = list(manifest or model_loader.class_names())

    camino_indices = Path(indices_path or getattr(model_loader, "manifest_path", config.MANIFEST_PATH))
    camino_indices = camino_indices.parent / "class_indices.json"
    if camino_indices.exists():
        indices = load_indices(camino_indices)
        validate_with_manifest(indices, getattr(model_loader, "manifest_path", config.MANIFEST_PATH))
        if indices.classes != nombres:
            raise ModelMismatchError(
                "Las clases del archivo de índices no coinciden con el manifiesto usado por la app."
            )
        umbral = indices.confidence_threshold if threshold is None else threshold
    else:
        umbral = config.DEFAULT_CONFIDENCE_THRESHOLD if threshold is None else threshold

    confianza = vector[indice]
    margen = confianza - sorted(vector)[-2] if len(vector) > 1 else confianza
    motivos: list[str] = []
    if confianza < umbral or margen < config.MIN_CONFIDENCE_MARGIN:
        motivos.append("La imagen no coincide con ninguna de las frutas entrenadas.")
    if hasattr(modelo, "get_layer"):  # solo modelos Keras reales tienen umbrales calibrados
        motivo = rechazo_por_estructura(entrada)
        if motivo:
            motivos.append(motivo)
    motivo = rechazo_por_distancia(
        modelo, entrada, camino_indices.parent / config.PROTOTYPES_PATH.name
    )
    if motivo:
        motivos.append(motivo)
    rechazado = bool(motivos)
    razon = " ".join(motivos) if motivos else None

    if rechazado:
        # No hay clase coincidente: no se devuelve ningún porcentaje ni nombre de fruta.
        return PredictionOutcome(
            top_index=-1,
            fruit_name="No reconocido",
            confidence=0.0,
            probabilities=[],
            class_names=nombres,
            rejected=True,
            reason=razon,
        )

    return PredictionOutcome(
        top_index=indice,
        fruit_name=nombres[indice],
        confidence=confianza * 100,
        probabilities=vector,
        class_names=nombres,
        rejected=rechazado,
        reason=razon,
    )


class FruitPredictor:
    """Fachada reutilizable para la app y los scripts de línea de comandos."""

    def __init__(
        self,
        model_loader,
        image_processor,
        indices_path: str | Path = config.INDICES_PATH,
        threshold: float | None = None,
    ) -> None:
        self.model_loader = model_loader
        self.image_processor = image_processor
        self.indices_path = Path(indices_path)
        self.threshold = threshold

    def predict(self, archivo: Any) -> PredictionOutcome:
        return predict(
            self.model_loader,
            self.image_processor,
            archivo,
            threshold=self.threshold,
            indices_path=self.indices_path,
        )
