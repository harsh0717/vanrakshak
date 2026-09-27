# ============================================================
# VanRakshak AI ΓÇö Flask Application Entry Point
# Human-Wildlife Conflict Mitigation Platform ΓÇö Gir Forest
# PROTOTYPE / DEMO VERSION
# Run: python app.py
# ============================================================

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

import time
import json
import asyncio
import threading
try:
    import websockets
except ImportError:
    websockets = None
from flask import Flask, jsonify, request, render_template, Response
from agents.orchestrator import Orchestrator
from agents.compensation_agent import CompensationAgent

app = Flask(__name__, template_folder="templates")
app.config["JSON_SORT_KEYS"] = False

# Single orchestrator instance (in-memory state)
orch = Orchestrator()

# Cross-device sync ΓÇö bumped whenever data changes (sightings, alerts, incidents)
_last_updated: float = time.time()

# ---------------------------------------------------------------------------
# WebSocket Server for Real-Time Threat Updates (ws://0.0.0.0:8765)
# Compatible with browser WebSocket and CLI tools like websocat
# ---------------------------------------------------------------------------
WS_CLIENTS = set()
_ws_loop = None

async def _ws_handler(websocket):
    WS_CLIENTS.add(websocket)
    try:
        welcome = {
            "type": "INIT",
            "server": "VanRakshak AI Live Stream",
            "timestamp": time.time(),
            "last_updated": _last_updated,
            "message": "Connected to real-time wildlife threat stream"
        }
        await websocket.send(json.dumps(welcome))
        async for raw in websocket:
            try:
                data = json.loads(raw)
                if data.get("type") == "PING":
                    await websocket.send(json.dumps({"type": "PONG", "timestamp": time.time()}))
            except Exception:
                pass
    except Exception:
        pass
    finally:
        WS_CLIENTS.discard(websocket)

async def _ws_main():
    global _ws_loop
    _ws_loop = asyncio.get_running_loop()
    try:
        async with websockets.serve(_ws_handler, "0.0.0.0", 8765):
            print("  [WebSocket] Stream active on ws://0.0.0.0:8765 (websocat ready)")
            await asyncio.Future()
    except Exception as e:
        print(f"  [WebSocket] Server notice: {e}")

def _start_ws_server():
    if not websockets:
        print("  [WebSocket] Library not installed; running in standard HTTP/SSE streaming mode.")
        return
    def _run():
        try:
            asyncio.run(_ws_main())
        except Exception as e:
            print(f"  [WebSocket] Thread exited: {e}")
    t = threading.Thread(target=_run, daemon=True, name="VanRakshak-WS")
    t.start()

# Launch WebSocket server in background
_start_ws_server()

def _broadcast_ws(payload: dict):
    """Broadcast JSON message to all connected WebSocket clients (browsers & websocat)."""
    if not WS_CLIENTS or not _ws_loop:
        return
    msg = json.dumps(payload)
    async def _send():
        disconnected = set()
        for ws in list(WS_CLIENTS):
            try:
                await ws.send(msg)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            WS_CLIENTS.discard(ws)
    try:
        if _ws_loop.is_running():
            asyncio.run_coroutine_threadsafe(_send(), _ws_loop)
    except Exception:
        pass


def _touch(event_type="UPDATE", details=None):
    """Bump the global last-updated timestamp and broadcast to all WebSocket clients."""
    global _last_updated
    _last_updated = time.time()
    payload = {
        "type": "THREAT_UPDATE",
        "event": event_type,
        "timestamp": _last_updated,
        "details": details or {}
    }
    _broadcast_ws(payload)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ok(data):
    return jsonify({"success": True, "data": data})


def _err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code


# ===========================================================================
# HTML Front-end
# ===========================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ===========================================================================
# Officer In-Memory Authentication (Demo / Prototype ΓÇö No Database Required)
# ===========================================================================

DEMO_OFFICERS = {
    "admin@1234": {
        "password": "harshil",
        "name": "Harshil Patil",
        "role": "Chief Range Forest Officer & Administrator",
        "badge": "GJ-FOR-CW-001",
        "division": "Gir National Park & Sanctuary",
        "station": "Sasan Gir HQ",
        "access_level": "LEVEL-5 (FULL COMMAND ACCESS)"
    }
}


