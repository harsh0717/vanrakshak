# ============================================================
# VanRakshak AI — Central Orchestrator
# Routes wildlife events through all 5 agents in sequence.
# Maintains shared state. Human-approval queue enforced.
# ============================================================

import copy
import uuid
from datetime import datetime, timedelta

from agents.movement_agent     import MovementAgent
from agents.alert_agent        import AlertAgent
from agents.response_agent     import ResponseAgent
from agents.compensation_agent import CompensationAgent, _REQUIRED_DOCS
from agents.hotspot_agent      import HotspotAgent
from data.sample_data          import get_all_data


class Orchestrator:
    """
    Central Orchestration Layer for VanRakshak AI.

    State held in-memory (no database).  The pipeline for a new sighting:
        S001  →  MovementAgent  →  AlertAgent  →  ResponseAgent
              →  HotspotAgent  →  (human approval queue)
    """

    def __init__(self):
        # --- Load demo seed data ---
        seed = get_all_data()
        self.villages        = seed["villages"]
        self.sightings       = seed["sightings"]
        self.incidents       = seed["incidents"]
        self.response_teams  = seed["response_teams"]
        self.risk_assessments = seed["risk_assessments"]
        self.agent_logs      = seed["agent_logs"]

        # Runtime state
        self.alerts           = []
        self.compensation_claims = []
        self.pending_approvals  = []
        self.approved_actions   = []
        self.audit_log          = []

        # Instantiate all agents
        self.movement_agent     = MovementAgent()
        self.alert_agent        = AlertAgent()
        self.response_agent     = ResponseAgent()
        self.compensation_agent = CompensationAgent()
        self.hotspot_agent      = HotspotAgent()

        # Run initial hotspot assessment on seed data
        self._refresh_hotspots()
        self._log("Orchestrator", "System initialised with demo seed data", 1.0)

        # Seed rich demo alerts, approvals, and compensation claims
        self._seed_demo_state()

    def _seed_demo_state(self):
        """Seed initial alerts, pending approvals, and compensation claims for realistic demo."""
        _now = datetime.utcnow()
        village_map = {v["id"]: v for v in self.villages}

        # 1. Seed 20 alerts across top sightings
        for s in self.sightings[:20]:
            v = village_map.get(s["nearest_village"])
            if v:
                mv = self.movement_agent.process(s, v, self.sightings, self.incidents)
                al = self.alert_agent.process(mv, s, v)
                self.alerts.append(al)

        # 2. Seed pending officer approvals (Human-in-the-Loop)
        self.pending_approvals = [
            {
                "action_id": "APR-101",
                "action_type": "DISPATCH_TEAM",
                "incident_id": "INC-011",
                "ai_recommendation": "Dispatch Talala Rescue Team (RT-003) to Talala for Leopard encounter near primary school path.",
                "recommended_team": "RT-003",
                "recommended_team_name": "Talala Rescue Team",
                "confidence": 0.88,
                "risk_score": 0.74,
                "reasoning": "Morning school route encounter. Nearest rapid rescue team is RT-003 (0.9 km). Prioritize perimeter security.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(hours=2)).isoformat(),
                "village_id": "V003",
            },
            {
                "action_id": "APR-102",
                "action_type": "DISPATCH_TEAM",
                "incident_id": "INC-023",
                "ai_recommendation": "Dispatch Mendarda Forest Unit (RT-002) to Mendarda for high-risk Asiatic Lion pride sighting.",
                "recommended_team": "RT-002",
                "recommended_team_name": "Mendarda Forest Unit",
                "confidence": 0.92,
                "risk_score": 0.89,
                "reasoning": "Pride of 3 lingering within 400m of village dwellings. Acoustic deterrents and thermal drone escort recommended.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(hours=1)).isoformat(),
                "village_id": "V006",
            },
            {
                "action_id": "APR-103",
                "action_type": "DISPATCH_TEAM",
                "incident_id": "INC-025",
                "ai_recommendation": "Dispatch Dhari Wildlife Squad (RT-004) to Dhari for Leopard entered farm shed.",
                "recommended_team": "RT-004",
                "recommended_team_name": "Dhari Wildlife Squad",
                "confidence": 0.94,
                "risk_score": 0.85,
                "reasoning": "Farmer trapped inside residence; predator in shed. Specialized feline capture kit and tranquilizer unit required.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(minutes=40)).isoformat(),
                "village_id": "V002",
            },
            {
                "action_id": "APR-104",
                "action_type": "DEPLOY_EQUIPMENT",
                "incident_id": "INC-013",
                "ai_recommendation": "Deploy Box Trap Cage and Thermal Drone TD-02 in Visavadar mango grove corridor.",
                "recommended_team": "RT-001",
                "recommended_team_name": "Sasan Rapid Response",
                "confidence": 0.85,
                "risk_score": 0.81,
                "reasoning": "Repeat leopard incursions recorded over 72h. Passive capture cage prevents livestock loss without harming feline.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(hours=3)).isoformat(),
                "village_id": "V004",
            },
            {
                "action_id": "APR-105",
                "action_type": "COMPENSATION_CLAIM",
                "claim_id": "CLM-001",
                "ai_recommendation": "Approve ₹50,000 compensation payout to Devji Rabari (Sasan Gir) for 2 buffaloes killed by lion.",
                "confidence": 0.95,
                "risk_score": 0.82,
                "reasoning": "All 7 documents verified: Veterinary post-mortem complete, Sarpanch endorsement attached, carcass geotagged.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(hours=4)).isoformat(),
                "village_id": "V001",
            },
            {
                "action_id": "APR-106",
                "action_type": "COMPENSATION_CLAIM",
                "claim_id": "CLM-003",
                "ai_recommendation": "Approve ₹12,000 compensation payout to Khimji B. Solanki (Dhari) for 3 sheep lost to hyena pack.",
                "confidence": 0.89,
                "risk_score": 0.55,
                "reasoning": "Predation confirmed via hair sample and pugmarks. Claimant bank passbook and Aadhaar verified.",
                "status": "PENDING",
                "timestamp": (_now - timedelta(hours=5)).isoformat(),
                "village_id": "V002",
            },
        ]

        # 3. Seed realistic compensation claims
        all_docs = list(_REQUIRED_DOCS)
        partial_docs = all_docs[:5]

        self.compensation_claims = [
            {
                "claim_id": "CLM-001",
                "incident_id": "INC-001",
                "claimant_name": "Devji Rabari",
                "village_id": "V001",
                "village_name": "Sasan Gir",
                "species_responsible": "Asiatic Lion",
                "livestock_type": "buffalo",
                "livestock_count": 2,
                "rate_per_animal_inr": 25000,
                "preliminary_amount_inr": 50000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.95,
                "status": "PENDING_REVIEW",
                "timestamp": (_now - timedelta(days=2)).isoformat(),
                "notes": "2 milch buffaloes predated at night in Maldhari Ness.",
            },
            {
                "claim_id": "CLM-002",
                "incident_id": "INC-002",
                "claimant_name": "Bhagwanji Ahir",
                "village_id": "V003",
                "village_name": "Talala",
                "species_responsible": "Leopard",
                "livestock_type": "goat",
                "livestock_count": 1,
                "rate_per_animal_inr": 3500,
                "preliminary_amount_inr": 3500,
                "doc_checklist": [{"document": d, "available": d in partial_docs} for d in all_docs],
                "docs_complete": False,
                "missing_docs": [d for d in all_docs if d not in partial_docs],
                "confidence": 0.78,
                "status": "DRAFT",
                "timestamp": (_now - timedelta(days=1)).isoformat(),
                "notes": "Goat dragged into shrubland. Awaiting bank passbook.",
            },
            {
                "claim_id": "CLM-003",
                "incident_id": "INC-005",
                "claimant_name": "Khimji B. Solanki",
                "village_id": "V004",
                "village_name": "Visavadar",
                "species_responsible": "Hyena",
                "livestock_type": "sheep",
                "livestock_count": 3,
                "rate_per_animal_inr": 4000,
                "preliminary_amount_inr": 12000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.90,
                "status": "PENDING_REVIEW",
                "timestamp": (_now - timedelta(days=5)).isoformat(),
                "notes": "3 sheep killed in unprotected pen. Verified by forest guard.",
            },
            {
                "claim_id": "CLM-004",
                "incident_id": "INC-006",
                "claimant_name": "Bhavna Patel",
                "village_id": "V001",
                "village_name": "Sasan Gir",
                "species_responsible": "Asiatic Lion",
                "livestock_type": "cow",
                "livestock_count": 1,
                "rate_per_animal_inr": 20000,
                "preliminary_amount_inr": 20000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.98,
                "status": "APPROVED",
                "timestamp": (_now - timedelta(days=7)).isoformat(),
                "notes": "Direct Benefit Transfer processed to claimant SBI account.",
            },
            {
                "claim_id": "CLM-005",
                "incident_id": "INC-008",
                "claimant_name": "Mansukh V. Gohil",
                "village_id": "V006",
                "village_name": "Mendarda",
                "species_responsible": "Leopard",
                "livestock_type": "goat",
                "livestock_count": 2,
                "rate_per_animal_inr": 3500,
                "preliminary_amount_inr": 7000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.88,
                "status": "PENDING_REVIEW",
                "timestamp": (_now - timedelta(days=4)).isoformat(),
                "notes": "Goats taken from pen near outer wall.",
            },
            {
                "claim_id": "CLM-006",
                "incident_id": "INC-015",
                "claimant_name": "Ramji J. Bharwad",
                "village_id": "V006",
                "village_name": "Mendarda",
                "species_responsible": "Asiatic Lion",
                "livestock_type": "cow",
                "livestock_count": 1,
                "rate_per_animal_inr": 20000,
                "preliminary_amount_inr": 20000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.92,
                "status": "VERIFIED",
                "timestamp": (_now - timedelta(days=2)).isoformat(),
                "notes": "Post-mortem by Talala Veterinary dispensary confirmed lion predation.",
            },
            {
                "claim_id": "CLM-007",
                "incident_id": "INC-018",
                "claimant_name": "Pravin K. Mer",
                "village_id": "V001",
                "village_name": "Sasan Gir",
                "species_responsible": "Leopard",
                "livestock_type": "goat",
                "livestock_count": 2,
                "rate_per_animal_inr": 3500,
                "preliminary_amount_inr": 7000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.91,
                "status": "PENDING_REVIEW",
                "timestamp": (_now - timedelta(days=3)).isoformat(),
                "notes": "Night raid on shed. Panchanama verified by forest guard.",
            },
            {
                "claim_id": "CLM-008",
                "incident_id": "INC-024",
                "claimant_name": "Suresh M. Vala",
                "village_id": "V001",
                "village_name": "Sasan Gir",
                "species_responsible": "Asiatic Lion",
                "livestock_type": "buffalo",
                "livestock_count": 1,
                "rate_per_animal_inr": 25000,
                "preliminary_amount_inr": 25000,
                "doc_checklist": [{"document": d, "available": True} for d in all_docs],
                "docs_complete": True,
                "missing_docs": [],
                "confidence": 0.94,
                "status": "PENDING_REVIEW",
                "timestamp": (_now - timedelta(days=9)).isoformat(),
                "notes": "Adult milch buffalo predated near Sasan outer corridor.",
            },
        ]


    # ==================================================================
    # Main pipeline — called on every new sighting
    # ==================================================================

    def process_sighting(self, sighting: dict) -> dict:
        """
        Full 5-agent pipeline for a new wildlife sighting.

        1. Identify nearest village
        2. Agent 1 — movement / risk prediction
        3. Agent 2 — alert generation
        4. Agent 3 — incident + approval queue
        5. Agent 5 — hotspot refresh
        Returns a pipeline result dict.
        """
        pipeline_id = f"PIP-{uuid.uuid4().hex[:6].upper()}"
        self._log("Orchestrator", f"Pipeline {pipeline_id} started for {sighting.get('id','new')}", 1.0)

        # Assign an id if new
        if not sighting.get("id"):
            sighting["id"] = f"S{len(self.sightings)+1:03d}"
        self.sightings.append(sighting)

        # Step 1 — resolve village
        village = self._find_village(sighting.get("nearest_village")) or self.villages[0]

        # Step 2 — Movement Agent
        movement_result = self.movement_agent.process(
            sighting, village, self.sightings, self.incidents
        )
        self._log("MovementAgent",
                  f"Risk={movement_result['risk_score']} ({movement_result['risk_level']}) for {village['name']}",
                  movement_result["confidence"])

        # Step 3 — Alert Agent
        alert = self.alert_agent.process(movement_result, sighting, village)
        self.alerts.append(alert)
        self._log("AlertAgent",
                  f"{'Broadcast' if alert['broadcast'] else 'Logged'} {alert['severity']} alert — {village['name']}",
                  alert["confidence"])

        # Step 4 — Response Agent (only for MEDIUM/HIGH)
        incident = None
        if movement_result["risk_level"] in ("MEDIUM", "HIGH"):
            incident = self.response_agent.process(
                alert, sighting, village, self.response_teams, self.pending_approvals
            )
            self.incidents.append(incident)
            self._log("ResponseAgent",
                      f"Incident {incident['id']} created — team {incident['recommended_team_name']} recommended",
                      alert["confidence"])
        else:
            self._log("ResponseAgent", "Risk LOW — no incident created", alert["confidence"])

        # Step 5 — Hotspot refresh
        hotspot_result = self._refresh_hotspots()
        self._log("HotspotAgent",
                  f"{len(hotspot_result['hotspots'])} clusters recalculated",
                  hotspot_result["confidence"])

        self._log("Orchestrator", f"Pipeline {pipeline_id} complete", movement_result["confidence"])

        return {
            "pipeline_id":    pipeline_id,
            "sighting":       sighting,
            "village":        village,
            "movement":       movement_result,
            "alert":          alert,
            "incident":       incident,
            "hotspots":       hotspot_result["hotspots"][:3],
            "pending_approvals": len(self.pending_approvals),
            "timestamp":      datetime.utcnow().isoformat(),
        }

    # ==================================================================
    # Compensation claim
    # ==================================================================

    def submit_compensation_claim(self, claim_data: dict) -> dict:
        if not claim_data.get("village_name") and claim_data.get("village_id"):
            v = self._find_village(claim_data["village_id"])
            if v:
                claim_data["village_name"] = v["name"]
        claim = self.compensation_agent.process(claim_data, self.pending_approvals)
        self.compensation_claims.append(claim)
        self._log("CompensationAgent",
                  f"Claim {claim['claim_id']} drafted — ₹{claim['preliminary_amount_inr']:,}",
                  claim["confidence"])
        return claim

    def get_claim_by_id(self, claim_id: str):
        for c in self.compensation_claims:
            if c.get("claim_id") == claim_id:
                return c
        return None

    # ==================================================================
    # Human approval
    # ==================================================================

    def approve_action(self, action_id: str, decision: str, officer_note: str = "") -> dict:
        """
        decision: 'APPROVE' or 'REJECT'
        """
        for item in self.pending_approvals:
            if item["action_id"] == action_id:
                item["status"]        = decision
                item["officer_note"]  = officer_note
                item["decided_at"]    = datetime.utcnow().isoformat()

                if decision == "APPROVE" and item["action_type"] == "DISPATCH_TEAM":
                    # Actually assign the team to the incident
                    inc_id = item.get("incident_id")
                    for inc in self.incidents:
                        if inc["id"] == inc_id:
                            self.response_agent.update_status(
                                inc, "ASSIGNED", self.response_teams,
                                f"Officer approved dispatch of {item['recommended_team_name']}"
                            )
                            break

                self.approved_actions.append(item)
                self.pending_approvals.remove(item)
                self._log("Orchestrator",
                          f"Action {action_id} {decision} by officer",
                          item.get("confidence", 1.0))
                return {"success": True, "action": item}

        return {"success": False, "error": f"Action {action_id} not found"}

    # ==================================================================
    # Incident status update
    # ==================================================================

    def update_incident(self, incident_id: str, new_status: str, notes: str = "") -> dict:
        norm_id = str(incident_id).strip().upper().replace("-", "")
        for inc in self.incidents:
            inc_id = str(inc.get("id", "")).strip().upper().replace("-", "")
            disp_id = str(inc.get("display_id", "")).strip().upper().replace("-", "")
            if inc.get("id") == incident_id or norm_id == inc_id or norm_id == disp_id:
                self.response_agent.update_status(inc, new_status, self.response_teams, notes)
                self._log("ResponseAgent", f"Incident {inc.get('id', incident_id)} → {new_status}", 1.0)
                return inc
        return {}

    # ==================================================================
    # Demo scenario — 8-step end-to-end walkthrough
    # ==================================================================

    def run_demo_scenario(self) -> dict:
        """
        Simulate a complete pipeline: lion sighting near Sasan Gir at night.
        Returns step-by-step log for the UI.
        """
        steps = []

        steps.append({
            "step": 1, "agent": "Field Sensor / Guard",
            "action": "New sighting reported",
            "detail": "Forest Guard Ramesh K. reports: Male Asiatic Lion, 0.7 km from Sasan Gir village pen area. Time: 22:30 IST.",
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        demo_sighting = {
            "id": f"DEMO-{uuid.uuid4().hex[:4].upper()}",
            "species": "Asiatic Lion",
            "lat": 21.1195, "lon": 70.6110,
            "nearest_village": "V001",
            "distance_km": 0.7,
            "timestamp": datetime.utcnow().isoformat(),
            "time_of_day": "night",
            "observer": "Forest Guard Ramesh K.",
            "notes": "DEMO: Male lion near livestock pen — demo scenario",
            "verified": True,
        }

        steps.append({
            "step": 2, "agent": "Orchestrator",
            "action": "Event routed to pipeline",
            "detail": f"Sighting {demo_sighting['id']} ingested. Routing to MovementAgent.",
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        village = self._find_village("V001")
        movement = self.movement_agent.process(
            demo_sighting, village, self.sightings, self.incidents
        )
        steps.append({
            "step": 3, "agent": "MovementAgent",
            "action": "Movement & risk prediction",
            "detail": (
                f"Risk Score: {movement['risk_score']} — {movement['risk_level']}. "
                f"Movement Probability: {movement['movement_probability']:.0%}. "
                f"Predicted Zone: {movement['predicted_risk_zone']}."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "risk_score": movement["risk_score"],
                "risk_level": movement["risk_level"],
                "confidence": movement["confidence"],
            },
        })

        alert = self.alert_agent.process(movement, demo_sighting, village)
        self.alerts.append(alert)
        steps.append({
            "step": 4, "agent": "AlertAgent",
            "action": f"{'Broadcast' if alert['broadcast'] else 'Logged'} {alert['severity']} alert",
            "detail": alert["en_text"],
            "gu_text": alert["gu_text"],
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "alert_id": alert["alert_id"],
                "severity": alert["severity"],
                "broadcast": alert["broadcast"],
            },
        })

        incident = self.response_agent.process(
            alert, demo_sighting, village, self.response_teams, self.pending_approvals
        )
        self.incidents.append(demo_sighting)
        steps.append({
            "step": 5, "agent": "ResponseAgent",
            "action": f"Incident ticket {incident['id']} created",
            "detail": (
                f"Severity: {incident['severity']}. "
                f"Nearest team: {incident['recommended_team_name']} "
                f"({incident['distance_to_team_km']} km away). "
                f"Dispatch approval requested from officer."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "incident_id": incident["id"],
                "recommended_team": incident["recommended_team_name"],
                "approval_id": incident.get("approval_id"),
            },
        })

        steps.append({
            "step": 6, "agent": "Officer (Human-in-the-Loop)",
            "action": "Approval queue — officer reviews dispatch recommendation",
            "detail": (
                f"AI Recommendation: Dispatch {incident['recommended_team_name']}. "
                f"Confidence: {alert['confidence']:.0%}. "
                "Officer reviews and APPROVES or OVERRIDES. "
                "⚠️ No autonomous dispatch — human decision required."
            ),
            "status": "AWAITING_HUMAN", "timestamp": datetime.utcnow().isoformat(),
        })

        hotspot_result = self._refresh_hotspots()
        steps.append({
            "step": 7, "agent": "HotspotAgent",
            "action": "Hotspot clusters recalculated",
            "detail": (
                f"{len(hotspot_result['hotspots'])} conflict zones identified. "
                f"Daily summary: {hotspot_result['daily_summary']}"
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
            "output": {
                "cluster_count": len(hotspot_result["hotspots"]),
                "top_hotspot": hotspot_result["hotspots"][0]["center_village"] if hotspot_result["hotspots"] else "N/A",
            },
        })

        steps.append({
            "step": 8, "agent": "Orchestrator",
            "action": "Audit log updated — pipeline complete",
            "detail": (
                "Full pipeline executed: PREDICT → ALERT → COORDINATE → LEARN. "
                "All actions logged. Human approval enforced at dispatch stage. "
                "System ready for next event."
            ),
            "status": "COMPLETE", "timestamp": datetime.utcnow().isoformat(),
        })

        self._log("Orchestrator", "Demo scenario completed", movement["confidence"])

        return {
            "scenario": "Lion Sighting — Sasan Gir Night Alert",
            "steps": steps,
            "sighting": demo_sighting,
            "alert": alert,
            "incident": incident,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ==================================================================
    # Dashboard data
    # ==================================================================

    def get_dashboard(self) -> dict:
        active_incidents  = sum(1 for i in self.incidents if i.get("status") not in ("RESOLVED",))
        high_risk         = sum(1 for r in self.risk_assessments if r["risk_level"] == "HIGH")
        avg_confidence    = (
            sum(r["confidence"] for r in self.risk_assessments) / max(1, len(self.risk_assessments))
        )
        pending_approvals = len(self.pending_approvals)

        # Enrich villages with risk level
        risk_map = {r["village_id"]: r for r in self.risk_assessments}
        villages_enriched = []
        for v in self.villages:
            r = risk_map.get(v["id"], {})
            villages_enriched.append({
                **v,
                "risk_score":  r.get("risk_score", 0.0),
                "risk_level":  r.get("risk_level", "LOW"),
                "confidence":  r.get("confidence", 0.70),
            })

        recent_sightings = sorted(
            self.sightings, key=lambda s: s.get("timestamp", ""), reverse=True
        )[:10]

        recent_alerts = sorted(
            self.alerts, key=lambda a: a.get("timestamp", ""), reverse=True
        )[:10]

        recent_incidents = sorted(
            self.incidents, key=lambda i: i.get("timestamp", ""), reverse=True
        )[:10]

        return {
            "stats": {
                "active_incidents":  active_incidents,
                "high_risk_zones":   high_risk,
                "avg_confidence":    round(avg_confidence, 2),
                "pending_approvals": pending_approvals,
                "total_sightings":   len(self.sightings),
                "total_incidents":   len(self.incidents),
            },
            "villages":          villages_enriched,
            "recent_sightings":  recent_sightings,
            "recent_alerts":     recent_alerts,
            "recent_incidents":  recent_incidents,
            "agent_statuses":    self._get_all_agent_statuses(),
        }

    def get_hotspot_data(self) -> dict:
        return self._refresh_hotspots()

    def _refresh_hotspots(self) -> dict:
        result = self.hotspot_agent.process(self.incidents, self.sightings, self.villages)
        self.last_hotspot_result = result
        return result

    def _get_all_agent_statuses(self) -> list:
        return [
            self.movement_agent.get_status(),
            self.alert_agent.get_status(),
            self.response_agent.get_status(),
            self.compensation_agent.get_status(),
            self.hotspot_agent.get_status(),
        ]

    def _find_village(self, village_id: str):
        for v in self.villages:
            if v["id"] == village_id:
                return v
        return None

    def _log(self, agent: str, action: str, confidence: float):
        self.audit_log.append({
            "agent":      agent,
            "action":     action,
            "confidence": confidence,
            "timestamp":  datetime.utcnow().isoformat(),
        })
        # Mirror to agent_logs list (used by the API)
        self.agent_logs.append({
            "agent":      agent,
            "action":     action,
            "confidence": confidence,
            "timestamp":  datetime.utcnow().isoformat(),
        })
