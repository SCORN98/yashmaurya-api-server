"""Audit event persistence and retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from .models import AuditEvent

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIT_FILE = BASE_DIR / "data" / "audit_log.jsonl"


def _ensure_parent() -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)


def new_event_id() -> str:
    return f"evt-{uuid4().hex[:12]}"


def append_event(event: AuditEvent) -> None:
    _ensure_parent()
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(event.model_dump_json())
        f.write("\n")


def list_events(limit: int = 50) -> list[AuditEvent]:
    _ensure_parent()
    if not AUDIT_FILE.exists():
        return []

    lines = AUDIT_FILE.read_text(encoding="utf-8").strip().splitlines()
    events = [AuditEvent.model_validate(json.loads(line)) for line in lines if line.strip()]
    return list(reversed(events[-limit:]))


def get_event(event_id: str) -> AuditEvent | None:
    for event in list_events(limit=10000):
        if event.event_id == event_id:
            return event
    return None
