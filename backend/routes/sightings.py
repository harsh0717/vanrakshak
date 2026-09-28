"""VanRakshak AI — Sightings Routes"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/sightings")
async def list_sightings(
    limit: int = Query(default=20, le=100, ge=1),
    species: Optional[str] = Query(default=None),
):
    """
    GET /api/sightings
    Return recent wildlife sightings from shared state.
    Optionally filter by species.
    """
    from main import get_orchestrator
    from data.sample_data import SAMPLE_VILLAGES
    orch = get_orchestrator()
    sightings = list(orch.shared_state["sightings"])

    village_map = {v["village_id"]: v["name"] for v in SAMPLE_VILLAGES}
    normalized = []
    for s in sightings:
        s_copy = dict(s)
        sid = s_copy.get("sighting_id") or s_copy.get("id", "SGT000")
        s_copy["id"] = sid
        s_copy["sighting_id"] = sid

        vid = s_copy.get("nearest_village_id") or s_copy.get("village_id") or ""
        vname = s_copy.get("village") or village_map.get(vid, "Gir Forest Sector")
        s_copy["village"] = vname
        s_copy["location"] = s_copy.get("notes") or s_copy.get("location") or f"Near {vname}"

        dist = s_copy.get("distance_to_nearest_village_km") or s_copy.get("distance_km") or 2.0
        s_copy["distance_km"] = round(float(dist), 1)

        conf = s_copy.get("confidence", 0.85)
        s_copy["confidence"] = round(float(conf), 2)
        s_copy["reported_by"] = s_copy.get("source") or s_copy.get("reported_by") or "villager_report"
        s_copy["verified"] = s_copy.get("verified", s_copy["confidence"] >= 0.7)
        s_copy["risk_level"] = s_copy.get("risk_level", "HIGH" if s_copy["confidence"] >= 0.8 else "MEDIUM")
        normalized.append(s_copy)

    if species:
        normalized = [s for s in normalized if s.get("species", "").lower() == species.lower()]

    # Most recent first
    normalized = sorted(normalized, key=lambda s: s.get("timestamp", ""), reverse=True)
    return {
        "sightings": normalized[:limit],
        "total":     len(normalized),
        "is_demo":   True,
    }


@router.post("/sightings")
async def report_sighting(body: dict):
    """
    POST /api/sightings
    Report a new wildlife sighting. Triggers the full orchestrated
    PREDICT → ALERT → COORDINATE workflow.

    Required body fields:
        species (str)
    Optional:
        lat, lon, count, source, nearest_village_id, village_id, village, notes, distance_km
    """
    from main import get_orchestrator
    from data.sample_data import SAMPLE_VILLAGES, get_village_by_id
    orch = get_orchestrator()

    species = body.get("species")
    if not species:
        raise HTTPException(
            status_code=422,
            detail="Missing required field: species",
        )

    village_id = body.get("nearest_village_id") or body.get("village_id") or body.get("village")
    # Resolve village if name was sent instead of ID
    if village_id:
        v_match = next((v for v in SAMPLE_VILLAGES if v["village_id"] == village_id or v["name"].lower() == str(village_id).lower()), None)
        if v_match:
            village_id = v_match["village_id"]
    if not village_id:
        village_id = "VLG001"

    v_obj = get_village_by_id(village_id) or SAMPLE_VILLAGES[0]
    lat = float(body.get("lat") or v_obj["lat"])
    lon = float(body.get("lon") or v_obj["lon"])

    payload = {
        "species": species,
        "lat": lat,
        "lon": lon,
        "count": int(body.get("count", 1)),
        "source": body.get("source") or body.get("reported_by") or "villager_report",
        "nearest_village_id": village_id,
        "distance_km": float(body.get("distance_km", 1.5)),
        "notes": body.get("notes") or body.get("location") or f"Citizen report near {v_obj['name']}",
        "time_of_day": body.get("time_of_day", "dusk"),
        "timestamp": body.get("timestamp") or datetime.now(timezone.utc).isoformat(),
    }

    result = orch.process_sighting(payload)
    return result
