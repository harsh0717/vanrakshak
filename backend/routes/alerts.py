"""VanRakshak AI — Alerts Routes"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/alerts")
async def list_active_alerts():
    """
    GET /api/alerts
    Return all currently active alerts from shared state.
    """
    from main import get_orchestrator
    orch = get_orchestrator()
    raw_alerts = [a for a in orch.shared_state["alerts"] if a.get("is_active", True)]

    approvals_by_alert = {}
    for a in orch.shared_state.get("approvals", []):
        if a.get("approval_id"):
            if a.get("ticket_id"):
                approvals_by_alert[a["ticket_id"]] = a["approval_id"]
            if a.get("incident_id"):
                approvals_by_alert[a["incident_id"]] = a["approval_id"]

    normalized = []
    for al in raw_alerts:
        a_copy = dict(al)
        alt_id = a_copy.get("alert_id") or a_copy.get("id", "ALT000")
        a_copy["id"] = alt_id
        a_copy["alert_id"] = alt_id

        vname = a_copy.get("village_name") or a_copy.get("village") or "Gir Protected Zone"
        a_copy["village"] = vname
        a_copy["village_name"] = vname

        rlevel = a_copy.get("risk_level") or a_copy.get("severity", "MEDIUM")
        a_copy["risk_level"] = rlevel
        a_copy["severity"] = rlevel

        ts = a_copy.get("issued_at") or a_copy.get("timestamp", "")
        a_copy["timestamp"] = ts
        a_copy["issued_at"] = ts

        en = a_copy.get("message_english") or a_copy.get("message_en", "")
        gu = a_copy.get("message_gujarati") or a_copy.get("message_gu", "")
        a_copy["message_en"] = en
        a_copy["message_english"] = en
        a_copy["message_gu"] = gu
        a_copy["message_gujarati"] = gu

        is_approved = bool(a_copy.get("officer_approved", False))
        is_override = bool(a_copy.get("officer_override", False))
        a_copy["officer_approved"] = is_approved
        a_copy["officer_override"] = is_override
        a_copy["pending_review"] = a_copy.get("pending_review", not (is_approved or is_override))

        if not a_copy.get("approval_id"):
            inc_id = a_copy.get("incident_id")
            if inc_id and inc_id in approvals_by_alert:
                a_copy["approval_id"] = approvals_by_alert[inc_id]

        normalized.append(a_copy)

    return {
        "alerts":  normalized,
        "total":   len(normalized),
        "is_demo": True,
    }


@router.post("/alerts/generate")
async def generate_alert(body: dict):
    """
    POST /api/alerts/generate
    Manually trigger alert generation for an incident, sighting, or village.

    Supports:
      - incident_id (str)
      - sighting_id (str) + village_id (str)
    """
    from main import get_orchestrator
    from data.sample_data import get_village_by_id, SAMPLE_SIGHTINGS, SAMPLE_VILLAGES
    import uuid

    orch = get_orchestrator()

    incident_id = body.get("incident_id")
    sighting_id = body.get("sighting_id")
    village_id  = body.get("village_id")

    incident = None
    if incident_id:
        incident = next(
            (i for i in orch.shared_state["incidents"] if i.get("incident_id") == incident_id or i.get("id") == incident_id),
            None,
        )
        if incident:
            village_id = village_id or incident.get("village_id")
            sighting_id = sighting_id or incident.get("sighting_id")

    sighting = None
    if sighting_id:
        sighting = next(
            (s for s in orch.shared_state["sightings"] if s.get("sighting_id") == sighting_id or s.get("id") == sighting_id),
            next((s for s in SAMPLE_SIGHTINGS if s.get("sighting_id") == sighting_id), None),
        )
        if sighting and not village_id:
            village_id = sighting.get("nearest_village_id") or sighting.get("village_id")

    if not village_id:
        village_id = "VLG001"

    village = get_village_by_id(village_id)
    if village is None:
        village = SAMPLE_VILLAGES[0]

    species = "Asiatic Lion"
    if incident:
        species = incident.get("species", species)
    elif sighting:
        species = sighting.get("species", species)
    elif body.get("species"):
        species = body["species"]

    if sighting is None:
        sighting = {
            "sighting_id": f"SGT-GEN-{uuid.uuid4().hex[:6].upper()}",
            "species": species,
            "lat": village.get("lat", 21.12),
            "lon": village.get("lon", 70.55),
            "count": 1,
            "source": "manual_trigger",
            "nearest_village_id": village_id,
        }

    # Run movement assessment to calculate dynamic risk
    assessment = orch.agents["movement"].analyze(
        sighting_data=sighting,
        village_id=village_id,
    )

    alert = orch.agents["alert"].generate_alert(
        risk_assessment=assessment,
        village=village,
        species=species,
    )

    alert["incident_id"] = incident_id or (incident.get("incident_id") if incident else None)
    alert["id"] = alert["alert_id"]
    alert["village"] = village["name"]
    alert["risk_level"] = alert.get("severity", "MEDIUM")
    alert["message_en"] = alert.get("message_english", "")
    alert["message_gu"] = alert.get("message_gujarati", "")
    alert["timestamp"] = alert.get("issued_at")
    alert["officer_approved"] = False
    alert["officer_override"] = False
    alert["pending_review"] = True

    # Link or generate approval
    approval = orch._create_pending_approval(
        ticket_id=alert["alert_id"],
        incident_id=alert["incident_id"] or alert["alert_id"],
        sighting_id=sighting.get("sighting_id", "SGT-MANUAL"),
        risk_level=alert["risk_level"],
    )
    orch.shared_state["approvals"].append(approval)
    alert["approval_id"] = approval["approval_id"]

    orch.shared_state["alerts"].insert(0, alert)
    return alert
