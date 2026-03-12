"""SDS2 apply adapter stub.

Replace placeholders with real SDS2 write API calls in your SDS2 runtime.
"""

from __future__ import annotations

import json
from pathlib import Path


def apply_changes_from_json(changes_path: str) -> None:
    path = Path(changes_path)
    if not path.exists():
        raise FileNotFoundError(f"Change file does not exist: {changes_path}")

    payload = json.loads(path.read_text(encoding="utf-8"))

    # TODO: Replace this block with actual SDS2 write operations.
    for change in payload.get("suggested_changes", []):
        print(
            "Applying",
            change.get("change_id"),
            "to member",
            change.get("member_id"),
            "action",
            change.get("action"),
        )


if __name__ == "__main__":
    demo = Path(__file__).resolve().parent.parent / "data" / "pending_changes.json"
    if demo.exists():
        apply_changes_from_json(str(demo))
    else:
        print("No pending_changes.json found. Create one from /changes/propose output.")
