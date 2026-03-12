"""FastAPI entrypoint for the SDS2 AI Copilot MVP."""

from __future__ import annotations
from schemas import
from copy import deepcopy
from fastapi import FastAPI, HTTPException, BackgroundTasks

from .audit import append_event, get_event, list_events, new_event_id
from .models import (
    ApplyRequest,
    ApplyResult,
    AuditEvent,
    ChangeProposal,
    ClashReport,
    ErrorResponse,
    EstimateResult,
    ModelData,
    RollbackRequest,
    now_utc,
)
from .rules import apply_changes_to_model, detect_clashes, estimate_project, propose_changes
from .storage import load_model, save_model

app = FastAPI(title="SDS2 AI Copilot MVP", version="0.1.0")
async def run_analysis_in_background(model: ModelData, task_type: str, event_id: str):
    # यह फंक्शन चुपचाप पीछे काम करेगा
    if task_type == "clash":
        result = detect_clashes(model) # rules.py वाला फंक्शन
    elif task_type == "estimate":
        result = estimate_project(model)
    
    # काम खत्म होने पर हम इसे Audit में सेव कर देंगे
    # append_event(result) 
    print(f"Task {task_type} for {event_id} is finished! - main.py:34")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/model", response_model=ModelData)
def get_model() -> ModelData:
    return load_model()


@app.post("/analyze/estimate")
async def analyze_estimate(model: ModelData, background_tasks: BackgroundTasks):
    if not model.members:
        raise HTTPException(status_code=400, detail="Model contains no members")
    
    event_id = new_event_id()
    background_tasks.add_task(estimate_project, model)
    
    return {"message": "Estimation started", "event_id": event_id}


@app.post("/analyze/clashes")
async def analyze_clashes(model: ModelData, background_tasks: BackgroundTasks):
    if not model.members:
        raise HTTPException(status_code=400, detail="Model contains no members")
    
    event_id = new_event_id() # आपने पहले से इसे इम्पोर्ट किया हुआ है
    
    # काम को बैकग्राउंड में भेजें
    background_tasks.add_task(detect_clashes, model) 
    
    return {
        "message": "Clash analysis started",
        "event_id": event_id
    }


@app.post("/changes/propose", response_model=ChangeProposal, responses={400: {"model": ErrorResponse}})
def changes_propose(model: ModelData) -> ChangeProposal:
    if not model.members:
        raise HTTPException(status_code=400, detail="Model contains no members")
    suggestions = propose_changes(model)
    return ChangeProposal(project_id=model.project_id, revision=model.revision, suggested_changes=suggestions)


@app.post("/changes/apply", response_model=ApplyResult, responses={400: {"model": ErrorResponse}})
def changes_apply(req: ApplyRequest) -> ApplyResult:
    if req.approval_token.strip().upper() != "APPROVED":
        raise HTTPException(status_code=400, detail="approval_token must be 'APPROVED'")

    before = deepcopy(req.model)
    proposals = propose_changes(req.model)

    selected = set(req.selected_change_ids)
    known_ids = {item.change_id for item in proposals}
    unknown_ids = sorted(selected - known_ids)
    if unknown_ids:
        raise HTTPException(status_code=400, detail=f"Unknown change IDs: {', '.join(unknown_ids)}")

    after = apply_changes_to_model(deepcopy(req.model), selected, proposals)
    save_model(after)

    event = AuditEvent(
        event_id=new_event_id(),
        timestamp_utc=now_utc(),
        action="apply",
        project_id=req.model.project_id,
        revision=req.model.revision,
        before_snapshot=before,
        after_snapshot=after,
        metadata={"selected_change_ids": sorted(selected)},
    )
    append_event(event)

    return ApplyResult(
        event_id=event.event_id,
        project_id=req.model.project_id,
        revision=req.model.revision,
        applied_change_ids=sorted(selected),
        message="Changes applied and audit event recorded.",
    )


@app.post("/changes/rollback", response_model=ApplyResult, responses={404: {"model": ErrorResponse}})
def changes_rollback(req: RollbackRequest) -> ApplyResult:
    event = get_event(req.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    save_model(event.before_snapshot)

    rollback_event = AuditEvent(
        event_id=new_event_id(),
        timestamp_utc=now_utc(),
        action="rollback",
        project_id=event.project_id,
        revision=event.revision,
        before_snapshot=event.after_snapshot,
        after_snapshot=event.before_snapshot,
        metadata={"reverted_event_id": event.event_id},
    )
    append_event(rollback_event)

    return ApplyResult(
        event_id=rollback_event.event_id,
        project_id=event.project_id,
        revision=event.revision,
        applied_change_ids=[],
        message=f"Rollback completed for {event.event_id}.",
    )


@app.get("/audit/events", response_model=list[AuditEvent])
def audit_events(limit: int = 50) -> list[AuditEvent]:
    return list_events(limit=limit)
@app.post("/apply")
def apply(request: ApplyRequest):
    return {
        "status": "success",
        "data": request
    }