@app.route("/api/officer/login", methods=["POST"])
def api_officer_login():
    """Authenticate forest officer against in-memory demo accounts."""
    data = request.get_json(silent=True) or {}
    officer_id = str(data.get("officer_id") or data.get("username") or "").strip().lower()
    password = str(data.get("password") or "").strip()

    if not officer_id or not password:
        return _err("Please provide both Officer ID and Password", 400)

    officer = DEMO_OFFICERS.get(officer_id)
    if officer and officer["password"] == password:
        profile = {k: v for k, v in officer.items() if k != "password"}
        profile["officer_id"] = officer_id
        return _ok({
            "authenticated": True,
            "officer": profile,
            "token": f"vr-demo-token-{officer_id}",
            "message": f"Welcome, {profile['name']} ({profile['role']})"
        })
    return _err("Invalid Officer ID or Password. Please check demo credentials.", 401)


@app.route("/api/officer/verify", methods=["GET"])
def api_officer_verify():
    """Return available demo officer profiles for quick evaluation."""
    demo_accounts = [
        {
            "id": k,
            "name": v["name"],
            "role": v["role"],
            "badge": v["badge"],
            "division": v["division"]
        }
        for k, v in DEMO_OFFICERS.items()
    ]
    return _ok({"status": "ready", "accounts": demo_accounts})


@app.route("/api/officer/logout", methods=["POST"])
def api_officer_logout():
    """Log out officer session."""
    return _ok({"authenticated": False, "message": "Officer signed out successfully."})


# ===========================================================================
# Cross-Device Sync ΓÇö Lightweight update check
# ===========================================================================

@app.route("/api/updates/check")
def api_updates_check():
    """Return the last-modified timestamp. Clients poll this every 3 s;
    if the value has changed since their last check, they trigger a full reload.
    This avoids hammering heavier endpoints like /api/dashboard constantly."""
    return _ok({"last_updated": _last_updated})


@app.route("/api/events")
def api_events():
    """Server-Sent Events (SSE) live push stream over standard HTTP (port 5000).
    Dual-layer fallback when WebSocket port 8765 cannot be reached."""
    def event_stream():
        last = _last_updated
        yield f"data: {json.dumps({'type': 'CONNECTED', 'last_updated': _last_updated})}\n\n"
        while True:
            time.sleep(1.0)
            if _last_updated > last:
                last = _last_updated
                yield f"data: {json.dumps({'type': 'THREAT_UPDATE', 'last_updated': _last_updated})}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")


# ===========================================================================
# Dashboard
# ===========================================================================

@app.route("/api/dashboard")
def api_dashboard():
    return _ok(orch.get_dashboard())


# ===========================================================================
# Villages
# ===========================================================================

@app.route("/api/villages")
def api_villages():
    risk_map = {r["village_id"]: r for r in orch.risk_assessments}
    result = []
    for v in orch.villages:
        r = risk_map.get(v["id"], {})
        result.append({
            **v,
            "risk_score": r.get("risk_score", 0.0),
            "risk_level": r.get("risk_level", "LOW"),
            "confidence": r.get("confidence", 0.70),
        })
    return _ok(result)


# ===========================================================================
# Sightings
# ===========================================================================

@app.route("/api/sightings", methods=["GET"])
def api_sightings_get():
    sightings = sorted(orch.sightings, key=lambda s: s.get("timestamp", ""), reverse=True)
    return _ok(sightings)


@app.route("/api/sightings", methods=["POST"])
def api_sightings_post():
    data = request.get_json(silent=True) or {}
    if "species" not in data:
        return _err("Missing required field: species")

    lat = data.get("lat")
    lon = data.get("lon")
    nearest_village = data.get("nearest_village")

    from agents.response_agent import _haversine as haversine_km

    if (lat is not None and lon is not None) and not nearest_village:
        best_v = None
        min_d = 9999.0
        for v in orch.villages:
            d = haversine_km(float(lat), float(lon), v["lat"], v["lon"])
            if d < min_d:
                min_d = d
                best_v = v
        if best_v:
            data["nearest_village"] = best_v["id"]
            if "distance_km" not in data:
                data["distance_km"] = round(min_d, 2)
    elif nearest_village and (lat is None or lon is None):
        v = next((x for x in orch.villages if x["id"] == nearest_village), None)
        if v:
            data["lat"] = v["lat"]
            data["lon"] = v["lon"]
            if "distance_km" not in data:
                data["distance_km"] = 1.0

    if "distance_km" not in data:
        data["distance_km"] = 1.0
    if "time_of_day" not in data:
        import datetime
        h = datetime.datetime.now().hour
        if 5 <= h < 8:
            data["time_of_day"] = "dawn"
        elif 8 <= h < 17:
            data["time_of_day"] = "day"
        elif 17 <= h < 20:
            data["time_of_day"] = "dusk"
        else:
            data["time_of_day"] = "night"

    if "lat" not in data or "lon" not in data or "nearest_village" not in data:
        return _err("Missing location coordinates or nearest village")

    try:
        data["lat"] = float(data["lat"])
        data["lon"] = float(data["lon"])
        data["distance_km"] = float(data["distance_km"])
    except (ValueError, TypeError):
        return _err("Invalid coordinate or distance values")

    pipeline_result = orch.process_sighting(data)
    _touch()
    return _ok(pipeline_result), 201


