"""Rule and heuristic layer for analysis and change proposals."""

from __future__ import annotations

from math import dist

from .models import ClashPair, ClashReport, EstimateResult, ModelData, SuggestedChange

STEEL_USD_PER_KG = 2.5
ALUMINUM_USD_PER_KG = 4.2
FRP_USD_PER_KG = 6.8
DEFAULT_USD_PER_KG = 3.0


def estimate_project(model: ModelData) -> EstimateResult:
    total_weight = sum(member.weight_kg for member in model.members)

    cost = 0.0
    for member in model.members:
        material_key = member.material.lower()
        if "steel" in material_key:
            unit = STEEL_USD_PER_KG
        elif "aluminum" in material_key or "aluminium" in material_key:
            unit = ALUMINUM_USD_PER_KG
        elif "frp" in material_key:
            unit = FRP_USD_PER_KG
        else:
            unit = DEFAULT_USD_PER_KG
        cost += member.weight_kg * unit

    assumptions = [
        "Estimator uses material-based static USD/kg multipliers.",
        "No labor, logistics, coating, or regional pricing factors included.",
        "Use as pre-bid directional estimate only.",
    ]

    return EstimateResult(
        project_id=model.project_id,
        revision=model.revision,
        total_weight_kg=round(total_weight, 2),
        estimated_cost_usd=round(cost, 2),
        assumptions=assumptions,
    )


def _segment_midpoint(member) -> tuple[float, float, float]:
    return (
        (member.start.x + member.end.x) / 2,
        (member.start.y + member.end.y) / 2,
        (member.start.z + member.end.z) / 2,
    )


def detect_clashes(model: ModelData) -> ClashReport:
    clashes = []
    members = model.members

    # Simple proxy clash detector using midpoint proximity.
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a = members[i]
            b = members[j]
            d = dist(_segment_midpoint(a), _segment_midpoint(b))
            if d < 120:
                severity = "high"
            elif d < 250:
                severity = "medium"
            elif d < 400:
                severity = "low"
            else:
                continue

            clashes.append(
                ClashPair(member_a=a.member_id, member_b=b.member_id, severity=severity)
            )

    return ClashReport(project_id=model.project_id, revision=model.revision, clashes=clashes)


def propose_changes(model: ModelData) -> list[SuggestedChange]:
    report = detect_clashes(model)
    changes: list[SuggestedChange] = []

    for idx, clash in enumerate(report.clashes, start=1):
        if clash.severity == "high":
            action = "shift_member"
            reason = f"High clash risk between {clash.member_a} and {clash.member_b}."
            payload = {"axis": "x", "delta_mm": 25, "target": clash.member_b}
        elif clash.severity == "medium":
            action = "resize_plate"
            reason = f"Medium clash risk between {clash.member_a} and {clash.member_b}."
            payload = {"target": clash.member_b, "plate_trim_mm": 10}
        else:
            action = "flag_review"
            reason = f"Low clash risk between {clash.member_a} and {clash.member_b}."
            payload = {"target_pair": [clash.member_a, clash.member_b], "review": True}

        changes.append(
            SuggestedChange(
                change_id=f"chg-{idx:04d}",
                member_id=clash.member_b,
                action=action,
                reason=reason,
                payload=payload,
            )
        )

    return changes


def apply_changes_to_model(model: ModelData, selected_change_ids: set[str], proposed: list[SuggestedChange]) -> ModelData:
    by_id = {change.change_id: change for change in proposed if change.change_id in selected_change_ids}

    for member in model.members:
        for change in by_id.values():
            if change.member_id != member.member_id:
                continue

            if change.action == "shift_member":
                delta = float(change.payload.get("delta_mm", 0))
                axis = change.payload.get("axis", "x")
                if axis == "x":
                    member.start.x += delta
                    member.end.x += delta
                elif axis == "y":
                    member.start.y += delta
                    member.end.y += delta
                elif axis == "z":
                    member.start.z += delta
                    member.end.z += delta
            elif change.action == "resize_plate":
                trim = float(change.payload.get("plate_trim_mm", 0))
                member.weight_kg = max(1.0, round(member.weight_kg - (trim * 0.08), 3))
            else:
                # flag_review does not mutate geometry in this MVP.
                pass

    return model
