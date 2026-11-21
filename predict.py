"""Wrapper de la predicción (la lógica vive en ml/predictor.py)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts.predict import main

if __name__ == "__main__":
    sys.exit(main())
