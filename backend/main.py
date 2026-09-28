"""
VanRakshak AI — FastAPI Application Entry Point
=================================================
Run with:
    uvicorn backend.main:app --reload
  or (from inside backend/):
    uvicorn main:app --reload

ALL DATA AND MODELS ARE DEMO / PROTOTYPE ONLY.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from orchestrator.orchestrator import VanRakshakOrchestrator

# ---------------------------------------------------------------------------
# Create the module-level orchestrator singleton
# ---------------------------------------------------------------------------
_orchestrator: VanRakshakOrchestrator | None = None


def get_orchestrator() -> VanRakshakOrchestrator:
    """Return the app-wide orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = VanRakshakOrchestrator()
    return _orchestrator


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="VanRakshak AI",
    description=(
        "Agentic AI Platform for Human-Wildlife Conflict Mitigation "
        "around Gir Forest, Gujarat, India.\n\n"
        "⚠️ **PROTOTYPE / DEMO** — All data is synthetic. "
        "Not for operational use without validated models and Forest Department approval."
    ),
    version="1.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Include routers
# ---------------------------------------------------------------------------

from routes.dashboard    import router as dashboard_router
from routes.sightings    import router as sightings_router
from routes.incidents    import router as incidents_router
from routes.alerts       import router as alerts_router
from routes.compensation import router as compensation_router
from routes.agents       import router as agents_router
from routes.demo         import router as demo_router

app.include_router(dashboard_router,    prefix="/api", tags=["Dashboard"])
app.include_router(sightings_router,    prefix="/api", tags=["Sightings"])
app.include_router(incidents_router,    prefix="/api", tags=["Incidents"])
app.include_router(alerts_router,       prefix="/api", tags=["Alerts"])
app.include_router(compensation_router, prefix="/api", tags=["Compensation"])
app.include_router(agents_router,       prefix="/api", tags=["Agents"])
app.include_router(demo_router,         prefix="/api", tags=["Demo"])

# ---------------------------------------------------------------------------
# Root health-check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def root():
    return {
        "service":     "VanRakshak AI",
        "status":      "running",
        "version":     "1.0.0-demo",
        "description": "Agentic AI for Human-Wildlife Conflict Mitigation — Gir Forest",
        "disclaimer":  "PROTOTYPE / DEMO — All data is synthetic",
        "docs":        "/docs",
        "is_demo":     True,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "is_demo": True}


# ---------------------------------------------------------------------------
# In-Memory Demo Officer Authentication (No Database Required)
# ---------------------------------------------------------------------------

DEMO_OFFICERS = {
    "admin@1234": {
        "password": "admin",
        "name": "ADMIN",
        "role": "Chief Range Forest Officer & Administrator",
        "badge": "GJ-FOR-CW-001",
        "division": "Gir National Park & Sanctuary",
        "station": "Sasan Gir HQ",
        "access_level": "LEVEL-5 (FULL COMMAND ACCESS)"
    },
    "admin": {
        "password": "admin",
        "name": "ADMIN",
        "role": "Chief Range Forest Officer & Administrator",
        "badge": "GJ-FOR-CW-001",
        "division": "Gir National Park & Sanctuary",
        "station": "Sasan Gir HQ",
        "access_level": "LEVEL-5 (FULL COMMAND ACCESS)"
    }
}


@app.post("/api/officer/login", tags=["Officer Auth"])
async def officer_login(payload: dict):
    officer_id = str(payload.get("officer_id") or payload.get("username") or "").strip().lower()
    password = str(payload.get("password") or "").strip()

    if not officer_id or not password:
        return {"success": False, "error": "Please provide both Officer ID and Password"}

    officer = DEMO_OFFICERS.get(officer_id)
    if officer and (officer["password"] == password or password in ("admin", "admin@1234", "admin123")):
        profile = {k: v for k, v in officer.items() if k != "password"}
        profile["officer_id"] = officer_id
        return {
            "success": True,
            "data": {
                "authenticated": True,
                "officer": profile,
                "token": f"vr-demo-token-{officer_id}",
                "message": f"Welcome, {profile['name']} ({profile['role']})"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid Officer ID or Password. Please check demo credentials.")


@app.get("/api/officer/verify", tags=["Officer Auth"])
async def officer_verify():
    accounts = [
        {"id": k, "name": v["name"], "role": v["role"], "badge": v["badge"], "division": v["division"]}
        for k, v in DEMO_OFFICERS.items()
    ]
    return {"success": True, "data": {"status": "ready", "accounts": accounts}}


@app.post("/api/officer/logout", tags=["Officer Auth"])
async def officer_logout():
    return {"success": True, "data": {"authenticated": False, "message": "Signed out"}}


# ---------------------------------------------------------------------------
# Startup event — initialise orchestrator eagerly
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Pre-warm the orchestrator and ML model on startup."""
    orch = get_orchestrator()
    # Trigger ML model training (happens in __init__ of MovementPredictor)
    _ = orch.agents["movement"]
    print("✅ VanRakshak AI started — orchestrator and ML model ready [DEMO MODE]")
