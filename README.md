# SDS2 AI Copilot MVP

This project is a starter implementation of an AI copilot architecture for SDS2:

- Read-only analysis first
- Human approval before write actions
- Full audit trail with rollback support

## What This MVP Includes

- `FastAPI` service for analysis + change workflow
- Deterministic estimator and clash detector (placeholder logic)
- Approval-gated apply endpoint
- JSON audit log with before/after snapshots
- Rollback endpoint
- SDS2 integration stubs (`export_model.py`, `apply_changes.py`)

## Project Layout

```text
sds2-ai-copilot/
  app/
    audit.py
    main.py
    models.py
    rules.py
    storage.py
  data/
    sample_model.json
  sds2_adapter/
    apply_changes.py
    export_model.py
  tests/
    test_api.py
  requirements.txt
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run API:

```bash
uvicorn app.main:app --reload --port 8000
```

4. Open docs:

- `http://localhost:8000/docs`

## Core API Endpoints

- `GET /health`
- `POST /analyze/estimate`
- `POST /analyze/clashes`
- `POST /changes/propose`
- `POST /changes/apply`
- `POST /changes/rollback`
- `GET /audit/events`

## SDS2 Integration Flow (Target)

1. SDS2 plugin/script exports model data to JSON.
2. JSON is sent to this AI service for analysis and recommendations.
3. Engineer reviews recommendations.
4. Approved changes are applied through SDS2 write API calls.
5. Every apply action is logged for traceability and rollback.

## Important Notes

- The SDS2 calls are stubbed in this MVP because real SDS2 API runtime is not available in this workspace.
- Replace placeholder sections in `sds2_adapter/` with real SDS2 Python/.NET API calls in your environment.
- Keep final engineering authority with deterministic checks and human approval.