# ===========================================================================
# Incidents
# ===========================================================================

@app.route("/api/incidents", methods=["GET"])
def api_incidents():
    incidents = sorted(orch.incidents, key=lambda i: i.get("timestamp", ""), reverse=True)
    return _ok(incidents)


@app.route("/api/incidents/<incident_id>/update", methods=["POST"])
def api_incident_update(incident_id):
    data       = request.get_json(silent=True) or {}
    new_status = data.get("status")
    notes      = data.get("notes", "")
    if not new_status:
        return _err("Missing 'status' field")
    updated = orch.update_incident(incident_id, new_status, notes)
    if not updated:
        return _err(f"Incident {incident_id} not found", 404)
    _touch()
    return _ok(updated)


# ===========================================================================
# Alerts
# ===========================================================================

@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    alerts = sorted(orch.alerts, key=lambda a: a.get("timestamp", ""), reverse=True)
    # Seed alerts from sample data if none yet generated
    if not alerts:
        from data.sample_data import SIGHTINGS, VILLAGES
        from agents.movement_agent import MovementAgent
        from agents.alert_agent    import AlertAgent
        ma = MovementAgent()
        aa = AlertAgent()
        village_map = {v["id"]: v for v in VILLAGES}
        for s in SIGHTINGS[:20]:
            v = village_map.get(s["nearest_village"])
            if not v:
                continue
            mv = ma.process(s, v, SIGHTINGS, orch.incidents)
            al = aa.process(mv, s, v)
            alerts.append(al)
    return _ok(alerts)


