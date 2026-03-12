"""Storage helpers for model and local JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from .models import ModelData

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CURRENT_MODEL_FILE = DATA_DIR / "current_model.json"
SAMPLE_MODEL_FILE = DATA_DIR / "sample_model.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_model(model: ModelData) -> None:
    ensure_data_dir()
    CURRENT_MODEL_FILE.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def load_model() -> ModelData:
    ensure_data_dir()
    if CURRENT_MODEL_FILE.exists():
        content = CURRENT_MODEL_FILE.read_text(encoding="utf-8")
        return ModelData.model_validate(json.loads(content))

    content = SAMPLE_MODEL_FILE.read_text(encoding="utf-8")
    model = ModelData.model_validate(json.loads(content))
    save_model(model)
    return model
