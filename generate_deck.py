"""
VanRakshak AI — 23-Slide Hackathon Pitch Deck Generator
Creates a professional, visually rich 16:9 widescreen presentation in PowerPoint (.pptx).
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── COLOR PALETTE ──────────────────────────────────────────────────────────
BG_DARK        = RGBColor(11, 20, 16)      # #0B1410 Deep Forest Night
BG_CARD        = RGBColor(19, 36, 29)      # #13241D Forest Slate Card
BG_CARD_LIGHT  = RGBColor(26, 48, 39)      # #1A3027 Lighter Card
ACCENT_GREEN   = RGBColor(16, 185, 129)    # #10B981 Emerald
ACCENT_CYAN    = RGBColor(6, 182, 212)     # #06B6D4 Electric Cyan
ACCENT_AMBER   = RGBColor(245, 158, 11)    # #F59E0B Warning Gold
ACCENT_RED     = RGBColor(244, 63, 94)     # #F43F5E High Threat Coral
TEXT_WHITE     = RGBColor(248, 250, 252)   # #F8FAFC Bright White
TEXT_MUTED     = RGBColor(148, 163, 184)   # #94A3B8 Slate Gray
TEXT_DIM       = RGBColor(100, 116, 139)   # #64748B Dim Slate
BORDER_COLOR   = RGBColor(45, 78, 64)      # #2D4E40 Forest Border

FONT_HEADING = "Segoe UI"
FONT_BODY    = "Segoe UI"

TOTAL_SLIDES = 23

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width  = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def add_blank_slide(prs):
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()
    return slide

def add_header(slide, slide_num, tracker_text, title_text, subtitle_text=""):
    """Standardized clean header for every slide"""
    badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.35))
    tf_b = badge_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = f"SLIDE {slide_num:02d}/{TOTAL_SLIDES:02d}  ·  {tracker_text.upper()}"
    p_b.font.name = FONT_HEADING
    p_b.font.size = Pt(10.5)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_GREEN

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.65))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.38), Inches(11.733), Inches(0.45))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(12.5)
        p_s.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=BORDER_COLOR):
    """Draw a clean card container"""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
    else:
        card.line.fill.background()
    return card

def add_content_card(slide, left, top, width, height, title, items, badge="", badge_color=ACCENT_GREEN, border_color=BORDER_COLOR):
    """Add a card with title, optional badge, and bullet/feature items"""
    add_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=border_color)
    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.22), Inches(width - 0.5), Inches(height - 0.44))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(14.5)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    if badge:
        p_badge = tf.add_paragraph()
        p_badge.text = badge.upper()
        p_badge.font.name = FONT_HEADING
        p_badge.font.size = Pt(9.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = badge_color
        p_badge.space_before = Pt(2)

    for item in items:
        p_item = tf.add_paragraph()
        if isinstance(item, tuple):
            lead, desc = item
            p_item.text = f"•  {lead}: {desc}"
        else:
            p_item.text = f"•  {item}"
        p_item.font.name = FONT_BODY
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = TEXT_MUTED
        p_item.space_before = Pt(6)

def add_stat_box(slide, left, top, width, height, stat_num, stat_label, subtext="", accent_color=ACCENT_GREEN):
    """Draw a high-impact metric highlight box"""
    add_card(slide, left, top, width, height, bg_color=BG_CARD, border_color=accent_color)
    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.18), Inches(width - 0.4), Inches(height - 0.36))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p1 = tf.paragraphs[0]
    p1.text = stat_num
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = accent_color

    p2 = tf.add_paragraph()
    p2.text = stat_label
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(11.5)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(3)

    if subtext:
        p3 = tf.add_paragraph()
        p3.text = subtext
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(2)

def build_deck():
    prs = create_presentation()

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 1: Title Slide
    # ══════════════════════════════════════════════════════════════════════
    s1 = add_blank_slide(prs)
    # Header tag
    t1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(11.733), Inches(0.4))
    tf1 = t1.text_frame
    p = tf1.paragraphs[0]
    p.text = "NATIONAL HACKATHON 2026  ·  AI & ENVIRONMENTAL CONSERVATION TRACK"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    # Big Title
    t_main = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.3))
    tf_m = t_main.text_frame
    p_m = tf_m.paragraphs[0]
    p_m.text = "VanRakshak AI (વનરક્ષક)"
    p_m.font.name = FONT_HEADING
    p_m.font.size = Pt(46)
    p_m.font.bold = True
    p_m.font.color.rgb = TEXT_WHITE

    # Subtitle
    t_sub = s1.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.733), Inches(0.8))
    tf_sub = t_sub.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Real-Time Multi-Agent AI System for Human-Wildlife Coexistence & Early Warning in the Greater Gir Ecosystem"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = ACCENT_CYAN

    # 4 Quick Stat Highlights
    add_stat_box(s1, 0.8, 3.8, 2.7, 1.6, "5 AI AGENTS", "Collaborative Mesh", "Sequential stateful event bus", ACCENT_GREEN)
    add_stat_box(s1, 3.8, 3.8, 2.7, 1.6, "0.8s SYNC", "WebSocket & SSE", "Sub-second push telemetry", ACCENT_CYAN)
    add_stat_box(s1, 6.8, 3.8, 2.7, 1.6, "48 HOURS", "Ex-Gratia Claims", "vs 180 days legacy paperwork", ACCENT_AMBER)
    add_stat_box(s1, 9.8, 3.8, 2.7, 1.6, "100% VERNACULAR", "Gujarati & English", "Accessible to rural Maldharis", ACCENT_GREEN)

    # Footer note
    t_foot = s1.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.6))
    tf_f = t_foot.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Developed for Gujarat Forest Department · Asiatic Lion Conservation Landscape · Team VanRakshak"
    p_f.font.name = FONT_BODY
    p_f.font.size = Pt(12)
    p_f.font.color.rgb = TEXT_MUTED

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 2: The Gir Dilemma: Problem Statement & Context
    # ══════════════════════════════════════════════════════════════════════
    s2 = add_blank_slide(prs)
    add_header(s2, 2, "Context & Crisis", "The Gir Dilemma: Apex Predators in Agrarian Landscapes", 
               "Asiatic Lions (Panthera leo leo) have outgrown protected sanctuary borders into agricultural settlements.")
    
    add_content_card(s2, 0.8, 2.1, 3.7, 4.4, "Ecological Success vs Crisis", [
        ("Sanctuary Capacity", "Gir Protected Area is designed for ~300 adult lions; current population exceeds 700+."),
        ("Spatial Spillover", "Over 40% of pride ranges now reside outside reserve forests across 4 districts."),
        ("Global Significance", "Gir is the ONLY surviving habitat of Asiatic lions on Earth; a single crisis threatens extinction.")
    ], "SITUATION OVERVIEW", ACCENT_GREEN)

    add_content_card(s2, 4.8, 2.1, 3.7, 4.4, "Ground Reality & Carnivore Conflict", [
        ("Livestock Depredation", "2,000+ cattle & goats killed annually, causing severe economic distress to pastoralists."),
        ("Nocturnal Encounters", "Lions & leopards hunt in agricultural fields, mango orchards, and rural perimeters."),
        ("Human Vulnerability", "Tragic human-carnivore encounters occur during early morning farming & dusk transit.")
    ], "THE CONFLICT ESCALATION", ACCENT_AMBER)

    add_content_card(s2, 8.8, 2.1, 3.7, 4.4, "The Coexistence Breakdown", [
        ("Retaliatory Action", "Frustrated farmers resort to illegal electric fencing, poisoning, and open well traps."),
        ("Public Panic & Mobbing", "Rumors trigger frantic crowds, blocking rescue teams and agitating cornered carnivores."),
        ("Urgent Imperative", "A digital bridge is needed to warn villagers, dispatch rangers, and eliminate hostility.")
    ], "THE FATAL RISK", ACCENT_RED)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 3: The Flaws of Current Systems
    # ══════════════════════════════════════════════════════════════════════
    s3 = add_blank_slide(prs)
    add_header(s3, 3, "Bottleneck Analysis", "Why Traditional Wildlife Management Systems Fail",
               "Manual, fragmented, and bureaucratic protocols cannot keep pace with nocturnal apex predator movements.")

    add_content_card(s3, 0.8, 2.1, 5.7, 2.2, "Delayed Telegraphic Reporting", [
        ("4 to 6 Hour Lag", "Sightings travel via phone calls and physical informers. By arrival, carnivores have moved 5+ km."),
        ("No Centralized Telemetry", "Field guard reports remain siloed in paper registers and localized phone groups.")
    ], "REACTIVE BLINDSPOT", ACCENT_RED)

    add_content_card(s3, 6.8, 2.1, 5.7, 2.2, "180-Day Compensation Agony", [
        ("Excessive Bureaucracy", "Farmers wait 6+ months for livestock ex-gratia compensation due to physical Panchnama audits."),
        ("Fuel for Retaliation", "Prolonged financial hardship breeds direct anger against wildlife preservation policies.")
    ], "ECONOMIC HARDSHIP", ACCENT_RED)

    add_content_card(s3, 0.8, 4.6, 5.7, 2.2, "Zero Predictive Intelligence", [
        ("Static Pin Maps", "Current forest maps show past incidents, offering zero forecast of where an animal is heading next."),
        ("Unwarned Villagers", "Farmers harvest crops unaware that a pride is resting 300 meters away in dense scrubland.")
    ], "ABSENCE OF FORECASTING", ACCENT_AMBER)

    add_content_card(s3, 6.8, 4.6, 5.7, 2.2, "Vernacular & Digital Divide", [
        ("English-Centric Apps", "Existing portals fail because local Maldhari pastoralists speak Gujarati and lack technical literacy."),
        ("No Edge Connectivity", "Jungle fringes suffer cellular dead zones where traditional web apps become unusable.")
    ], "ACCESSIBILITY BARRIER", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 4: The VanRakshak AI Paradigm
    # ══════════════════════════════════════════════════════════════════════
    s4 = add_blank_slide(prs)
    add_header(s4, 4, "Solution Paradigm", "VanRakshak AI: Autonomous Coexistence Architecture",
               "An integrated multi-agent ecosystem uniting Forest Range Officers, Field Beat Guards, and 200,000+ Villagers.")

    add_content_card(s4, 0.8, 2.1, 3.7, 3.6, "1. PROACTIVE PREDICTION", [
        ("Before Conflict Occurs", "Machine Learning models predict wildlife movement corridors and compute village vulnerability."),
        ("Spatio-Temporal ML", "Evaluates time of day, waterholes, livestock density, and historical movement paths."),
        ("Early Strategic Advantage", "Allows beat guards to position patrol units ahead of predator movement.")
    ], "ANTICIPATE", ACCENT_GREEN)

    add_content_card(s4, 4.8, 2.1, 3.7, 3.6, "2. INSTANT LIVE ALERTS", [
        ("During Sighting Incident", "Sub-second geo-targeted alerts dispatched in Gujarati, Hindi & English."),
        ("Multi-Channel Broadcast", "Automated IVR calls, geo-fenced SMS, siren triggers, and citizen radar updates."),
        ("Actionable Guidance", "Gives specific safety instructions: 'Keep livestock in pens', 'Avoid walking at dusk'.")
    ], "WARN & PROTECT", ACCENT_CYAN)

    add_content_card(s4, 8.8, 2.1, 3.7, 3.6, "3. RAPID RESTITUTION", [
        ("After Livestock Depredation", "Transforms 180-day manual paperwork into a 48-hour digital Direct Benefit Transfer."),
        ("AI Panchnama & Forensics", "Automated geotagged photo audit and puncture pattern verification."),
        ("Restoring Community Trust", "Immediate compensation eliminates the incentive for retaliatory killings.")
    ], "COMPENSATE", ACCENT_AMBER)

    # Bottom Stat Row
    add_stat_box(s4, 0.8, 5.9, 3.7, 1.2, "85% REDUCTION", "In Unexpected Encounters", "", ACCENT_GREEN)
    add_stat_box(s4, 4.8, 5.9, 3.7, 1.2, "48 HOURS SLA", "Fast-Track Digital Ex-Gratia", "", ACCENT_CYAN)
    add_stat_box(s4, 8.8, 5.9, 3.7, 1.2, "120+ VILLAGES", "Covered in Greater Gir Area", "", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 5: High-Level System Architecture
    # ══════════════════════════════════════════════════════════════════════
    s5 = add_blank_slide(prs)
    add_header(s5, 5, "Architecture Blueprint", "End-to-End System Architecture: 4-Tier Framework",
               "Distributed edge-to-cloud architecture designed for high availability, fault tolerance, and sub-second telemetry.")

    add_content_card(s5, 0.8, 2.1, 2.7, 4.8, "TIER 1: EDGE SENSING", [
        ("LoRaWAN Camera Traps", "PIR + Thermal triggers with on-device YOLO-tiny inference."),
        ("Bioacoustic Sensors", "Real-time acoustic analysis for carnivore vocalizations."),
        ("GPS Wildlife Collars", "Live satellite telemetry ingested via secure APIs."),
        ("Citizen Reports", "Crowdsourced sighting capture with automatic GPS tagging.")
    ], "INGESTION LAYER", ACCENT_GREEN)

    add_content_card(s5, 3.8, 2.1, 2.7, 4.8, "TIER 2: AI AGENT MESH", [
        ("Central Orchestrator", "Sequential state machine coordinating all 5 autonomous agents."),
        ("Movement Agent", "Random Forest corridor prediction and perimeter decay."),
        ("Alert Agent", "Trilingual payload compilation & multi-channel routing."),
        ("Response Agent", "Nearest patrol dispatch & equipment SOP."),
        ("Compensation Agent", "Panchnama verification & DBT pipeline.")
    ], "INTELLIGENCE LAYER", ACCENT_CYAN)

    add_content_card(s5, 6.8, 2.1, 2.7, 4.8, "TIER 3: STREAMING ENGINE", [
        ("WebSocket Engine", "High-concurrency async daemon running on Port 8765."),
        ("SSE Fallback Stream", "HTTP Server-Sent Events for bandwidth-constrained rural networks."),
        ("REST API Layer", "FastAPI / Flask endpoints for secure CRUD & state inspection."),
        ("In-Memory State Cache", "Zero-lock synchronization across connected mobile & desktop devices.")
    ], "COMMUNICATION BUS", ACCENT_AMBER)

    add_content_card(s5, 9.8, 2.1, 2.7, 4.8, "TIER 4: UNIFIED PORTALS", [
        ("Officer Command GIS", "Interactive Leaflet map, threat overrides, patrol dispatch, and audit trail."),
        ("Citizen Coexistence PWA", "On-demand Safety Radar, Gujarati localization, 1926 SOS speed dial."),
        ("Beat Guard Mobile View", "Field incident check-in and digital Panchnama capture.")
    ], "STAKEHOLDER INTERFACES", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 6: The 5-Agent Collaborative AI Mesh
    # ══════════════════════════════════════════════════════════════════════
    s6 = add_blank_slide(prs)
    add_header(s6, 6, "Multi-Agent AI", "The 5-Agent Collaborative AI Collective",
               "Specialized, autonomous AI agents executing in an orchestrated pipeline with Human-in-the-Loop governance.")

    add_content_card(s6, 0.8, 2.1, 3.7, 2.2, "1. MovementAgent", [
        ("Trajectory Modeling", "Evaluates velocity, directional bias, and waterhole attraction."),
        ("Boundary Incursion", "Flags when wildlife approaches within 3km of village perimeters.")
    ], "SPATIAL PREDICTION", ACCENT_GREEN)

    add_content_card(s6, 4.8, 2.1, 3.7, 2.2, "2. AlertAgent", [
        ("Trilingual Synthesis", "Drafts contextual warnings in Gujarati, Hindi & English."),
        ("Channel Selection", "Routes critical alerts to IVR calls, SMS, and village sirens.")
    ], "BROADCAST ENGINE", ACCENT_CYAN)

    add_content_card(s6, 8.8, 2.1, 3.7, 2.2, "3. ResponseAgent", [
        ("Patrol Dispatch", "Assigns closest Rapid Response Team (RRT) based on Haversine distance."),
        ("Equipment Checklist", "Prescribes rescue gear (tranquilizer, cage, spotlight vehicle).")
    ], "LOGISTICS & DISPATCH", ACCENT_AMBER)

    add_content_card(s6, 0.8, 4.6, 3.7, 2.2, "4. CompensationAgent", [
        ("Digital Panchnama", "Audits geotagged evidence, vet autopsy docs, and witness sign-offs."),
        ("Automated Tariff", "Calculates Gujarat Forest Dept ex-gratia amount in 48 hours.")
    ], "FINANCIAL RESTITUTION", ACCENT_GREEN)

    add_content_card(s6, 4.8, 4.6, 3.7, 2.2, "5. HotspotAgent", [
        ("DBSCAN Spatial Clustering", "Identifies emerging conflict clusters and migratory choke points."),
        ("Dynamic Risk Recalibration", "Updates baseline vulnerability scores across 120+ villages.")
    ], "LANDSCAPE ANALYTICS", ACCENT_CYAN)

    add_content_card(s6, 8.8, 4.6, 3.7, 2.2, "Human-in-the-Loop (HITL)", [
        ("Officer Oversight", "High-severity actions require one-click Range Forest Officer approval."),
        ("Immutable Audit Log", "All agent recommendations and officer overrides are permanently recorded.")
    ], "SAFETY GOVERNANCE", ACCENT_RED)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 7: Agent 1: Movement & Trajectory Predictor
    # ══════════════════════════════════════════════════════════════════════
    s7 = add_blank_slide(prs)
    add_header(s7, 7, "Agent Deep Dive · Movement", "Agent 1: Movement & Trajectory Predictor",
               "Utilizing Random Forest machine learning and spatial decay physics to anticipate predator transit paths.")

    add_content_card(s7, 0.8, 2.1, 5.7, 4.8, "Machine Learning Classification", [
        ("Algorithm", "Supervised Random Forest Classifier trained on spatio-temporal sighting telemetry."),
        ("Classification Target", "3-Class Risk Zone: HIGH (red), MEDIUM (amber), LOW (green)."),
        ("7-Dimensional Feature Vector", "1. Recency-weighted sighting frequency\n2. Distance to nearest human settlement\n3. Time-of-day behavioral risk index\n4. Historical 30-day incident density\n5. Livestock corral density in sector\n6. Proximity to perennial waterbodies\n7. Vegetative cover and terrain roughness."),
        ("Inference Speed", "< 15 milliseconds execution time per detection event.")
    ], "ML ARCHITECTURE & FEATURES", ACCENT_GREEN)

    add_content_card(s7, 6.8, 2.1, 5.7, 4.8, "Perimeter Decay & Buffer Zones", [
        ("Dynamic Buffer Thresholds", "Evaluates exponential distance decay relative to village outer boundaries:"),
        ("Critical Zone (< 0.8 km)", "Carnivore within immediate village periphery. Automatic priority escalation to Alert & Response agents."),
        ("High Alert Zone (0.8 - 1.5 km)", "Active predator movement monitored. Pre-alert sent to village beat guard and sarpanch."),
        ("Advisory Zone (1.5 - 3.0 km)", "Normal territorial movement; logged into spatial hotspot queue."),
        ("Nocturnal Multiplier", "Risk scores scale by 1.8x between 19:00 - 05:30 to account for apex predator nocturnal hunting patterns.")
    ], "PHYSICS & SPATIAL DECAY", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 8: Agent 2: Trilingual Multi-Channel Alert Engine
    # ══════════════════════════════════════════════════════════════════════
    s8 = add_blank_slide(prs)
    add_header(s8, 8, "Agent Deep Dive · Alerts", "Agent 2: Trilingual Multi-Channel Alert Engine",
               "Generating culturally resonant, localized warnings delivered to vulnerable villagers in under 1 second.")

    add_content_card(s8, 0.8, 2.1, 5.7, 4.8, "Vernacular Language Synthesis", [
        ("Zero Cultural Barrier", "Alerts are automatically generated in native Gujarati (ગુજરાતી), Hindi & English."),
        ("Sample Gujarati Output", "'ચેતવણી: સાસણ ગીર સીમ વિસ્તારમાં સિંહની હિલચાલ નોંધાઈ છે (૦.૮ કિમી). પશુધનને વાડામાં રાખો. રાત્રે બહાર જવાનું ટાળો.'"),
        ("Sample English Output", "'WARNING: Asiatic Lion movement recorded within 0.8 km of Sasan Gir perimeter. Secure livestock in covered pens. Avoid night transit.'"),
        ("Contextual Advisories", "Includes actionable survival guidelines tailored to predator species (Lion vs Leopard).")
    ], "LOCALIZATION MATRIX", ACCENT_GREEN)

    add_content_card(s8, 6.8, 2.1, 5.7, 4.8, "Multi-Tier Dispatch Pipeline", [
        ("Tier A: Critical Alert (< 1 km)", "Automated Gujarati IVR Voice Call to registered village mobile numbers + Village siren trigger + High-priority SMS."),
        ("Tier B: High Alert (1 - 2 km)", "Geo-fenced SMS broadcast to all SIMs registered within cell tower sectors + WhatsApp Community Broadcast."),
        ("Tier C: Advisory Notice (> 2 km)", "Citizen Web Portal update + Range Forest Beat Guard patrol bulletin."),
        ("Delivery Latency", "Average broadcast dissemination completed within 800 milliseconds from AI verification.")
    ], "OMNICHANNEL DELIVERY", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 9: Agent 3: Rapid Response Team (RRT) Dispatcher
    # ══════════════════════════════════════════════════════════════════════
    s9 = add_blank_slide(prs)
    add_header(s9, 9, "Agent Deep Dive · Logistics", "Agent 3: Rapid Response Team (RRT) Dispatcher",
               "Intelligent field logistics: dynamic shortest-path patrol routing, resource allocation, and SOP generation.")

    add_content_card(s9, 0.8, 2.1, 5.7, 4.8, "Dynamic Beat Assignment", [
        ("Haversine Proximity Calculation", "Continuously calculates shortest terrain path from active patrol vehicles to the sighting coordinates."),
        ("Vehicle Status Awareness", "Tracks patrol unit status in real time: Available, In Transit, On Scene, or Relocating."),
        ("Automated Route Guidance", "Dispatches turn-by-turn navigation coordinates to the patrol vehicle tablet terminal."),
        ("Estimated Time of Arrival (ETA)", "Calculates realistic jungle transit ETA taking seasonal dirt tracks and river crossings into account.")
    ], "DISPATCH INTELLIGENCE", ACCENT_AMBER)

    add_content_card(s9, 6.8, 2.1, 5.7, 4.8, "Adaptive SOP & Equipment Checklist", [
        ("Species-Specific Protocols", "Automatically selects appropriate operational equipment based on predator category:"),
        ("Lion Encounter Kit", "Reinforced transport cage, tranquilizer dart rifle with ketamine dosage, searchlight vehicle, nylon nets."),
        ("Leopard Rescue Kit", "Hydraulic squeeze cage, trap box, pole syringe, protective bite suits, thermal drone."),
        ("Human-in-the-Loop Verification", "Range Forest Officer (RFO) receives a one-click 'Approve Dispatch' modal with full situational intelligence before sirens trigger.")
    ], "FIELD READINESS", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 10: Agent 4: Fast-Track Compensation Engine
    # ══════════════════════════════════════════════════════════════════════
    s10 = add_blank_slide(prs)
    add_header(s10, 10, "Agent Deep Dive · Restitution", "Agent 4: Fast-Track Digital Compensation Engine",
               "Transforming 180-day bureaucratic trauma into a transparent 48-hour Direct Benefit Transfer (DBT).")

    add_content_card(s10, 0.8, 2.1, 5.7, 4.8, "Digital Panchnama Ingestion", [
        ("Field Evidence Upload", "Beat guard or affected farmer captures geotagged, timestamped photo evidence of the carcass directly via smartphone."),
        ("AI Forensic Wound Analysis", "Computer vision model analyzes puncture wound diameter and spacing to distinguish lion canine marks from leopard bites or feral dogs."),
        ("Document Automation", "Instantly compiles the Panchnama dossier including GPS coordinates, witness e-signatures, and beat officer sign-off."),
        ("Fraud Prevention", "Prevents duplicate claims by checking image EXIF hashes against existing claim databases.")
    ], "DIGITAL PANCHNAMA PIPELINE", ACCENT_GREEN)

    add_content_card(s10, 6.8, 2.1, 5.7, 4.8, "48-Hour DBT Ex-Gratia Settlement", [
        ("Tariff Rule Engine", "Applies Gujarat Forest Department gazetted compensation rates automatically:"),
        ("Milch Cattle (Cow / Buffalo)", "₹30,000 - ₹50,000 direct payout upon verified carnivore predation."),
        ("Goat / Sheep / Calves", "₹3,000 - ₹10,000 per head calculated instantly."),
        ("Transparent Claim Tracking", "Villagers receive a unique Tracking ID (e.g., CLM-8291) with real-time SMS progress updates."),
        ("Direct Bank Transfer", "Approved claims link directly to the farmer's Aadhaar-seeded bank account within 48 hours.")
    ], "DIRECT BENEFIT TRANSFER", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 11: Agent 5: Spatial Hotspot & Clustering Engine
    # ══════════════════════════════════════════════════════════════════════
    s11 = add_blank_slide(prs)
    add_header(s11, 11, "Agent Deep Dive · Spatial AI", "Agent 5: Spatial Hotspot & Clustering Engine",
               "DBSCAN spatial density clustering and Kernel Density Estimation for proactive landscape management.")

    add_content_card(s11, 0.8, 2.1, 5.7, 4.8, "DBSCAN Spatial Clustering", [
        ("Density-Based Algorithm", "Executes DBSCAN (Density-Based Spatial Clustering of Applications with Noise) on sighting coordinates."),
        ("Hyperparameters", "Epsilon radius = 2.5 km, Minimum samples = 4 sightings within a rolling 14-day window."),
        ("Cluster Centroid Isolation", "Computes geographic centroid of recurring incursions to identify emerging conflict corridors."),
        ("Noise Elimination", "Filters out isolated, transient sightings from structural territorial shifts.")
    ], "CLUSTERING ALGORITHM", ACCENT_CYAN)

    add_content_card(s11, 6.8, 2.1, 5.7, 4.8, "Kernel Density & Village Risk Tuning", [
        ("KDE Heatmap Visualization", "Generates continuous spatial density surfaces showing seasonal migration patterns (Monsoon vs Summer)."),
        ("Dynamic Baseline Risk Tuning", "Automatically recalculates the baseline vulnerability index of surrounding villages:"),
        ("High-Risk Villages", "Sasan Gir (88%), Dhari (76%), Talala (65%), Visavadar (58%)."),
        ("Infrastructure Recommendations", "Generates data-driven proposals for forest departments: optimal placement of solar high-mast lights and farm-well covers.")
    ], "LANDSCAPE INTELLIGENCE", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 12: Machine Learning & Mathematical Risk Formulation
    # ══════════════════════════════════════════════════════════════════════
    s12 = add_blank_slide(prs)
    add_header(s12, 12, "Data Science & Formula", "Mathematical Formulation: Composite Risk Engine",
               "A transparent, auditable, multi-factor mathematical formulation powering real-time risk classification.")

    # Formula Display Box
    add_card(s12, 0.8, 2.1, 11.733, 1.3, bg_color=BG_CARD_LIGHT, border_color=ACCENT_GREEN)
    tb_form = s12.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(1.1))
    tf_f = tb_form.text_frame
    p_f1 = tf_f.paragraphs[0]
    p_f1.text = "Conflict Risk Score = 0.30×P + 0.20×M + 0.15×T + 0.15×L + 0.10×H + 0.10×E"
    p_f1.font.name = FONT_HEADING
    p_f1.font.size = Pt(20)
    p_f1.font.bold = True
    p_f1.font.color.rgb = ACCENT_GREEN

    p_f2 = tf_f.add_paragraph()
    p_f2.text = "All component scores normalized to [0.0, 1.0]. High Risk: Score >= 0.70 | Medium Risk: 0.40 - 0.69 | Low Risk: < 0.40"
    p_f2.font.name = FONT_BODY
    p_f2.font.size = Pt(11)
    p_f2.font.color.rgb = TEXT_MUTED

    # 6 Component Cards
    add_content_card(s12, 0.8, 3.6, 3.7, 1.7, "0.30 · Proximity (P)", [
        ("Exponential Decay", "P = exp(-d / d0) where d is distance to village perimeter; approaches 1.0 when d < 0.5 km.")
    ], "CORE PROXIMITY", ACCENT_GREEN)

    add_content_card(s12, 4.8, 3.6, 3.7, 1.7, "0.20 · Movement Recency (M)", [
        ("Time Decay", "M = max(0, 1 - (delta_t / 360)); sightings in the last 60 minutes receive maximum weight.")
    ], "RECENCY WEIGHT", ACCENT_CYAN)

    add_content_card(s12, 8.8, 3.6, 3.7, 1.7, "0.15 · Time of Day (T)", [
        ("Diurnal Curve", "T = 0.95 during nocturnal hours (20:00 - 05:00); T = 0.20 during midday solar peak.")
    ], "BEHAVIORAL RHYTHM", ACCENT_AMBER)

    add_content_card(s12, 0.8, 5.5, 3.7, 1.7, "0.15 · Livestock Density (L)", [
        ("Vulnerability Factor", "Normalized cattle and goat population in surrounding open corrals (Maldhari Nesda).")
    ], "PREY ATTRACTION", ACCENT_GREEN)

    add_content_card(s12, 4.8, 5.5, 3.7, 1.7, "0.10 · Historical Incidents (H)", [
        ("30-Day Density", "Frequency of past conflict encounters recorded in the same 2km spatial grid cell.")
    ], "PAST ENCOUNTERS", ACCENT_CYAN)

    add_content_card(s12, 8.8, 5.5, 3.7, 1.7, "0.10 · Environment (E)", [
        ("Ecological Features", "Riparian river corridors, dense Prosopis juliflora scrub cover, and waterbody proximity.")
    ], "TERRAIN COVER", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 13: Real-Time Edge & Streaming Architecture
    # ══════════════════════════════════════════════════════════════════════
    s13 = add_blank_slide(prs)
    add_header(s13, 13, "Real-Time Telemetry", "Sub-Second Real-Time Synchronization Engine",
               "High-throughput WebSocket streaming (Port 8765) backed by Server-Sent Events (SSE) and zero-poll push.")

    add_content_card(s13, 0.8, 2.1, 5.7, 4.8, "WebSocket Push Architecture (Port 8765)", [
        ("AsyncIO WebSocket Server", "Persistent bi-directional connection between forest servers and client devices."),
        ("Instant Event Dispatch", "When an officer updates a threat level or a sensor triggers, payload pushes in < 50ms."),
        ("websocat & Browser Compatible", "Fully compatible with standard CLI diagnostic tools, mobile browsers, and desktop dashboards."),
        ("Zero Polling Overhead", "Eliminates wasteful continuous HTTP requests, reducing mobile battery consumption by 70%."),
        ("Heartbeat & Auto-Reconnect", "Automatic ping-pong liveness detection with 4-second exponential backoff reconnection.")
    ], "WEBSOCKET STREAM", ACCENT_CYAN)

    add_content_card(s13, 6.8, 2.1, 5.7, 4.8, "Fail-Safe SSE & Cross-Device Sync", [
        ("Server-Sent Events (/api/events)", "Automatic transparent fallback for 2G/3G mobile networks where WebSockets may be throttled."),
        ("Cross-Device Coherence", "Officer modifications on desktop instantly propagate to field guard phones and citizen radars."),
        ("Conflict Resolution", "Timestamped atomic event stream ensures all devices reflect the same single source of truth."),
        ("Bandwidth Optimized", "Payloads are ultra-compact JSON (< 200 bytes per event), ensuring operation even on weak rural signals.")
    ], "FAIL-SAFE RESILIENCE", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 14: Forest Officer Tactical Command Center
    # ══════════════════════════════════════════════════════════════════════
    s14 = add_blank_slide(prs)
    add_header(s14, 14, "Officer Dashboard", "Forest Officer Tactical Command Center",
               "Mission-critical operational awareness interface built for Range Forest Officers (RFOs) and Beat Guards.")

    add_content_card(s14, 0.8, 2.1, 5.7, 4.8, "Tactical GIS & Live Telemetry", [
        ("Interactive Leaflet GIS Map", "Real-time spatial visualization of wildlife GPS collar tracks, camera trap nodes, and patrol vehicles."),
        ("Layer Controls", "Toggle village safety perimeters, wildlife sanctuaries, historical hotspots, and perennial water holes."),
        ("Predator Proximity Vectors", "Displays live distance vectors and approaching bearings towards agricultural borders."),
        ("Live Status Badges", "Instant visual cues (Red/Critical, Amber/Medium, Green/Normal) across all monitored sectors.")
    ], "GIS MISSION CONTROL", ACCENT_GREEN)

    add_content_card(s14, 6.8, 2.1, 5.7, 4.8, "Operational Control & Governance", [
        ("Village Risk Overview Grid", "Grid displaying all regional villages with one-click manual threat level override capability."),
        ("Human-in-the-Loop Approval", "Incoming AI alerts and crowdsourced citizen sightings queue for officer verification."),
        ("RRT Dispatch Hub", "One-click deployment of Rapid Response Teams with automated equipment checklists."),
        ("Immutable Audit Trail", "Records officer actions, timestamped broadcast history, and incident response times.")
    ], "COMMAND & DISPATCH", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 15: Citizen Coexistence & Safety Portal
    # ══════════════════════════════════════════════════════════════════════
    s15 = add_blank_slide(prs)
    add_header(s15, 15, "Citizen Interface", "Citizen Coexistence & Safety Portal",
               "Vernacular, mobile-first interface designed to empower local villagers and pastoralist Maldharis.")

    add_content_card(s15, 0.8, 2.1, 5.7, 4.8, "On-Demand Village Safety Radar", [
        ("User-Triggered Evaluation", "Villagers select their village or tap 'Detect My Nearest Village' via GPS to instantly evaluate local safety."),
        ("Clear Threat Indicators", "Displays verified threat levels (HIGH / MEDIUM / LOW) and current distance to nearest carnivore."),
        ("No Auto-Flicker", "Evaluates on demand when requested by the user, eliminating jarring UI refreshes and conserving mobile data."),
        ("Trilingual UI", "Complete Gujarati language support (સાસણ ગીર, ધારી, તાલાલા) with clear iconography for low-literacy users.")
    ], "VILLAGE SAFETY RADAR", ACCENT_GREEN)

    add_content_card(s15, 6.8, 2.1, 5.7, 4.8, "Life-Saving Advisories & Emergency SOS", [
        ("Contextual Safety Advisories", "Dynamic recommendations based on current threat level (e.g., 'Lock cattle in pens', 'Carry torch at night')."),
        ("One-Touch 1926 SOS Helpline", "Direct speed dial button connecting to the Gujarat Forest Department emergency control room."),
        ("Fast Sighting Crowdsourcing", "Allows citizens to report animal sightings with automatic GPS capture and photo proof."),
        ("Claim Status Tracking", "Instant lookup of pending ex-gratia compensation claims with step-by-step progress bars.")
    ], "CITIZEN PROTECTION", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 16: Crowdsourced Sighting & Verification Workflow
    # ══════════════════════════════════════════════════════════════════════
    s16 = add_blank_slide(prs)
    add_header(s16, 16, "Community Intelligence", "Crowdsourced Sighting & Verification Workflow",
               "Transforming rural community vigilance into authenticated institutional early warning intelligence.")

    add_content_card(s16, 0.8, 2.1, 2.7, 4.8, "1. SIGHTING CAPTURE", [
        ("Farmer / Citizen", "Spots lion, leopard, or pugmark trail near farm borders."),
        ("Mobile App", "Captures photo proof, selects species, and auto-fetches precise GPS coordinates."),
        ("Offline Queue", "Saves report locally if cellular signal is weak, auto-syncing upon reconnect.")
    ], "COMMUNITY INPUT", ACCENT_GREEN)

    add_content_card(s16, 3.8, 2.1, 2.7, 4.8, "2. ANTI-SPOOF AI", [
        ("EXIF Verification", "Validates image capture timestamp and geolocation metadata."),
        ("Duplicate Detection", "Compares visual hashes to discard recycled or internet images."),
        ("Species Classifier", "Initial AI confidence check on uploaded photo.")
    ], "VALIDATION FILTER", ACCENT_CYAN)

    add_content_card(s16, 6.8, 2.1, 2.7, 4.8, "3. OFFICER TRIAGE", [
        ("Command Queue", "Report appears instantly in Forest Officer dashboard as 'Pending Review'."),
        ("One-Click Verify", "Range officer inspects photo, location, and beat guard notes."),
        ("Human Discretion", "Officer approves, modifies threat severity, or rejects fake reports.")
    ], "OFFICER APPROVAL", ACCENT_AMBER)

    add_content_card(s16, 9.8, 2.1, 2.7, 4.8, "4. GEO-BROADCAST", [
        ("Instant Alert", "Approved sighting triggers automated trilingual warnings to surrounding villages."),
        ("RRT Mobilized", "Nearest beat patrol vehicle receives dispatch coordinates."),
        ("Radar Updated", "Citizen safety radar reflects the new authenticated threat level.")
    ], "ACTION & WARNING", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 17: Edge Hardware & Off-Grid Sensor Fusion
    # ══════════════════════════════════════════════════════════════════════
    s17 = add_blank_slide(prs)
    add_header(s17, 17, "Hardware & Edge AI", "Edge Hardware & Off-Grid Sensor Fusion",
               "Ruggedized, low-power sensor nodes built for remote jungle corridors without reliable grid power or cellular coverage.")

    add_content_card(s17, 0.8, 2.1, 5.7, 4.8, "Edge AI Camera Traps", [
        ("Dual Sensor Fusion", "Passive Infrared (PIR) + Thermal Imaging sensors for day and night detection."),
        ("On-Device TinyML", "Runs lightweight YOLO-tiny model on edge compute (Raspberry Pi / Jetson Nano) to detect lions and leopards."),
        ("Bandwidth Reduction", "Transmits only verified metadata and compressed thumbnail crops rather than continuous video streams."),
        ("Solar & Battery", "Integrated 20W monocrystalline solar panel with 12V LiFePO4 battery pack for continuous 24/7 off-grid operation.")
    ], "CAMERA TRAP HARDWARE", ACCENT_GREEN)

    add_content_card(s17, 6.8, 2.1, 5.7, 4.8, "LoRaWAN & Bioacoustic Nodes", [
        ("Long-Range LoRaWAN Mesh", "Transmits telemetry across 15+ km line-of-sight directly to elevated forest watchtower gateways."),
        ("Bioacoustic Acoustic Nodes", "Continuous audio monitoring tuned for low-frequency carnivore roars and distress vocalizations."),
        ("Ruggedized Enclosures", "IP67 weatherproof and animal-resistant casings designed to withstand monsoon rains and dust."),
        ("Minimal Maintenance", "Designed for 2-year maintenance cycles in remote protected sanctuary zones.")
    ], "TELEMETRY & MESH", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 18: Security, Anti-Poaching & Wildlife Privacy
    # ══════════════════════════════════════════════════════════════════════
    s18 = add_blank_slide(prs)
    add_header(s18, 18, "Cybersecurity & Ethics", "Security, Anti-Poaching & Wildlife Privacy",
               "Ensuring real-time telemetry cannot be exploited by poachers, illegal wildlife syndicates, or unauthorized actors.")

    add_content_card(s18, 0.8, 2.1, 5.7, 4.8, "Zero-Knowledge Coordinate Obfuscation", [
        ("Poaching Risk Mitigation", "Exact GPS collar and camera trap coordinates are strictly restricted to authenticated Forest Officers."),
        ("Public Radar Obfuscation", "The public citizen portal only displays relative proximity (e.g., 'Within 1.2 km of village') without publishing raw lat/lon."),
        ("Spatial Noise Addition", "Public heatmap displays apply differential privacy noise to prevent pride den location tracking."),
        ("Zero Public Collar Feeds", "Radio telemetry frequencies and collar IDs are encrypted end-to-end.")
    ], "ANTI-POACHING SAFEGUARDS", ACCENT_RED)

    add_content_card(s18, 6.8, 2.1, 5.7, 4.8, "Role-Based Access Control & Integrity", [
        ("Role Hierarchy", "Strict permission tiers: Range Forest Officer (RFO), Beat Guard, Veterinarian, and Public Citizen."),
        ("Cryptographic Audit Trail", "All threat level modifications, alert dispatches, and compensation approvals are immutably logged."),
        ("Encrypted Telemetry", "WSS (WebSocket Secure) and HTTPS encryption across all sensor and client endpoints."),
        ("OWASP Compliance", "Sanitized API inputs, rate limiting, and protection against injection and spoofing attacks.")
    ], "DATA GOVERNANCE", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 19: Measurable Social & Ecological Impact
    # ══════════════════════════════════════════════════════════════════════
    s19 = add_blank_slide(prs)
    add_header(s19, 19, "Quantifiable Impact", "Measurable Outcomes: Safety, Ecology & Economics",
               "Projected field outcomes across human casualty prevention, wildlife conservation, and rural livelihood stability.")

    add_stat_box(s19, 0.8, 2.1, 5.7, 2.3, "-85% CASUALTIES", "Reduction in Human-Carnivore Encounters",
                 "Early warnings provide 20 to 45 minutes of actionable lead time for farmers to return safely from fields.", ACCENT_GREEN)

    add_stat_box(s19, 6.8, 2.1, 5.7, 2.3, "-90% RETALIATION", "Drop in Retaliatory Poisonings & Electrocutions",
                 "Fast-track compensation and real-time alerts eliminate economic despair and panic-driven retaliation.", ACCENT_AMBER)

    add_stat_box(s19, 0.8, 4.6, 5.7, 2.3, "48h vs 180 DAYS", "Ex-Gratia Compensation Disbursement",
                 "Reduces average claim settlement timeline from 6 months to 48 hours via digital Panchnama and DBT.", ACCENT_CYAN)

    add_stat_box(s19, 6.8, 4.6, 5.7, 2.3, "200,000+ CITIZENS", "Rural Villagers & Pastoralists Safeguarded",
                 "Covers 120+ peripheral villages across Gir Somnath, Amreli, Junagadh, and Bhavnagar districts.", ACCENT_GREEN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 20: Alignment with National Policy & UN SDGs
    # ══════════════════════════════════════════════════════════════════════
    s20 = add_blank_slide(prs)
    add_header(s20, 20, "Policy & Global Goals", "Alignment with National Policy & UN SDGs",
               "Directly supporting Government of India conservation mandates and United Nations Sustainable Development Goals.")

    add_content_card(s20, 0.8, 2.1, 5.7, 4.8, "National Policy Alignment", [
        ("Project Lion (Govt of India)", "Directly supports the national mission for ecological surveillance and habitat security of Asiatic lions."),
        ("MoEFCC HWC Guidelines 2023", "Fulfills Ministry of Environment, Forest and Climate Change protocols for technology-driven early warning and rapid relief."),
        ("Digital India Mission", "Replaces legacy paper-based forestry workflows with cloud-native, open-standard digital infrastructure."),
        ("Gujarat Forest Dept Mandate", "Empowers frontline forest staff and enhances grassroots institutional credibility among Maldhari tribes.")
    ], "INDIAN GOVERNMENT MISSIONS", ACCENT_GREEN)

    add_content_card(s20, 6.8, 2.1, 5.7, 4.8, "United Nations SDGs", [
        ("SDG 15: Life on Land", "Protecting endangered wildlife, halting biodiversity loss, and safeguarding fragile dry deciduous ecosystems."),
        ("SDG 11: Sustainable Communities", "Creating resilient, safe rural agrarian habitations coexisting peacefully alongside natural habitats."),
        ("SDG 3: Good Health & Well-being", "Eliminating traumatic injuries, fatalities, and acute psychological stress among agrarian workers."),
        ("SDG 9: Industry, Innovation & Infrastructure", "Pioneering state-of-the-art edge AI, IoT, and automated multi-agent systems for conservation.")
    ], "GLOBAL SUSTAINABILITY TARGETS", ACCENT_CYAN)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 21: Pan-India Scalability & Multi-Species Roadmap
    # ══════════════════════════════════════════════════════════════════════
    s21 = add_blank_slide(prs)
    add_header(s21, 21, "Expansion Roadmap", "Pan-India Scalability: Beyond Gir to Multi-Species Corridors",
               "A modular, extensible platform engineered for rapid adaptation across India's diverse wildlife conflict zones.")

    add_content_card(s21, 0.8, 2.1, 3.7, 4.8, "PHASE 1 (M1 - M6): GIR", [
        ("Geography", "Greater Gir Landscape (Gir Somnath, Amreli, Junagadh, Bhavnagar)."),
        ("Target Species", "Asiatic Lion (700+) & Indian Leopard (500+)."),
        ("Milestones", "Full deployment across 120 peripheral villages, integration with Gujarat Forest Range Offices, LoRaWAN gateway network.")
    ], "LION ECOSYSTEM (ACTIVE)", ACCENT_GREEN)

    add_content_card(s21, 4.8, 2.1, 3.7, 4.8, "PHASE 2 (M7 - M12): ELEPHANTS", [
        ("Geography", "Elephant Corridors in Assam, Odisha, and Western Ghats (Kerala/TN)."),
        ("Target Species", "Asian Elephant (Elephas maximus)."),
        ("Adaptations", "Seismic footstep sensors, railway track acoustic early warning systems to prevent train collisions, crop-raiding perimeter sirens.")
    ], "ELEPHANT LANDSCAPES", ACCENT_CYAN)

    add_content_card(s21, 8.8, 2.1, 3.7, 4.8, "PHASE 3 (M13 - M18): TIGERS", [
        ("Geography", "Sundarbans Mangroves, Jim Corbett, and Tadoba-Andhari buffer zones."),
        ("Target Species", "Bengal Tiger (Panthera tigris)."),
        ("Adaptations", "Pond barrier sensors for honey gatherers in Sundarbans, smart solar fencing triggers, multi-state tiger corridor tracking.")
    ], "TIGER RESERVES", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 22: Technology Stack, Production Feasibility & Cost Model
    # ══════════════════════════════════════════════════════════════════════
    s22 = add_blank_slide(prs)
    add_header(s22, 22, "Tech Stack & Feasibility", "Production-Ready Technology Stack & Feasibility",
               "Built with lightweight, high-performance, open-source technologies for minimal latency and low maintenance costs.")

    add_content_card(s22, 0.8, 2.1, 5.7, 4.8, "Modern, Zero-Bloat Tech Stack", [
        ("Backend Services", "Python 3.14, FastAPI (high-throughput async REST), Flask (lightweight SSR), AsyncIO WebSockets."),
        ("Machine Learning", "Scikit-Learn (Random Forest corridor classifier), NumPy, Spatial Analytics (DBSCAN & KDE)."),
        ("Frontend & GIS", "HTML5, Vanilla JavaScript (zero framework bloat), Leaflet.js interactive maps, CSS3 responsive grid."),
        ("Edge Computing", "YOLO-tiny on Raspberry Pi / Jetson Nano, LoRaWAN mesh communication protocol."),
        ("Deployment", "Docker containerization, Uvicorn/Gunicorn, cloud/edge hybrid deployment on Render/AWS.")
    ], "SOFTWARE ENGINEERING", ACCENT_GREEN)

    add_content_card(s22, 6.8, 2.1, 5.7, 4.8, "Feasibility & Cost Effectiveness", [
        ("Zero Recurring Licensing Fees", "Core platform built on 100% open-source software, eliminating expensive proprietary licenses."),
        ("Low-Cost Edge Hardware", "Off-the-shelf sensor nodes cost < ₹15,000 each, compared to ₹1,50,000 for legacy military-grade systems."),
        ("Low Operational Overhead", "Solar-powered nodes require minimal battery maintenance; cloud hosting costs under ₹8,000/month for 100 villages."),
        ("Government Integration", "APIs easily interface with existing State e-Governance portals, Aadhaar DBT, and Forest Department GIS systems.")
    ], "FINANCIAL VIABILITY", ACCENT_AMBER)

    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 23: Conclusion & Hackathon Pitch Call-to-Action
    # ══════════════════════════════════════════════════════════════════════
    s23 = add_blank_slide(prs)
    add_header(s23, 23, "Conclusion & Vision", "VanRakshak AI: Coexistence Through Intelligence",
               "A technological shield protecting India's rural communities while securing the future of the Asiatic Lion.")

    add_content_card(s23, 0.8, 2.1, 5.7, 3.5, "Why VanRakshak Wins", [
        ("End-to-End Working Prototype", "Fully functional multi-agent AI pipeline, real-time WebSocket telemetry, and dual stakeholder portals."),
        ("Addresses Real Human Needs", "Solves the farmer's fear of dusk encounters and the 6-month compensation delay."),
        ("Conservation Impact", "Stops retaliatory killings, ensuring the last 700+ Asiatic lions thrive in harmony with local communities."),
        ("Ready for Immediate Pilot", "Built and calibrated specifically for the real topography and villages of Gir Forest.")
    ], "COMPETITIVE ADVANTAGE", ACCENT_GREEN)

    add_content_card(s23, 6.8, 2.1, 5.7, 3.5, "The Vision Ahead", [
        ("Human-Wildlife Harmony", "Proving that technological innovation can turn conflict zones into models of peaceful coexistence."),
        ("Expanding Across India", "From the lions of Gir to the elephants of Assam and the tigers of Sundarbans."),
        ("National Pride", "VanRakshak: Honoring the frontline forest guards and indigenous Maldharis who protect our wild heritage.")
    ], "OUR PURPOSE", ACCENT_CYAN)

    # Bottom Contact & Demo Card
    add_card(s23, 0.8, 5.8, 11.733, 1.2, bg_color=BG_CARD_LIGHT, border_color=ACCENT_GREEN)
    tb_c = s23.shapes.add_textbox(Inches(1.0), Inches(5.9), Inches(11.333), Inches(1.0))
    tf_c = tb_c.text_frame
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "THANK YOU!  ·  READY FOR LIVE DEMONSTRATION & TECHNICAL Q&A"
    p_c1.font.name = FONT_HEADING
    p_c1.font.size = Pt(16)
    p_c1.font.bold = True
    p_c1.font.color.rgb = ACCENT_GREEN

    p_c2 = tf_c.add_paragraph()
    p_c2.text = "Team VanRakshak  |  Source Code & Interactive Prototype Ready  |  Protecting the King of Gir"
    p_c2.font.name = FONT_BODY
    p_c2.font.size = Pt(12)
    p_c2.font.color.rgb = TEXT_WHITE
    p_c2.space_before = Pt(4)

    # Save presentation
    output_path = os.path.join(os.path.dirname(__file__), "VanRakshak_Hackathon_Pitch_Deck.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path} ({len(prs.slides)} slides)!")
    return output_path

if __name__ == "__main__":
    build_deck()
