"""VanRakshak AI — Compensation Routes"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


def _normalize_claim(claim: dict) -> dict:
    from data.sample_data import SAMPLE_VILLAGES
    village_map = {v["village_id"]: v["name"] for v in SAMPLE_VILLAGES}
    c = dict(claim)
    c_name = c.get("claimant_name") or c.get("villager_name") or "Citizen Claimant"
    c["claimant_name"] = c_name
    c["villager_name"] = c_name

    vid = c.get("claimant_village_id") or c.get("village_id") or c.get("village") or "VLG001"
    vname = village_map.get(vid, vid)
    c["claimant_village_id"] = vid
    c["village_id"] = vid
    c["village"] = vname

    cnt = c.get("contact_number") or c.get("contact") or "N/A"
    c["contact_number"] = cnt
    c["contact"] = cnt

    ldesc = c.get("loss_description") or c.get("loss_details") or "Conflict damages"
    c["loss_description"] = ldesc
    c["loss_details"] = ldesc

    eval_val = c.get("estimated_loss_value") or c.get("estimated_value")
    c["estimated_loss_value"] = eval_val
    c["estimated_value"] = eval_val

    c["officer_review_status"] = c.get("officer_review_status", "PENDING_VERIFICATION")
    c["documents_checklist"] = c.get("document_checklist") or c.get("documents_checklist", [])
    c["document_checklist"] = c["documents_checklist"]
    c["is_demo"] = True
    return c


@router.post("/compensation/start")
async def start_claim(body: dict):
    """
    POST /api/compensation/start
    Initiate a livestock/crop compensation claim draft.
    Accepts both snake_case and frontend field formats.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    incident_id = body.get("incident_id")
    if not incident_id:
        raise HTTPException(status_code=422, detail="Missing required field: incident_id")

    # Find matching incident if possible
    inc = next((i for i in orch.shared_state["incidents"] if i.get("incident_id") == incident_id or i.get("id") == incident_id), None)

    claimant_name = body.get("claimant_name") or body.get("villager_name")
    if not claimant_name:
        claimant_name = "Anonymous Resident"

    village_id = (
        body.get("claimant_village_id")
        or body.get("village")
        or body.get("village_id")
        or (inc.get("village_id") if inc else "VLG001")
    )

    loss_type = (body.get("loss_type") or (inc.get("type") if inc else "livestock_predation")).lower()
    if loss_type == "livestock_predation":
        canonical_loss_type = "livestock_predation"
    elif "crop" in loss_type:
        canonical_loss_type = "crop_damage"
    elif "injury" in loss_type:
        canonical_loss_type = "human_injury"
    elif "property" in loss_type:
        canonical_loss_type = "property_damage"
    else:
        canonical_loss_type = "livestock_predation"

    loss_description = (
        body.get("loss_description")
        or body.get("loss_details")
        or (inc.get("losses") if inc else "Conflict loss reported by resident")
    )
    contact_number = body.get("contact_number") or body.get("contact") or "+91-98765-00000"
    estimated_loss = body.get("estimated_loss_value") or body.get("estimated_value")

    claim = orch.agents["compensation"].start_claim(
        incident_id=incident_id,
        villager_info={
            "claimant_name":  claimant_name,
            "village_id":     village_id,
            "contact_number": contact_number,
        },
        loss_details={
            "loss_type":             canonical_loss_type,
            "loss_description":      loss_description,
            "species_responsible":   body.get("species_responsible", inc.get("species", "Unknown") if inc else "Unknown"),
            "estimated_loss_value":  float(estimated_loss) if estimated_loss else None,
        },
    )

    normalized = _normalize_claim(claim)
    orch.shared_state["claims"].append(normalized)
    return normalized


@router.get("/compensation/{claim_id}")
async def get_claim(claim_id: str):
    """
    GET /api/compensation/{claim_id}
    Retrieve a specific compensation claim draft.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    # Check shared_state first
    claim = next((c for c in orch.shared_state["claims"] if c.get("claim_id") == claim_id), None)
    if claim is None:
        claim = orch.agents["compensation"].get_claim(claim_id)

    if claim is None:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")

    return _normalize_claim(claim)


@router.get("/compensation/checklist/{loss_type}")
async def get_checklist(loss_type: str):
    """
    GET /api/compensation/checklist/{loss_type}
    Return the required document checklist for a given loss type.
    """
    from main import get_orchestrator
    orch = get_orchestrator()

    norm_type = loss_type.lower()
    if "crop" in norm_type:
        norm_type = "crop_damage"
    elif "injury" in norm_type:
        norm_type = "human_injury"
    elif "property" in norm_type:
        norm_type = "property_damage"
    else:
        norm_type = "livestock_predation"

    checklist = orch.agents["compensation"].get_document_checklist(norm_type)
    return {
        "loss_type": loss_type,
        "canonical_loss_type": norm_type,
        "checklist": checklist,
        "required_documents": checklist,
        "optional_documents": [
            "Camera trap footage (if available)",
            "Village head (Sarpanch) letter of attestation",
        ],
        "notes": "All claims must be filed within 30 days of the incident. Final approval rests with authorized Forest Department officer.",
        "count":     len(checklist),
        "is_demo":   True,
    }