@app.route("/api/alerts/generate", methods=["POST"])
def api_alert_generate():
    """Generate a new dynamic alert for a given village/sighting or user input."""
    import uuid
    from datetime import datetime

    data = request.get_json(silent=True) or {}
    village_id   = data.get("village_id")
    village_name = data.get("village_name")
    species      = data.get("species")
    severity     = data.get("severity")
    distance_km  = data.get("distance_km")
    user_msg     = data.get("message")

    village = None
    if village_id:
        village = next((v for v in orch.villages if v["id"] == village_id), None)
    if not village and village_name:
        village = next((v for v in orch.villages if v["name"].strip().lower() == str(village_name).strip().lower()), None)
    if not village:
        village = orch.villages[0]

    village_name = village["name"]

    if not species:
        sighting_id = data.get("sighting_id")
        s = next((x for x in orch.sightings if x["id"] == sighting_id), orch.sightings[0] if orch.sightings else None)
        species = s.get("species", "Asiatic Lion") if s else "Asiatic Lion"

    try:
        dist = round(float(distance_km), 1) if distance_km is not None else 0.8
    except (ValueError, TypeError):
        dist = 0.8

    sev = (severity or ("HIGH" if dist <= 1.0 else "MEDIUM" if dist <= 2.5 else "LOW")).upper()
    confidence = 0.95 if sev == "HIGH" else 0.85 if sev == "MEDIUM" else 0.76

    from agents.alert_agent import _SAFETY_ACTIONS, _FOREST_CONTACT

    guj_species = {
        "Asiatic Lion": "α¬╕α¬┐α¬éα¬╣",
        "Leopard": "α¬ªα½Çα¬¬α¬íα½ï",
        "Hyena": "α¬¥α¬░α¬û",
        "Wild Boar": "α¬£α¬éα¬ùα¬▓α½Ç α¬¡α½éα¬éα¬í",
    }.get(species, species)

    if user_msg and str(user_msg).strip():
        en_text = str(user_msg).strip()
    else:
        en_text = (
            f"{sev} RISK ALERT ΓÇö A {species.lower()} has been sighted near {village_name} "
            f"({dist:.1f} km away). Keep all livestock secured indoors. Do NOT venture outside after dark. "
            f"Stay in groups. Contact Forest Dept: {_FOREST_CONTACT}."
        )

    gu_text = (
        f"ΓÜá∩╕Å {('α¬ëα¬Üα½ìα¬Ü α¬£α½ïα¬ûα¬«' if sev == 'HIGH' else 'α¬╕α¬╛α¬ºα¬╛α¬░α¬ú' if sev == 'MEDIUM' else 'α¬╕α¬╛α¬«α¬╛α¬¿α½ìα¬»')} α¬Üα½çα¬ñα¬╡α¬úα½Ç: "
        f"{village_name} α¬¿α¬£α½Çα¬ò {guj_species} α¬¿α½Ç α¬╣α¬┐α¬▓α¬Üα¬╛α¬▓ α¬¿α½ïα¬éα¬ºα¬╛α¬ê α¬¢α½ç ({dist:.1f} α¬òα¬┐α¬«α½Ç). "
        f"α¬ñα¬«α¬╛α¬░α¬╛ α¬¬α½ìα¬░α¬╛α¬úα½Çα¬ôα¬¿α½ç α¬╕α½üα¬░α¬òα½ìα¬╖α¬┐α¬ñ α¬░α¬╛α¬ûα½ï. α¬░α¬╛α¬ñα½ìα¬░α½ç α¬¼α¬╣α¬╛α¬░ α¬¿ α¬¿α½Çα¬òα¬│α½ï. α¬╡α¬¿ α¬╡α¬┐α¬¡α¬╛α¬ù: {_FOREST_CONTACT}."
    )

    alert = {
        "alert_id": f"ALT-{uuid.uuid4().hex[:6].upper()}",
        "severity": sev,
        "village_id": village["id"],
        "village_name": village_name,
        "species": species,
        "risk_score": 0.88 if sev == "HIGH" else 0.58 if sev == "MEDIUM" else 0.28,
        "confidence": confidence,
        "distance_km": dist,
        "broadcast": sev != "LOW",
        "en_text": en_text,
        "gu_text": gu_text,
        "safety_actions": _SAFETY_ACTIONS.get(sev, _SAFETY_ACTIONS["LOW"]),
        "timestamp": datetime.utcnow().isoformat(),
        "nlg_note": "IBM Granite LLM ΓÇö Natural Language Generation (Proposed Integration ΓÇö Simulated in Prototype)",
        "agent_meta": {
            "agent": "AlertAgent",
            "version": "1.0-DYNAMIC",
            "timestamp": datetime.utcnow().isoformat(),
            "disclaimer": "Dynamic Alert broadcast via Officer Console",
        },
    }

    # Prepend to alerts list so newest appears first
    orch.alerts.insert(0, alert)

    # Dynamically log new sighting and incident
    new_sighting = {
        "id": f"S{len(orch.sightings)+1:03d}",
        "species": species,
        "lat": round(village["lat"] + 0.005, 4),
        "lon": round(village["lon"] + 0.005, 4),
        "nearest_village": village["id"],
        "distance_km": dist,
        "timestamp": datetime.utcnow().isoformat(),
        "time_of_day": "night",
        "observer": "Officer Alert Console",
        "notes": f"Broadcast Alert: {species} near {village_name} ({dist}km)",
        "verified": True,
    }
    orch.sightings.insert(0, new_sighting)

    if sev in ("HIGH", "MEDIUM"):
        new_inc = {
            "id": f"INC{len(orch.incidents)+1:03d}",
            "display_id": f"INC-{len(orch.incidents)+1:03d}",
            "village_id": village["id"],
            "village_name": village_name,
            "species": species,
            "severity": sev,
            "risk_score": alert["risk_score"],
            "status": "NEW",
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_team": "Rapid Response Team Alpha" if sev == "HIGH" else "Patrol Unit B",
            "incident_type": "WILDLIFE_SIGHTING",
            "notes": en_text,
        }
        orch.incidents.insert(0, new_inc)

    orch._log("AlertAgent", f"Generated & Broadcast {sev} alert for {village_name} ({species})", confidence)
    _touch()
    return _ok(alert), 201


# ===========================================================================
# Hotspots
# ===========================================================================

