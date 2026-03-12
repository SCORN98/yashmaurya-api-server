"""SDS2 export adapter stub.

Replace placeholders with real SDS2 Python API calls in your SDS2 runtime.
"""

from __future__ import annotations

import json
from pathlib import Path


def export_model_to_json(output_path: str) -> None:
    # TODO: Replace this with real SDS2 model extraction.
    model = {
        "project_id": "SDS2-DEMO-001",
        "revision": "A",
        "members": [
            {
                "member_id": "C1",
                "type": "column",
                "material": "Steel A36",
                "length_mm": 4200,
                "weight_kg": 280,
                "start": {"x": 0, "y": 0, "z": 0},
                "end": {"x": 0, "y": 0, "z": 4200},
            },
            {
                "member_id": "B1",
                "type": "beam",
                "material": "Steel A572",
                "length_mm": 6000,
                "weight_kg": 190,
                "start": {"x": 50, "y": 0, "z": 4000},
                "end": {"x": 6050, "y": 0, "z": 4000},
            },
            {
                "member_id": "BR1",
                "type": "brace",
                "material": "FRP",
                "length_mm": 3200,
                "weight_kg": 60,
                "start": {"x": 100, "y": 100, "z": 0},
                "end": {"x": 1800, "y": 1100, "z": 2200},
            },
        ],
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(model, indent=2), encoding="utf-8")


if __name__ == "__main__":
    export_model_to_json(str(Path(__file__).resolve().parent.parent / "data" / "sample_model.json"))
    print("Sample export written to data/sample_model.json")
