"""VanRakshak AI — Incidents Routes"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/incidents")
async def list_incidents(
    status: Optional[str]  = Query(default=None, description="Filter by status (NEW, ASSIGNED, etc.)"),
    severity: Optional[str] = Query(default=None, description="Filter by severity (HIGH, MEDIUM, LOW)"),
    village_id: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100, ge=1),
):
    """
    GET /api/incidents
    List conflict incidents with optional filters.
    """
    from main import get_orchestrator
    from data.sample_data import SAMPLE_VILLAGES
    orch = get_orchestrator()
    incidents = list(orch.shared_state["incidents"])

    village_map = {v["village_id"]: v["name"] for v in SAMPLE_VILLAGES}
    approvals_by_inc = {}
    for a in orch.shared_state.get("approvals", []):
        if a.get("incident_id"):
            approvals_by_inc[a["incident_id"]] = a.get("approval_id")

    normalized = []
    for inc in incidents:
        inc_copy = dict(inc)
        inc_id = inc_copy.get("incident_id") or inc_copy.get("id", "INC000")
        inc_copy["id"] = inc_id
        inc_copy["incident_id"] = inc_id
        inc_copy["display_id"] = inc_copy.get("display_id") or inc_id

        vid = inc_copy.get("village_id", "")
        vname = inc_copy.get("village") or inc_copy.get("village_name") or village_map.get(vid, vid or "Gir Sector")
        inc_copy["village"] = vname
        inc_copy["village_name"] = vname

        ts = inc_copy.get("timestamp") or inc_copy.get("date", "")
        inc_copy["timestamp"] = ts
        inc_copy["date"] = ts

        if not inc_copy.get("approval_id"):
            inc_copy["approval_id"] = approvals_by_inc.get(inc_id)

        inc_copy.setdefault("severity", inc_copy.get("risk_level", "MEDIUM"))
        inc_copy.setdefault("risk_score", 0.75)
        inc_copy.setdefault("recommended_team", "Gir Rapid Response Alpha")
        inc_copy.setdefault("description", f"Conflict incident near {vname} involving {inc_copy.get('species', 'wildlife')}")
        inc_copy.setdefault("pending_approval", inc_copy.get("status") in ("NEW", "PENDING"))

        normalized.append(inc_copy)

    if status:
        normalized = [i for i in normalized if i.get("status", "").upper() == status.upper()]
    if severity:
        normalized = [i for i in normalized if i.get("severity", "").upper() == severity.upper()]
    if village_id:
        normalized = [i for i in normalized if i.get("village_id") == village_id]

    normalized = sorted(normalized, key=lambda i: i.get("timestamp", ""), reverse=True)
    return {
        "incidents": normalized[:limit],
        "total":     len(normalized),
        "filters":   {"status": status, "severity": severity, "village_id": village_id},
        "is_demo":   True,
    }


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """
    GET /api/incidents/{incident_id}
    Retrieve a single incident by ID.
    """
    from main import get_orchestrator
    from data.sample_data import SAMPLE_VILLAGES
    orch = get_orchestrator()
    incidents = orch.shared_state["incidents"]
    incident = next((i for i in incidents if i.get("incident_id") == incident_id or i.get("id") == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    village_map = {v["village_id"]: v["name"] for v in SAMPLE_VILLAGES}
    inc_copy = dict(incident)
    inc_id = inc_copy.get("incident_id") or inc_copy.get("id", incident_id)
    inc_copy["id"] = inc_id
    inc_copy["incident_id"] = inc_id
    inc_copy["display_id"] = inc_copy.get("display_id") or inc_id

    vid = inc_copy.get("village_id", "")
    vname = inc_copy.get("village") or inc_copy.get("village_name") or village_map.get(vid, vid or "Gir Sector")
    inc_copy["village"] = vname
    inc_copy["village_name"] = vname
    inc_copy["timestamp"] = inc_copy.get("timestamp") or inc_copy.get("date", "")
    inc_copy["date"] = inc_copy["timestamp"]

    if not inc_copy.get("approval_id"):
        match_approval = next((a for a in orch.shared_state.get("approvals", []) if a.get("incident_id") == inc_id), None)
        if match_approval:
            inc_copy["approval_id"] = match_approval.get("approval_id")

    return inc_copy


@router.put("/incidents/{incident_id}/status")
async def update_incident_status(incident_id: str, body: dict):
    """
    PUT /api/incidents/{incident_id}/status
    Update the status of an incident ticket.

    Required body: new_status (str)
    Optional: officer_id (str), notes (str)
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    new_status = body.get("new_status")
    officer_id = body.get("officer_id", "OFFICER_DEMO")
    if not new_status:
        raise HTTPException(
            status_code=422,
            detail="Required field: new_status",
        )

    result = orch.update_incident_status(
        incident_id=incident_id,
        new_status=new_status,
        officer_id=officer_id,
        notes=body.get("notes"),
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/sos")
async def trigger_sos(body: dict):
    """
    POST /api/sos
    Trigger an urgent citizen distress beacon.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    lat = float(body.get("lat") or 21.1242)
    lon = float(body.get("lon") or 70.5521)
    contact = body.get("contact", "Citizen SOS")
    message = body.get("message", "Immediate distress reported by villager")
    village_id = body.get("village_id") or body.get("nearest_village_id") or "VLG001"

    sighting_payload = {
        "species": body.get("species", "Asiatic Lion"),
        "lat": lat,
        "lon": lon,
        "count": int(body.get("count", 1)),
        "source": "villager_report",
        "nearest_village_id": village_id,
        "distance_km": float(body.get("distance_km", 0.5)),
        "notes": f"URGENT CITIZEN SOS: {message} ({contact})",
    }
    workflow_result = orch.process_sighting(sighting_payload)

    return {
        "status": "SOS_BROADCAST",
        "message": "Forest Department Rapid Response Team notified. Stay in a safe, enclosed area.",
        "helplines": {
            "forest_dept_toll_free": "1926",
            "ambulance": "108",
            "sasan_gir_control_room": "02877-285541"
        },
        "workflow": workflow_result,
        "incident_id": workflow_result.get("incident_ticket", {}).get("incident_id"),
        "is_demo": True,
    }