@app.route("/api/hotspots")
def api_hotspots():
    return _ok(orch.get_hotspot_data())


# ===========================================================================
# Agent status
# ===========================================================================

@app.route("/api/agents/status")
def api_agents_status():
    statuses = [
        orch.movement_agent.get_status(),
        orch.alert_agent.get_status(),
        orch.response_agent.get_status(),
        orch.compensation_agent.get_status(),
        orch.hotspot_agent.get_status(),
    ]
    return _ok(statuses)


@app.route("/api/agents/logs")
def api_agents_logs():
    logs = sorted(orch.agent_logs, key=lambda l: l.get("timestamp", ""), reverse=True)[:50]
    return _ok(logs)


# ===========================================================================
# Approval queue (Human-in-the-Loop)
# ===========================================================================

@app.route("/api/approval-queue")
def api_approval_queue():
    return _ok(orch.pending_approvals)


@app.route("/api/approve/<action_id>", methods=["POST"])
def api_approve(action_id):
    data         = request.get_json(silent=True) or {}
    decision     = data.get("decision", "APPROVE").upper()
    officer_note = data.get("officer_note", "")
    if decision not in ("APPROVE", "REJECT"):
        return _err("decision must be APPROVE or REJECT")
    result = orch.approve_action(action_id, decision, officer_note)
    if not result["success"]:
        return _err(result["error"], 404)
    _touch()
    return _ok(result)


# ===========================================================================
# Compensation
# ===========================================================================

@app.route("/api/compensation/claims")
def api_claims_list():
    claims = sorted(orch.compensation_claims, key=lambda c: c.get("timestamp", ""), reverse=True)
    return _ok(claims)


@app.route("/api/compensation/submit", methods=["POST"])
def api_claim_submit():
    data = request.get_json(silent=True) or {}
    required = ["claimant_name", "village_id", "livestock_type", "livestock_count"]
    for field in required:
        if field not in data:
            return _err(f"Missing required field: {field}")
    claim = orch.submit_compensation_claim(data)
    _touch()
    return _ok(claim), 201


@app.route("/api/compensation/rates")
def api_comp_rates():
    return _ok(CompensationAgent.get_compensation_rates())


@app.route("/api/compensation/required-docs")
def api_required_docs():
    return _ok(CompensationAgent.get_required_docs())


@app.route("/api/compensation/claim/<claim_id>", methods=["GET"])
def api_claim_get(claim_id):
    claim = orch.get_claim_by_id(claim_id)
    if not claim:
        return _err(f"Claim {claim_id} not found", 404)
    return _ok(claim)


# ===========================================================================
# Citizen Emergency SOS
# ===========================================================================

@app.route("/api/sos", methods=["POST"])
def api_sos():
    data = request.get_json(silent=True) or {}
    try:
        lat = float(data.get("lat", 21.1242))
        lon = float(data.get("lon", 70.5521))
    except (ValueError, TypeError):
        lat, lon = 21.1242, 70.5521
    contact = data.get("contact", "Citizen Emergency")
    village_id = data.get("village_id", "V001")
    species = data.get("species", "Asiatic Lion")
    message = data.get("message", "Immediate distress reported by villager")

    sighting_payload = {
        "species": species,
        "lat": lat,
        "lon": lon,
        "nearest_village": village_id,
        "distance_km": 0.3,
        "time_of_day": "night",
        "observer": f"Citizen SOS ({contact})",
        "notes": f"URGENT SOS: {message}",
        "verified": True,
    }
    result = orch.process_sighting(sighting_payload)
    _touch()
    return _ok({
        "status": "SOS_BROADCAST",
        "message": "Forest Department Rapid Response Team notified. Stay in a safe, enclosed area.",
        "helplines": {
            "forest_dept_toll_free": "1926",
            "ambulance": "108",
            "sasan_gir_control_room": "02877-285541"
        },
        "workflow": result
    }), 201


# ===========================================================================
# Demo scenario
# ===========================================================================

@app.route("/api/demo/run")
def api_demo_run():
    result = orch.run_demo_scenario()
    return _ok(result)


# ===========================================================================
# Audit log
# ===========================================================================

@app.route("/api/audit-log")
def api_audit_log():
    logs = list(reversed(orch.audit_log[-100:]))
    return _ok(logs)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  VanRakshak AI ΓÇö Human-Wildlife Conflict Mitigation")
    print("  Gir Forest Prototype | DEMO MODE")
    print("  Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
