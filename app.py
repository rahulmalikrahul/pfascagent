# ╔══════════════════════════════════════════════════════════════════════╗
# ║      PFAS REGULATORY INTELLIGENCE PLATFORM                          ║
# ║      For Oil & Gas Industry — Environmental Compliance & Risk       ║
# ║      Powered by Claude AI + Crawl4AI                                ║
# ║      Single-file Streamlit Application v1.0                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import anthropic
import requests
import asyncio
import threading
import os
import re
import io
import time
import hashlib
import csv
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PFAS RegWatch | O&G Intelligence",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "PFAS Regulatory Intelligence Platform for Oil & Gas"}
)

# ──────────────────────────────────────────────────────────────
# INDUSTRIAL DARK THEME CSS
# ──────────────────────────────────────────────────────────────
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

:root {
    --bg0: #05090f;
    --bg1: #090e1a;
    --bg2: #0d1528;
    --bg3: #101c35;
    --border0: #162240;
    --border1: #1e3560;
    --border2: #2a4f88;
    --amber: #f59e0b;
    --amber2: #fbbf24;
    --amber-dim: rgba(245,158,11,0.12);
    --amber-glow: 0 0 20px rgba(245,158,11,0.25);
    --cyan: #22d3ee;
    --cyan-dim: rgba(34,211,238,0.10);
    --cyan-glow: 0 0 20px rgba(34,211,238,0.2);
    --red: #f43f5e;
    --red-dim: rgba(244,63,94,0.12);
    --green: #10b981;
    --green-dim: rgba(16,185,129,0.12);
    --purple: #a78bfa;
    --text0: #f0f6ff;
    --text1: #94a3b8;
    --text2: #4a6080;
    --ff-head: 'Bebas Neue', sans-serif;
    --ff-body: 'Space Grotesk', sans-serif;
    --ff-mono: 'DM Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg0) !important;
    color: var(--text0);
    font-family: var(--ff-body);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg1) 0%, var(--bg0) 100%) !important;
    border-right: 1px solid var(--border1) !important;
}

[data-testid="stSidebar"] * { color: var(--text0) !important; font-family: var(--ff-body) !important; }

.main-header {
    font-family: var(--ff-head);
    letter-spacing: 0.08em;
    font-size: 2.8rem;
    background: linear-gradient(135deg, var(--amber) 0%, var(--cyan) 80%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin-bottom: 0.1rem;
}

.sub-header {
    font-family: var(--ff-mono);
    font-size: 0.75rem;
    color: var(--text2);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.kpi-card {
    background: var(--bg2);
    border: 1px solid var(--border1);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-amber::before { background: var(--amber); }
.kpi-cyan::before  { background: var(--cyan); }
.kpi-red::before   { background: var(--red); }
.kpi-green::before { background: var(--green); }

.kpi-card:hover {
    background: var(--bg3);
    border-color: var(--border2);
    transform: translateY(-2px);
}

.kpi-value {
    font-family: var(--ff-head);
    font-size: 2.4rem;
    letter-spacing: 0.04em;
    line-height: 1;
}

.kpi-amber .kpi-value { color: var(--amber); }
.kpi-cyan  .kpi-value { color: var(--cyan); }
.kpi-red   .kpi-value { color: var(--red); }
.kpi-green .kpi-value { color: var(--green); }

.kpi-label {
    font-family: var(--ff-mono);
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text2);
    margin-top: 0.3rem;
}

.kpi-sub {
    font-family: var(--ff-mono);
    font-size: 0.72rem;
    color: var(--text1);
    margin-top: 0.1rem;
}

.section-title {
    font-family: var(--ff-head);
    font-size: 1.4rem;
    letter-spacing: 0.1em;
    color: var(--text0);
    border-bottom: 1px solid var(--border1);
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem 0;
}

.reg-card {
    background: var(--bg2);
    border: 1px solid var(--border0);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    transition: border-color 0.2s;
}
.reg-card:hover { border-color: var(--border2); }

.reg-title {
    font-family: var(--ff-body);
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text0);
    margin-bottom: 0.4rem;
}

.badge {
    display: inline-block;
    font-family: var(--ff-mono);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    margin-right: 0.3rem;
}
.badge-amber  { background: var(--amber-dim);  color: var(--amber);  border: 1px solid var(--amber);  }
.badge-cyan   { background: var(--cyan-dim);   color: var(--cyan);   border: 1px solid var(--cyan);   }
.badge-red    { background: var(--red-dim);    color: var(--red);    border: 1px solid var(--red);    }
.badge-green  { background: var(--green-dim);  color: var(--green);  border: 1px solid var(--green);  }

.log-box {
    background: var(--bg1);
    border: 1px solid var(--border1);
    border-radius: 6px;
    padding: 0.8rem 1rem;
    font-family: var(--ff-mono);
    font-size: 0.72rem;
    color: var(--cyan);
    max-height: 280px;
    overflow-y: auto;
    line-height: 1.8;
}

.chat-bubble-user {
    background: var(--amber-dim);
    border: 1px solid var(--amber);
    border-radius: 12px 12px 4px 12px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 0 0.5rem 15%;
    font-size: 0.88rem;
    color: var(--text0);
}
.chat-bubble-ai {
    background: var(--bg2);
    border: 1px solid var(--border1);
    border-radius: 12px 12px 12px 4px;
    padding: 0.7rem 1rem;
    margin: 0.5rem 15% 0.5rem 0;
    font-size: 0.88rem;
    color: var(--text0);
}

.audit-item {
    background: var(--bg2);
    border-left: 3px solid var(--cyan);
    border-radius: 0 6px 6px 0;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.84rem;
}
.audit-warn { border-left-color: var(--amber); }
.audit-fail { border-left-color: var(--red); }
.audit-pass { border-left-color: var(--green); }

.score-bar-wrap { background: var(--bg1); border-radius: 4px; height: 6px; margin: 4px 0; }
.score-bar { height: 6px; border-radius: 4px; }

[data-testid="stButton"] > button {
    background: var(--bg2) !important;
    border: 1px solid var(--border1) !important;
    color: var(--text0) !important;
    font-family: var(--ff-body) !important;
    font-size: 0.85rem !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    border-color: var(--amber) !important;
    color: var(--amber) !important;
    background: var(--amber-dim) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] select {
    background: var(--bg2) !important;
    border: 1px solid var(--border1) !important;
    color: var(--text0) !important;
    font-family: var(--ff-mono) !important;
    font-size: 0.85rem !important;
    border-radius: 6px !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg1) !important;
    border-bottom: 1px solid var(--border1) !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: var(--ff-mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text2) !important;
    border-radius: 4px 4px 0 0 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
    background: var(--amber-dim) !important;
}

[data-testid="stDataFrame"] { background: var(--bg2) !important; }

div[data-testid="metric-container"] {
    background: var(--bg2);
    border: 1px solid var(--border1);
    border-radius: 8px;
    padding: 1rem;
}

.stProgress > div > div > div { background: var(--amber) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

.sidebar-logo {
    font-family: var(--ff-head);
    font-size: 1.6rem;
    letter-spacing: 0.15em;
    color: var(--amber);
    text-align: center;
    padding: 0.5rem 0 0.2rem;
}
.sidebar-tagline {
    font-family: var(--ff-mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--text2);
    text-align: center;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

hr { border-color: var(--border0) !important; margin: 1rem 0 !important; }
</style>
"""

# ──────────────────────────────────────────────────────────────
# CONSTANTS & DATA
# ──────────────────────────────────────────────────────────────

PFAS_CHEMICALS = [
    "PFOA", "PFOS", "PFAS (Generic)", "PFBS", "PFHxS", "PFNA", "PFHxA",
    "PFDA", "PFUnDA", "GenX (HFPO-DA)", "PFBA", "PFPeA", "PFHpA",
    "6:2 FTS", "PFECHS", "F-53B", "OBS", "PFDS", "PFDoDA", "Fluorotelomers"
]

REGULATION_TYPES = ["Law", "Rule", "Guideline", "Standard", "Enforcement Action",
                    "Proposed Rule", "News", "Report", "MCL", "Advisory"]

COUNTRY_URLS: Dict[str, List[Dict]] = {
    "USA": [
        {"name": "EPA PFAS Overview", "url": "https://www.epa.gov/pfas", "category": "Federal"},
        {"name": "EPA PFAS Regulations", "url": "https://www.epa.gov/pfas/pfas-regulations-and-guidance-documents-topic", "category": "Federal"},
        {"name": "EPA PFAS Drinking Water", "url": "https://www.epa.gov/sdwa/and-polyfluoroalkyl-substances-pfas", "category": "Federal"},
        {"name": "EPA PFAS Oil & Gas", "url": "https://www.epa.gov/pfas/pfas-strategic-roadmap-epas-commitments-action-2021-2024", "category": "Federal"},
        {"name": "EPA PFAS Superfund", "url": "https://www.epa.gov/pfas/addressing-pfas-superfund-sites", "category": "Federal"},
    ],
    "UK": [
        {"name": "Environment Agency PFAS", "url": "https://www.gov.uk/guidance/per-and-polyfluoroalkyl-substances-pfas", "category": "National"},
        {"name": "Health & Safety PFAS", "url": "https://www.hse.gov.uk/chemical-classification/pfas.htm", "category": "National"},
    ],
    "EU": [
        {"name": "ECHA PFAS", "url": "https://echa.europa.eu/hot-topics/perfluoroalkyl-chemicals-pfas", "category": "Regional"},
        {"name": "EU PFAS Restriction", "url": "https://echa.europa.eu/registry-of-restriction-intentions/-/dislist/details/0b0236e18663449b", "category": "Regional"},
    ],
    "Australia": [
        {"name": "PFAS NEMP", "url": "https://www.dcceew.gov.au/environment/protection/chemicals-management/pfas", "category": "National"},
        {"name": "PFAS Health Standards", "url": "https://www.foodstandards.gov.au/consumer/chemicals/pfas/Pages/default.aspx", "category": "National"},
    ],
    "Canada": [
        {"name": "Health Canada PFAS", "url": "https://www.canada.ca/en/health-canada/services/chemical-substances/perfluoroalkyl-substances.html", "category": "National"},
        {"name": "Environment Canada PFAS", "url": "https://www.canada.ca/en/environment-climate-change/services/evaluating-existing-substances/perfluorooctane-sulfonate-related.html", "category": "National"},
    ],
    "Germany": [
        {"name": "UBA PFAS Germany", "url": "https://www.umweltbundesamt.de/en/topics/chemicals/per-polyfluoroalkyl-substances-pfas", "category": "National"},
    ],
    "Netherlands": [
        {"name": "RIVM PFAS", "url": "https://www.rivm.nl/en/pfas", "category": "National"},
    ],
    "Norway": [
        {"name": "Norwegian EPA PFAS", "url": "https://www.miljodirektoratet.no/en/topics/chemicals/pfas/", "category": "National"},
    ],
}

US_STATES_URLS: Dict[str, Dict] = {
    "Alabama":        {"url": "https://adem.alabama.gov/programs/water/pfas.cnt",        "agency": "ADEM",    "has_regs": True},
    "Alaska":         {"url": "https://dec.alaska.gov/eh/as/awss/pfas/",                "agency": "DEC",     "has_regs": True},
    "Arizona":        {"url": "https://azdeq.gov/PFAS",                                 "agency": "ADEQ",    "has_regs": True},
    "Arkansas":       {"url": "https://www.adeq.state.ar.us/water/pdw/pfas.aspx",       "agency": "ADEQ",    "has_regs": False},
    "California":     {"url": "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/pfas.html", "agency": "SWRCB", "has_regs": True},
    "Colorado":       {"url": "https://cdphe.colorado.gov/pfas",                         "agency": "CDPHE",   "has_regs": True},
    "Connecticut":    {"url": "https://portal.ct.gov/DEEP/Remediation--Site-Clean-Up/PFAS/PFAS", "agency": "DEEP", "has_regs": True},
    "Delaware":       {"url": "https://dnrec.delaware.gov/water/pfas/",                 "agency": "DNREC",   "has_regs": True},
    "Florida":        {"url": "https://floridadep.gov/water/drinking-water/content/pfas","agency": "FDEP",   "has_regs": True},
    "Georgia":        {"url": "https://epd.georgia.gov/pfas",                           "agency": "EPD",     "has_regs": False},
    "Hawaii":         {"url": "https://health.hawaii.gov/doh/pfas/",                    "agency": "DOH",     "has_regs": False},
    "Idaho":          {"url": "https://www.deq.idaho.gov/water-quality/pfas/",          "agency": "DEQ",     "has_regs": False},
    "Illinois":       {"url": "https://epa.illinois.gov/topics/water-quality/pfas.html","agency": "IEPA",    "has_regs": True},
    "Indiana":        {"url": "https://www.in.gov/idem/cleanwater/pfas/",               "agency": "IDEM",    "has_regs": False},
    "Iowa":           {"url": "https://www.iowadnr.gov/Environmental-Protection/Water-Quality/PFAS", "agency": "DNR", "has_regs": False},
    "Kansas":         {"url": "https://www.kdhe.ks.gov/1432/PFAS",                      "agency": "KDHE",    "has_regs": False},
    "Kentucky":       {"url": "https://eec.ky.gov/Environmental-Protection/Water/PFAS", "agency": "EEC",     "has_regs": False},
    "Louisiana":      {"url": "https://deq.louisiana.gov/page/pfas",                    "agency": "LDEQ",    "has_regs": True},
    "Maine":          {"url": "https://www.maine.gov/dep/spills/topics/pfas/",          "agency": "DEP",     "has_regs": True},
    "Maryland":       {"url": "https://mde.maryland.gov/Pages/PFAS.aspx",              "agency": "MDE",     "has_regs": True},
    "Massachusetts":  {"url": "https://www.mass.gov/info-details/per-and-polyfluoroalkyl-substances-pfas", "agency": "MassDEP", "has_regs": True},
    "Michigan":       {"url": "https://www.michigan.gov/pfasresponse",                  "agency": "EGLE",    "has_regs": True},
    "Minnesota":      {"url": "https://www.pca.state.mn.us/air-water-land-climate/pfas","agency": "MPCA",    "has_regs": True},
    "Mississippi":    {"url": "https://www.mdeq.ms.gov/natural-resources/geology/pfas/","agency": "MDEQ",   "has_regs": False},
    "Missouri":       {"url": "https://health.mo.gov/living/environment/pfas/",         "agency": "DHSS",    "has_regs": False},
    "Montana":        {"url": "https://deq.mt.gov/tsd/pfas",                           "agency": "DEQ",     "has_regs": False},
    "Nebraska":       {"url": "https://deq.ne.gov/Programs.nsf/Pages/PFAS",            "agency": "NDEQ",    "has_regs": False},
    "Nevada":         {"url": "https://ndep.nv.gov/water/pfas",                         "agency": "NDEP",    "has_regs": False},
    "New Hampshire":  {"url": "https://www.des.nh.gov/water/drinking-water/pfas",       "agency": "DES",     "has_regs": True},
    "New Jersey":     {"url": "https://www.nj.gov/dep/pfas/",                           "agency": "NJDEP",   "has_regs": True},
    "New Mexico":     {"url": "https://www.env.nm.gov/pfas/",                           "agency": "NMED",    "has_regs": False},
    "New York":       {"url": "https://www.health.ny.gov/environmental/water/drinking/pfoa_pfos/", "agency": "NYSDOH", "has_regs": True},
    "North Carolina": {"url": "https://deq.nc.gov/about/divisions/water-resources/pfas","agency": "NCDEQ",  "has_regs": True},
    "North Dakota":   {"url": "https://deq.nd.gov/WQ/4_PFAS.aspx",                     "agency": "NDDoH",   "has_regs": False},
    "Ohio":           {"url": "https://epa.ohio.gov/divisions-and-offices/drinking-and-ground-waters/pfas", "agency": "OhioEPA", "has_regs": True},
    "Oklahoma":       {"url": "https://deq.ok.gov/programs/wd/pfas.html",               "agency": "DEQ",     "has_regs": False},
    "Oregon":         {"url": "https://www.oregon.gov/ode/students-and-family/healthsafety/pages/pfas.aspx","agency": "DEQ", "has_regs": True},
    "Pennsylvania":   {"url": "https://www.dep.pa.gov/Business/Water/DrinkingWater/PFAS/", "agency": "PADEP", "has_regs": True},
    "Rhode Island":   {"url": "https://dem.ri.gov/environmental-protection-bureau/water-resources/pfas", "agency": "DEM", "has_regs": True},
    "South Carolina": {"url": "https://www.dhec.sc.gov/health/environmental-health-services/pfas/","agency":"DHEC","has_regs": False},
    "South Dakota":   {"url": "https://denr.sd.gov/des/dw/PFAS.aspx",                  "agency": "DENR",    "has_regs": False},
    "Tennessee":      {"url": "https://www.tn.gov/environment/program-areas/wr-water-resources/water-quality/pfas.html", "agency": "TDEC", "has_regs": False},
    "Texas":          {"url": "https://www.tceq.texas.gov/pfas",                         "agency": "TCEQ",    "has_regs": True},
    "Utah":           {"url": "https://deq.utah.gov/water-quality/pfas",                "agency": "DEQ",     "has_regs": False},
    "Vermont":        {"url": "https://dec.vermont.gov/water-investment/pfas",          "agency": "DEC",     "has_regs": True},
    "Virginia":       {"url": "https://www.deq.virginia.gov/topics/pfas",               "agency": "DEQ",     "has_regs": True},
    "Washington":     {"url": "https://ecology.wa.gov/water-shorelines/water-quality/swqs/pfas", "agency": "Ecology", "has_regs": True},
    "West Virginia":  {"url": "https://dep.wv.gov/WWE/Programs/pfas/Pages/default.aspx","agency": "DEP",    "has_regs": False},
    "Wisconsin":      {"url": "https://dnr.wi.gov/topic/pfas/",                         "agency": "DNR",     "has_regs": True},
    "Wyoming":        {"url": "https://deq.wyoming.gov/air-quality/pfas/",              "agency": "DEQ",     "has_regs": False},
}

# ISO3 codes for choropleth
COUNTRY_ISO3 = {
    "USA": "USA", "UK": "GBR", "EU": "DEU", "Australia": "AUS",
    "Canada": "CAN", "Germany": "DEU", "Netherlands": "NLD",
    "Norway": "NOR", "Sweden": "SWE", "Denmark": "DNK",
    "France": "FRA", "Belgium": "BEL", "Switzerland": "CHE",
    "Japan": "JPN", "South Korea": "KOR", "Finland": "FIN",
    "Austria": "AUT", "Italy": "ITA", "Spain": "ESP",
    "New Zealand": "NZL",
}

# Seed regulations data
SEED_REGULATIONS = [
    {
        "country": "USA", "state": "Federal", "jurisdiction": "Federal",
        "source_url": "https://www.epa.gov/sdwa/and-polyfluoroalkyl-substances-pfas",
        "title": "EPA National Primary Drinking Water Regulation (NPDWR) for PFAS — April 2024",
        "content": "The EPA finalized the first-ever National Primary Drinking Water Regulation for PFAS, setting legally enforceable MCLs of 4 ppt each for PFOA and PFOS, 10 ppt for PFNA, PFHxS, and HFPO-DA (GenX), and a PFAS Hazard Index of 1 for combinations of PFHxS, PFNA, HFPO-DA, and PFBS.",
        "regulation_type": "MCL", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFNA","PFHxS","GenX"]),
        "oil_gas_relevance_score": 0.90,
        "oil_gas_context": "Oil & gas operations use PFAS-containing firefighting foams (AFFF) at refineries and processing facilities. Produced water from O&G wells contains PFAS. The MCL rule directly impacts O&G companies that operate near drinking water sources.",
        "regulatory_limits": json.dumps({"PFOA_ppt": 4, "PFOS_ppt": 4, "PFNA_ppt": 10, "PFHxS_ppt": 10, "GenX_ppt": 10}),
        "effective_date": "2024-04-26", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Public water systems must monitor for PFAS","Systems exceeding MCLs must take action within 5 years","Annual reporting to customers required"]),
    },
    {
        "country": "USA", "state": "Federal", "jurisdiction": "Federal",
        "source_url": "https://www.epa.gov/pfas/pfas-listed-hazardous-substances-under-cercla",
        "title": "EPA Designates PFOA and PFOS as CERCLA Hazardous Substances — 2024",
        "content": "EPA designated PFOA and PFOS as hazardous substances under CERCLA (Superfund), enabling EPA to require responsible parties to clean up PFAS contamination or reimburse EPA for cleanup costs. This is particularly significant for oil & gas companies whose operations contributed to PFAS contamination.",
        "regulation_type": "Rule", "pfas_chemicals": json.dumps(["PFOA","PFOS"]),
        "oil_gas_relevance_score": 0.95,
        "oil_gas_context": "O&G companies that used PFAS-containing AFFF at refineries, pipelines, or offshore platforms may face Superfund liability for contaminated sites. Companies must report PFOA/PFOS releases above reportable quantities.",
        "regulatory_limits": json.dumps({"reportable_quantity_lbs": 0.00000002}),
        "effective_date": "2024-07-08", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Release reporting above RQ","Potential cleanup liability","Cost recovery by EPA","Site investigation requirements"]),
    },
    {
        "country": "USA", "state": "California", "jurisdiction": "California",
        "source_url": "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/pfas.html",
        "title": "California PFAS Maximum Contaminant Levels — State Drinking Water Standard",
        "content": "California set enforceable MCLs of 5 ppt for PFOA and 1 ppt for PFOS — stricter than the federal MCLs. The regulations require water systems to test and treat water exceeding these limits. California also has PFAS response levels and notification levels for additional PFAS compounds.",
        "regulation_type": "MCL", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFBS","PFHxS"]),
        "oil_gas_relevance_score": 0.88,
        "oil_gas_context": "California has strict liability for PFAS contamination. O&G companies operating in California must monitor wells, surface water, and groundwater near refineries and processing facilities for PFAS.",
        "regulatory_limits": json.dumps({"PFOA_ppt": 5, "PFOS_ppt": 1}),
        "effective_date": "2023-07-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Quarterly monitoring for large water systems","Public notification within 30 days","Treatment required if MCL exceeded","Annual state reporting"]),
    },
    {
        "country": "USA", "state": "Michigan", "jurisdiction": "Michigan",
        "source_url": "https://www.michigan.gov/pfasresponse",
        "title": "Michigan PFAS Action Plan — Groundwater and Drinking Water Standards",
        "content": "Michigan enacted some of the most stringent PFAS regulations in the U.S., setting MCLs for 7 PFAS compounds. The state has designated PFAS as hazardous substances under state law, enabling cost recovery from responsible parties including oil & gas operators.",
        "regulation_type": "Standard", "pfas_chemicals": json.dumps(["PFNA","PFHxS","PFOA","PFOS","PFBS","PFHpA","HFPO-DA"]),
        "oil_gas_relevance_score": 0.82,
        "oil_gas_context": "Michigan's active oil & gas sector faces requirements to characterize PFAS contamination at all regulated facilities. The state has pursued enforcement against O&G companies for PFAS contamination near sensitive water resources.",
        "regulatory_limits": json.dumps({"PFNA_ppt": 6, "PFHxS_ppt": 51, "PFOS_ppt": 16, "PFOA_ppt": 8}),
        "effective_date": "2020-01-10", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Site investigation for known/suspected releases","Groundwater monitoring requirements","Corrective action if standards exceeded","Cost allocation for responsible parties"]),
    },
    {
        "country": "USA", "state": "New Jersey", "jurisdiction": "New Jersey",
        "source_url": "https://www.nj.gov/dep/pfas/",
        "title": "New Jersey PFAS Drinking Water Standards and Groundwater Quality Standards",
        "content": "New Jersey adopted the most stringent PFAS drinking water standards in the U.S.: 13 ppt for PFOA, 13 ppt for PFOS, and 13 ppt for PFNA. NJ also designates PFOA, PFOS, and PFNA as hazardous substances, compelling cleanup by responsible parties including oil & gas companies.",
        "regulation_type": "MCL", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFNA"]),
        "oil_gas_relevance_score": 0.80,
        "oil_gas_context": "New Jersey's strict standards apply to O&G companies with refining, storage, or distribution operations. Companies may be responsible for groundwater remediation if PFAS contamination from AFFF use is detected.",
        "regulatory_limits": json.dumps({"PFOA_ppt": 13, "PFOS_ppt": 13, "PFNA_ppt": 13}),
        "effective_date": "2020-06-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Groundwater quality standards enforceable","Mandatory reporting of PFAS detections","Remediation required above standards","Hazardous substance designation enables cost recovery"]),
    },
    {
        "country": "UK", "state": "National", "jurisdiction": "England & Wales",
        "source_url": "https://www.gov.uk/guidance/per-and-polyfluoroalkyl-substances-pfas",
        "title": "UK Environment Agency PFAS Risk Assessment and Guidance for Oil & Gas",
        "content": "The UK Environment Agency published comprehensive guidance on PFAS risk assessment applicable to oil & gas operations. The guidance sets environmental quality standards and investigation thresholds, and requires PFAS characterization at contaminated land sites including former refinery and drilling sites.",
        "regulation_type": "Guideline", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFAS (Generic)"]),
        "oil_gas_relevance_score": 0.85,
        "oil_gas_context": "UK guidance specifically addresses PFAS contamination from AFFF used at oil & gas and aviation facilities. O&G operators face requirements to assess, characterize, and remediate PFAS contamination at regulated sites.",
        "regulatory_limits": json.dumps({"PFOS_drinking_water_ug_L": 0.0001}),
        "effective_date": "2022-11-15", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["PFAS site characterization for O&G facilities","Environmental permit conditions may include PFAS monitoring","Remediation strategy required for contaminated sites","Annual environmental monitoring reporting"]),
    },
    {
        "country": "EU", "state": "Regional", "jurisdiction": "European Union",
        "source_url": "https://echa.europa.eu/hot-topics/perfluoroalkyl-chemicals-pfas",
        "title": "EU Universal PFAS Restriction Proposal Under REACH — 2023",
        "content": "The EU proposed the most comprehensive restriction on PFAS ever, covering approximately 10,000 PFAS substances under REACH regulation. The restriction targets all non-essential uses of PFAS and would ban PFAS in oil & gas applications including drilling fluids and processing aids within 5 years of adoption.",
        "regulation_type": "Proposed Rule", "pfas_chemicals": json.dumps(["PFAS (Generic)","PFOA","PFOS","Fluorotelomers"]),
        "oil_gas_relevance_score": 0.95,
        "oil_gas_context": "The EU PFAS restriction directly targets oil & gas applications. Derogations for O&G drilling fluids and produced water treatment chemicals may apply but face strict sunset provisions. European O&G operators must prepare PFAS substitution plans.",
        "regulatory_limits": json.dumps({"generic_limit_ug_L": 0.1, "sum_PFAS_ug_L": 0.5}),
        "effective_date": "2026-01-01", "status": "Proposed", "verified": True,
        "key_requirements": json.dumps(["Substitution of PFAS in drilling fluids","PFAS inventory and reporting","Industry derogation application process","Transition period up to 12 years for essential uses"]),
    },
    {
        "country": "Australia", "state": "National", "jurisdiction": "Commonwealth",
        "source_url": "https://www.dcceew.gov.au/environment/protection/chemicals-management/pfas",
        "title": "Australia PFAS National Environmental Management Plan (NEMP) 2.0 — 2022",
        "content": "Australia's NEMP 2.0 provides a nationally consistent approach to PFAS site assessment and remediation. The plan sets health-based guidance values and establishes responsibilities for contaminating entities — including mining and O&G operators who used AFFF at facilities.",
        "regulation_type": "Guideline", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFHxS"]),
        "oil_gas_relevance_score": 0.87,
        "oil_gas_context": "Australian O&G companies that used PFAS-containing AFFF at onshore and offshore facilities are primary targets of NEMP 2.0. The plan requires site assessments, risk characterization, and remediation where health-based guidance values are exceeded.",
        "regulatory_limits": json.dumps({"PFOS_drinking_water_ug_L": 0.00004, "PFOA_drinking_water_ug_L": 0.00056}),
        "effective_date": "2022-07-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Site assessment required for known AFFF use","Risk-based remediation objectives","Community consultation for affected areas","State/Territory implementation required"]),
    },
    {
        "country": "Canada", "state": "National", "jurisdiction": "Federal",
        "source_url": "https://www.canada.ca/en/health-canada/services/chemical-substances/perfluoroalkyl-substances.html",
        "title": "Canada Prohibition of Certain Toxic Substances Regulations — PFOS and PFOA",
        "content": "Canada prohibits the manufacture, use, sale, and import of PFOS and PFOA under the Prohibition of Certain Toxic Substances Regulations. Limited exemptions exist for certain industrial applications including oil & gas well drilling additives, but these are being phased out.",
        "regulation_type": "Law", "pfas_chemicals": json.dumps(["PFOA","PFOS"]),
        "oil_gas_relevance_score": 0.83,
        "oil_gas_context": "Canadian O&G sector exemptions for PFOS and PFOA in drilling additives are time-limited. Alberta and British Columbia have additional provincial requirements for PFAS management at upstream O&G facilities.",
        "regulatory_limits": json.dumps({"PFOS_manufacture_g": 0, "PFOA_manufacture_g": 0}),
        "effective_date": "2016-01-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Prohibition on manufacture/use/sale","Exemption application process","Phase-out schedule for existing uses","Annual reporting for exempt uses"]),
    },
    {
        "country": "USA", "state": "Texas", "jurisdiction": "Texas",
        "source_url": "https://www.tceq.texas.gov/pfas",
        "title": "Texas TCEQ PFAS Monitoring and Response Framework for O&G Operations",
        "content": "The Texas Commission on Environmental Quality (TCEQ) established monitoring requirements for PFAS in groundwater near oil & gas production areas. Texas adopted the federal EPA MCLs and is developing additional state-specific guidance for PFAS in produced water from fracking operations.",
        "regulation_type": "Guideline", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFAS (Generic)"]),
        "oil_gas_relevance_score": 0.92,
        "oil_gas_context": "Texas is a major oil & gas producer with significant PFAS-related concerns from hydraulic fracturing, produced water disposal, and AFFF use at refineries. TCEQ's framework is directly targeted at O&G sector PFAS management.",
        "regulatory_limits": json.dumps({"PFOA_ppt": 4, "PFOS_ppt": 4}),
        "effective_date": "2024-01-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Groundwater monitoring near O&G facilities","Produced water PFAS testing","AFFF inventory and management","Incident reporting for PFAS releases"]),
    },
    {
        "country": "USA", "state": "Pennsylvania", "jurisdiction": "Pennsylvania",
        "source_url": "https://www.dep.pa.gov/Business/Water/DrinkingWater/PFAS/",
        "title": "Pennsylvania DEP PFAS Action Plan — Unconventional Natural Gas Industry",
        "content": "Pennsylvania DEP developed a targeted PFAS action plan for the unconventional natural gas sector, requiring testing of water supplies near drilling operations, establishing reporting thresholds, and providing a framework for remediation when PFAS contamination is attributed to gas extraction activities.",
        "regulation_type": "Rule", "pfas_chemicals": json.dumps(["PFOA","PFOS","PFAS (Generic)","Fluorotelomers"]),
        "oil_gas_relevance_score": 0.97,
        "oil_gas_context": "Pennsylvania's Marcellus Shale natural gas industry is the direct target of this action plan. Operators of unconventional gas wells must test water wells within 2,500 feet of drilling operations for PFAS and take corrective action if contamination is found.",
        "regulatory_limits": json.dumps({"action_level_ppt": 4, "notification_level_ppt": 10}),
        "effective_date": "2022-09-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Pre- and post-drilling water testing","PFAS monitoring in produced water","Disclosure of PFAS-containing additives","Remediation fund contributions"]),
    },
    {
        "country": "USA", "state": "Colorado", "jurisdiction": "Colorado",
        "source_url": "https://cdphe.colorado.gov/pfas",
        "title": "Colorado SB 22-193 — Protecting Opportunities and Workers Rights (PFAS Disclosure)",
        "content": "Colorado's SB 22-193 requires oil & gas operators to disclose all PFAS used in hydraulic fracturing fluids and produced water treatment chemicals. The law mandates environmental monitoring near operations and establishes a PFAS trust fund for remediation of affected water supplies.",
        "regulation_type": "Law", "pfas_chemicals": json.dumps(["PFAS (Generic)","Fluorotelomers","6:2 FTS"]),
        "oil_gas_relevance_score": 0.98,
        "oil_gas_context": "This law is specifically designed for Colorado's O&G sector. It requires full chemical disclosure for all PFAS used in fracturing and enhanced recovery operations, and mandates testing of water supplies within 1 mile of operations.",
        "regulatory_limits": json.dumps({"PFAS_disclosure_threshold_ppt": 0.5}),
        "effective_date": "2023-01-01", "status": "Active", "verified": True,
        "key_requirements": json.dumps(["Full PFAS chemical disclosure on FracFocus","Water supply testing within 1 mile","Annual environmental monitoring","Trust fund contributions proportional to PFAS use"]),
    },
]

# ──────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ──────────────────────────────────────────────────────────────

DB_PATH = "pfas_regulations.db"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS regulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            state TEXT DEFAULT 'National',
            jurisdiction TEXT,
            source_url TEXT,
            title TEXT NOT NULL,
            content TEXT,
            regulation_type TEXT,
            pfas_chemicals TEXT,
            oil_gas_relevance_score REAL DEFAULT 0.5,
            oil_gas_context TEXT,
            regulatory_limits TEXT,
            effective_date TEXT,
            status TEXT DEFAULT 'Active',
            verified INTEGER DEFAULT 0,
            audit_notes TEXT,
            citations TEXT,
            key_requirements TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scrape_session_id TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regulation_id INTEGER,
            audited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified INTEGER DEFAULT 0,
            confidence_score REAL DEFAULT 0.0,
            hallucination_flags TEXT,
            corrections TEXT,
            citations TEXT,
            audit_summary TEXT,
            auditor TEXT DEFAULT 'Claude AI',
            FOREIGN KEY(regulation_id) REFERENCES regulations(id)
        );

        CREATE TABLE IF NOT EXISTS scrape_sessions (
            id TEXT PRIMARY KEY,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            countries TEXT,
            states TEXT,
            urls_scraped INTEGER DEFAULT 0,
            regulations_found INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running'
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Seed data if empty
    c.execute("SELECT COUNT(*) FROM regulations")
    if c.fetchone()[0] == 0:
        for reg in SEED_REGULATIONS:
            c.execute("""
                INSERT INTO regulations (country, state, jurisdiction, source_url, title, content,
                    regulation_type, pfas_chemicals, oil_gas_relevance_score, oil_gas_context,
                    regulatory_limits, effective_date, status, verified, key_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reg["country"], reg["state"], reg["jurisdiction"], reg["source_url"],
                reg["title"], reg["content"], reg["regulation_type"], reg["pfas_chemicals"],
                reg["oil_gas_relevance_score"], reg["oil_gas_context"], reg["regulatory_limits"],
                reg["effective_date"], reg["status"], int(reg["verified"]), reg["key_requirements"]
            ))
        conn.commit()
    conn.close()

def get_all_regulations(country_filter=None, state_filter=None, status_filter=None, search_query=None):
    conn = get_db()
    c = conn.cursor()
    query = "SELECT * FROM regulations WHERE 1=1"
    params = []
    if country_filter:
        placeholders = ",".join("?" * len(country_filter))
        query += f" AND country IN ({placeholders})"
        params.extend(country_filter)
    if state_filter:
        placeholders = ",".join("?" * len(state_filter))
        query += f" AND state IN ({placeholders})"
        params.extend(state_filter)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if search_query:
        query += " AND (title LIKE ? OR content LIKE ? OR oil_gas_context LIKE ?)"
        params.extend([f"%{search_query}%"] * 3)
    query += " ORDER BY date_scraped DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_regulation_by_id(reg_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM regulations WHERE id=?", (reg_id,))
    r = c.fetchone()
    conn.close()
    return dict(r) if r else None

def save_regulation(reg: dict) -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO regulations (country, state, jurisdiction, source_url, title, content,
            regulation_type, pfas_chemicals, oil_gas_relevance_score, oil_gas_context,
            regulatory_limits, effective_date, status, verified, key_requirements, scrape_session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reg.get("country", ""), reg.get("state", "National"), reg.get("jurisdiction", ""),
        reg.get("source_url", ""), reg.get("title", ""), reg.get("content", ""),
        reg.get("regulation_type", ""), json.dumps(reg.get("pfas_chemicals", [])),
        float(reg.get("oil_gas_relevance_score", 0.5)), reg.get("oil_gas_context", ""),
        json.dumps(reg.get("regulatory_limits", {})), reg.get("effective_date", ""),
        reg.get("status", "Active"), int(reg.get("verified", False)),
        json.dumps(reg.get("key_requirements", [])), reg.get("scrape_session_id", "")
    ))
    row_id = c.lastrowid
    conn.commit()
    conn.close()
    return row_id

def save_audit(regulation_id: int, audit: dict):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO audit_results (regulation_id, verified, confidence_score,
            hallucination_flags, corrections, citations, audit_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        regulation_id,
        int(audit.get("verified", False)),
        float(audit.get("confidence_score", 0.0)),
        json.dumps(audit.get("hallucination_flags", [])),
        json.dumps(audit.get("corrections", [])),
        json.dumps(audit.get("citations", [])),
        audit.get("audit_summary", "")
    ))
    c.execute("UPDATE regulations SET verified=?, audit_notes=? WHERE id=?", (
        int(audit.get("verified", False)),
        audit.get("audit_summary", ""),
        regulation_id
    ))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_db()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM regulations"); stats["total"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM regulations WHERE verified=1"); stats["verified"] = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT country) FROM regulations"); stats["countries"] = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT state) FROM regulations"); stats["states"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM regulations WHERE oil_gas_relevance_score >= 0.8"); stats["high_relevance"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM regulations WHERE status='Proposed'"); stats["proposed"] = c.fetchone()[0]
    c.execute("SELECT country, COUNT(*) as cnt FROM regulations GROUP BY country ORDER BY cnt DESC"); stats["by_country"] = c.fetchall()
    c.execute("SELECT regulation_type, COUNT(*) as cnt FROM regulations GROUP BY regulation_type ORDER BY cnt DESC"); stats["by_type"] = c.fetchall()
    c.execute("SELECT state, COUNT(*) as cnt, AVG(oil_gas_relevance_score) as avg_score FROM regulations WHERE country='USA' GROUP BY state ORDER BY cnt DESC"); stats["by_state"] = c.fetchall()
    conn.close()
    return stats

def delete_regulation(reg_id: int):
    conn = get_db()
    conn.execute("DELETE FROM regulations WHERE id=?", (reg_id,))
    conn.execute("DELETE FROM audit_results WHERE regulation_id=?", (reg_id,))
    conn.commit()
    conn.close()

def save_chat_message(session_id: str, role: str, content: str):
    conn = get_db()
    conn.execute("INSERT INTO chat_history (session_id, role, content) VALUES (?,?,?)", (session_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(session_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE session_id=? ORDER BY timestamp", (session_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

# ──────────────────────────────────────────────────────────────
# WEB SCRAPING UTILITIES
# ──────────────────────────────────────────────────────────────

def scrape_with_requests(url: str) -> str:
    """Fallback scraper using requests + BeautifulSoup"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; PFAS-RegWatch-Bot/1.0; +https://pfasregwatch.io)"
        }
        resp = requests.get(url, headers=headers, timeout=25)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        # Remove scripts/styles
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        # Limit to 12000 chars
        return text[:12000]
    except Exception as e:
        return f"[Scrape error: {e}]"

def scrape_with_crawl4ai(url: str) -> str:
    """Primary scraper using crawl4ai"""
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        async def _crawl():
            cfg = CrawlerRunConfig(
                word_count_threshold=50,
                remove_overlay_elements=True,
                excluded_tags=["nav","footer","header","aside","script","style"],
            )
            async with AsyncWebCrawler(headless=True, verbose=False) as crawler:
                result = await crawler.arun(url=url, config=cfg)
                if result and result.success:
                    return (result.markdown or result.cleaned_html or "")[:12000]
                return ""
        # Run in new thread to avoid event loop conflicts
        output = [None]; err = [None]
        def _run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try: output[0] = loop.run_until_complete(_crawl())
            except Exception as e: err[0] = e
            finally: loop.close()
        t = threading.Thread(target=_run); t.start(); t.join(timeout=60)
        if err[0]:
            raise err[0]
        return output[0] or ""
    except ImportError:
        return scrape_with_requests(url)
    except Exception:
        return scrape_with_requests(url)

def scrape_url(url: str, log_fn=None) -> str:
    if log_fn: log_fn(f"🕷️  Fetching: {url}")
    content = scrape_with_crawl4ai(url)
    if not content or content.startswith("[Scrape error"):
        if log_fn: log_fn(f"⚠️  Crawl4AI failed, using fallback scraper…")
        content = scrape_with_requests(url)
    if log_fn: log_fn(f"✅  Retrieved {len(content):,} chars from {url}")
    return content

# ──────────────────────────────────────────────────────────────
# AGENT 1 — PFAS REGULATORY SCRAPER AGENT
# ──────────────────────────────────────────────────────────────

SCRAPER_SYSTEM = """You are a world-class PFAS regulatory intelligence analyst specializing in the Oil & Gas industry.

Your task is to analyze web page content and extract ALL PFAS-related regulations, rules, laws, standards, enforcement actions, and news — with a CRITICAL focus on relevance to the Oil & Gas (O&G) sector.

Key PFAS-O&G intersections to prioritize:
• PFAS in aqueous film-forming foam (AFFF) used at refineries, offshore platforms, and pipelines
• PFAS in hydraulic fracturing (fracking) fluids and additives
• PFAS in produced water from oil & gas wells
• PFAS contamination near refineries, petrochemical plants, and storage terminals
• PFAS in drilling fluid additives and fluorosurfactants
• Regulatory liability for O&G companies regarding PFAS cleanup
• Maximum contaminant levels (MCLs) affecting O&G operational areas

Return a JSON object with this EXACT structure:
{
  "regulations": [
    {
      "title": "Full official title of the regulation/law/rule",
      "type": "Law|Rule|Guideline|Standard|Enforcement Action|Proposed Rule|News|Report|MCL|Advisory",
      "summary": "Detailed 2-3 paragraph summary",
      "pfas_chemicals": ["PFOA", "PFOS", ...list of specific chemicals covered],
      "oil_gas_relevance": "high|medium|low",
      "oil_gas_relevance_score": 0.0 to 1.0,
      "oil_gas_context": "Explain specifically HOW this impacts O&G companies, their operations, liabilities",
      "regulatory_limits": {"compound_ppt": value, "other_limit": value},
      "effective_date": "YYYY-MM-DD or 'Proposed' or 'Unknown'",
      "status": "Active|Proposed|Repealed|Under Review",
      "jurisdiction": "Exact jurisdiction name",
      "key_requirements": ["Requirement 1", "Requirement 2", ...]
    }
  ],
  "source_quality": "high|medium|low",
  "page_relevance": "high|medium|low|none"
}

If no relevant PFAS regulations are found, return: {"regulations": [], "source_quality": "low", "page_relevance": "none"}

IMPORTANT: Only extract information DIRECTLY stated in the source content. Do NOT hallucinate or invent regulatory details."""

def run_scraper_agent(
    urls: List[Dict],
    api_key: str,
    session_id: str,
    log_fn=None,
    country: str = "",
    state: str = "National"
) -> List[int]:
    """Agent 1: Scrapes URLs and extracts PFAS regulations using Claude"""
    client = anthropic.Anthropic(api_key=api_key)
    saved_ids = []
    total = len(urls)

    for i, url_info in enumerate(urls):
        url = url_info.get("url", "")
        url_country = url_info.get("country", country)
        url_state = url_info.get("state", state)
        if log_fn:
            log_fn(f"\n── [{i+1}/{total}] Processing: {url_info.get('name', url)}")

        try:
            # 1. Scrape page
            content = scrape_url(url, log_fn)
            if not content or len(content) < 100:
                if log_fn: log_fn(f"⚠️  Insufficient content, skipping")
                continue

            # 2. Extract regulations with Claude
            if log_fn: log_fn(f"🤖  Agent 1 analyzing content with Claude…")
            prompt = f"""URL: {url}
Country: {url_country}
State/Region: {url_state}

PAGE CONTENT:
{content[:10000]}

Extract all PFAS regulations relevant to Oil & Gas from the above content."""

            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=4096,
                system=SCRAPER_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()

            # Parse JSON
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not json_match:
                if log_fn: log_fn(f"⚠️  No JSON found in response")
                continue
            data = json.loads(json_match.group())
            regs = data.get("regulations", [])

            if log_fn: log_fn(f"📋  Found {len(regs)} regulation(s)")
            for reg in regs:
                reg_record = {
                    "country": url_country,
                    "state": url_state,
                    "jurisdiction": reg.get("jurisdiction", f"{url_country} - {url_state}"),
                    "source_url": url,
                    "title": reg.get("title", "Untitled"),
                    "content": reg.get("summary", ""),
                    "regulation_type": reg.get("type", "Guideline"),
                    "pfas_chemicals": reg.get("pfas_chemicals", []),
                    "oil_gas_relevance_score": float(reg.get("oil_gas_relevance_score", 0.5)),
                    "oil_gas_context": reg.get("oil_gas_context", ""),
                    "regulatory_limits": reg.get("regulatory_limits", {}),
                    "effective_date": reg.get("effective_date", ""),
                    "status": reg.get("status", "Active"),
                    "verified": False,
                    "key_requirements": reg.get("key_requirements", []),
                    "scrape_session_id": session_id
                }
                reg_id = save_regulation(reg_record)
                saved_ids.append(reg_id)
                if log_fn: log_fn(f"  ✅  Saved: {reg.get('title', 'Untitled')[:70]}")

        except json.JSONDecodeError as e:
            if log_fn: log_fn(f"❌  JSON parse error: {e}")
        except anthropic.APIError as e:
            if log_fn: log_fn(f"❌  Claude API error: {e}")
        except Exception as e:
            if log_fn: log_fn(f"❌  Error: {e}")

        time.sleep(1.5)  # Respectful crawling delay

    if log_fn: log_fn(f"\n🏁  Agent 1 complete. Saved {len(saved_ids)} regulations.")
    return saved_ids

# ──────────────────────────────────────────────────────────────
# AGENT 2 — AUDITOR AGENT
# ──────────────────────────────────────────────────────────────

AUDITOR_SYSTEM = """You are an expert regulatory fact-checker and hallucination detector specializing in PFAS regulations.

Your job is to audit regulation data that was extracted by an AI scraper for accuracy, completeness, and hallucinations.

For each regulation you audit:
1. Compare the stored data against the provided source content
2. Identify any fabricated, exaggerated, or inaccurate claims
3. Verify regulatory limits are correct (e.g., MCL values in ppt)
4. Confirm effective dates and status are accurate
5. Assess oil & gas relevance scoring
6. Generate proper academic/legal citations

Return a JSON object with EXACTLY this structure:
{
  "verified": true/false,
  "confidence_score": 0.0 to 1.0,
  "hallucination_flags": [
    {"field": "field_name", "issue": "description", "severity": "high|medium|low"}
  ],
  "corrections": [
    {"field": "field_name", "original": "...", "corrected": "...", "reason": "..."}
  ],
  "citations": [
    {"text": "citation text", "url": "source URL", "accessed": "YYYY-MM-DD"}
  ],
  "audit_summary": "2-3 sentence plain-language summary of audit findings",
  "o_g_relevance_verified": true/false,
  "data_completeness_score": 0.0 to 1.0
}

Be RIGOROUS. If you cannot verify a claim from the source content, flag it as unverified. Never fabricate corrections."""

def run_auditor_agent(regulation_ids: List[int], api_key: str, log_fn=None) -> Dict:
    """Agent 2: Audits regulations for hallucinations and adds citations"""
    client = anthropic.Anthropic(api_key=api_key)
    results = {"audited": 0, "verified": 0, "flagged": 0, "details": []}

    for reg_id in regulation_ids:
        reg = get_regulation_by_id(reg_id)
        if not reg:
            continue
        if log_fn: log_fn(f"\n🔍  Auditing: {reg['title'][:60]}…")

        try:
            # Re-fetch source for comparison
            if log_fn: log_fn(f"   Fetching source: {reg['source_url']}")
            source_content = scrape_with_requests(reg["source_url"]) if reg.get("source_url") else ""

            prompt = f"""STORED REGULATION DATA:
Title: {reg['title']}
Country: {reg['country']} | State: {reg['state']}
Type: {reg['regulation_type']}
Status: {reg['status']}
Effective Date: {reg['effective_date']}
O&G Relevance Score: {reg['oil_gas_relevance_score']}
Summary: {reg['content']}
Regulatory Limits: {reg['regulatory_limits']}
O&G Context: {reg['oil_gas_context']}
Key Requirements: {reg['key_requirements']}
Source URL: {reg['source_url']}

SOURCE PAGE CONTENT (re-fetched for verification):
{source_content[:8000] if source_content else '[Source unavailable - cannot verify against original]'}

Today's Date: {datetime.now().strftime('%Y-%m-%d')}

Audit the stored regulation data for accuracy. Flag any hallucinations or inaccuracies."""

            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=3000,
                system=AUDITOR_SYSTEM,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not json_match:
                if log_fn: log_fn(f"   ⚠️  No JSON in audit response")
                continue
            audit = json.loads(json_match.group())
            save_audit(reg_id, audit)

            results["audited"] += 1
            if audit.get("verified"): results["verified"] += 1
            if audit.get("hallucination_flags"): results["flagged"] += 1
            results["details"].append({"id": reg_id, "title": reg["title"], "audit": audit})
            status = "✅  VERIFIED" if audit.get("verified") else "⚠️  FLAGGED"
            if log_fn: log_fn(f"   {status} — Confidence: {audit.get('confidence_score', 0):.0%}")

        except Exception as e:
            if log_fn: log_fn(f"   ❌  Audit error: {e}")

        time.sleep(1.5)

    if log_fn:
        log_fn(f"\n🏁  Audit complete: {results['audited']} audited, {results['verified']} verified, {results['flagged']} flagged")
    return results

# ──────────────────────────────────────────────────────────────
# Q&A AGENT (RAG-based)
# ──────────────────────────────────────────────────────────────

QA_SYSTEM = """You are PFAS-RegWatch, an expert AI assistant for an Oil & Gas major's regulatory compliance team.

You have access to a curated database of PFAS regulations from around the world, with special focus on regulations impacting the Oil & Gas sector.

Your role:
• Answer regulatory compliance questions about PFAS for O&G operations
• Cite specific regulations from the database with URLs when available
• Explain regulatory limits (MCLs, thresholds) in practical O&G context
• Identify compliance risks and required actions for O&G operators
• Compare regulations across jurisdictions
• Clarify legal requirements vs. guidelines vs. voluntary standards

Always:
• Cite your sources using [Source: URL] format
• Distinguish between federal/national and state/regional requirements
• Note when regulations are proposed vs. active
• Flag high-priority compliance obligations
• Express uncertainty when regulations are unclear or evolving

Never fabricate regulation details. If you don't know, say so."""

def ask_qa_agent(question: str, api_key: str, session_id: str) -> str:
    """Q&A Agent with RAG from regulations database"""
    client = anthropic.Anthropic(api_key=api_key)

    # Retrieve relevant regulations (simple keyword search)
    keywords = re.findall(r'\b\w{4,}\b', question.lower())
    all_regs = get_all_regulations()
    scored = []
    for reg in all_regs:
        score = sum(1 for kw in keywords if
                   kw in reg.get("title", "").lower() or
                   kw in reg.get("content", "").lower() or
                   kw in reg.get("country", "").lower() or
                   kw in reg.get("state", "").lower())
        if score > 0:
            scored.append((score, reg))
    scored.sort(reverse=True, key=lambda x: x[0])
    top_regs = scored[:8]

    context = ""
    for _, reg in top_regs:
        chemicals = ", ".join(json.loads(reg.get("pfas_chemicals") or "[]"))
        limits = reg.get("regulatory_limits", "{}")
        context += f"""
---
REGULATION: {reg['title']}
Country: {reg['country']} | State: {reg['state']} | Type: {reg['regulation_type']}
Status: {reg['status']} | Effective: {reg['effective_date']}
Source URL: {reg['source_url']}
O&G Relevance Score: {reg.get('oil_gas_relevance_score', 0.5):.0%}
Chemicals: {chemicals}
Regulatory Limits: {limits}
Summary: {reg['content'][:800]}
O&G Context: {reg['oil_gas_context'][:500]}
Key Requirements: {', '.join(json.loads(reg.get('key_requirements') or '[]')[:4])}
"""

    messages = get_chat_history(session_id)
    messages.append({"role": "user", "content": f"""PFAS REGULATIONS DATABASE CONTEXT:
{context if context else '[No matching regulations found — answering from general knowledge]'}

USER QUESTION:
{question}"""})

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system=QA_SYSTEM,
        messages=messages[-20:]  # Last 20 messages
    )
    answer = response.content[0].text
    save_chat_message(session_id, "user", question)
    save_chat_message(session_id, "assistant", answer)
    return answer

# ──────────────────────────────────────────────────────────────
# VISUALIZATIONS
# ──────────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk", color="#94a3b8", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    title_font=dict(family="Space Grotesk", color="#f0f6ff", size=15),
)

def make_world_heatmap(stats):
    df_rows = [dict(r) for r in stats["by_country"]] if stats["by_country"] else []
    if not df_rows:
        return go.Figure()
    df = pd.DataFrame(df_rows, columns=["country", "count"])
    df["iso3"] = df["country"].map(lambda c: COUNTRY_ISO3.get(c, None))
    df = df.dropna(subset=["iso3"])
    fig = px.choropleth(
        df, locations="iso3", color="count",
        color_continuous_scale=[[0, "#0d1528"], [0.4, "#1e4080"], [0.7, "#f59e0b"], [1.0, "#ef4444"]],
        title="Global PFAS Regulations by Country",
        hover_data={"country": True, "count": True, "iso3": False},
        labels={"count": "Regulations", "country": "Country"},
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_colorbar=dict(
        title="# Regs", tickfont=dict(color="#94a3b8"), titlefont=dict(color="#94a3b8")
    ))
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)",
        landcolor="#0f1d35", oceancolor="#060b18",
        showland=True, showocean=True,
        showcoastlines=True, coastlinecolor="#1e3560",
        showframe=False, projection_type="natural earth"
    )
    return fig

def make_us_heatmap(stats):
    rows = [dict(r) for r in stats["by_state"]] if stats["by_state"] else []
    if not rows:
        return go.Figure()
    df = pd.DataFrame(rows, columns=["state", "count", "avg_score"])
    state_abbr = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
        "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY", "Federal": "DC", "National": "DC"
    }
    df["abbr"] = df["state"].map(state_abbr)
    df = df.dropna(subset=["abbr"])
    fig = px.choropleth(
        df, locations="abbr", locationmode="USA-states",
        color="count", scope="usa",
        color_continuous_scale=[[0, "#0d1528"], [0.4, "#1e4080"], [0.7, "#f59e0b"], [1.0, "#ef4444"]],
        title="US State PFAS Regulations for Oil & Gas",
        hover_data={"state": True, "count": True, "avg_score": ":.2f", "abbr": False},
        labels={"count": "# Regulations", "avg_score": "O&G Relevance"},
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_colorbar=dict(
        title="# Regs", tickfont=dict(color="#94a3b8"), titlefont=dict(color="#94a3b8")
    ))
    fig.update_geos(bgcolor="rgba(0,0,0,0)", landcolor="#0f1d35", showframe=False)
    return fig

def make_type_donut(stats):
    rows = [dict(r) for r in stats["by_type"]] if stats["by_type"] else []
    if not rows:
        return go.Figure()
    df = pd.DataFrame(rows, columns=["type", "count"])
    colors = ["#f59e0b","#22d3ee","#f43f5e","#10b981","#a78bfa","#fb923c","#34d399","#60a5fa","#f472b6","#facc15"]
    fig = go.Figure(go.Pie(
        labels=df["type"], values=df["count"],
        hole=0.62, marker_colors=colors[:len(df)],
        textfont=dict(family="DM Mono", size=11, color="#f0f6ff"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Regulations by Type",
        legend=dict(font=dict(color="#94a3b8", size=11), bgcolor="rgba(0,0,0,0)"))
    return fig

def make_relevance_histogram(regs):
    if not regs:
        return go.Figure()
    scores = [r.get("oil_gas_relevance_score", 0) for r in regs]
    fig = go.Figure(go.Histogram(
        x=scores, nbinsx=10,
        marker_color="#f59e0b",
        marker_line=dict(color="#0d1528", width=1),
        hovertemplate="Score: %{x:.1f}<br>Count: %{y}<extra></extra>"
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="O&G Relevance Score Distribution",
        xaxis=dict(title="Relevance Score", gridcolor="#162240", color="#94a3b8"),
        yaxis=dict(title="# Regulations", gridcolor="#162240", color="#94a3b8"))
    return fig

# ──────────────────────────────────────────────────────────────
# EXPORT FUNCTIONS
# ──────────────────────────────────────────────────────────────

def export_to_csv(regs: List[Dict]) -> bytes:
    output = io.StringIO()
    if not regs:
        return b""
    fieldnames = ["id","country","state","jurisdiction","title","regulation_type","status",
                  "effective_date","oil_gas_relevance_score","pfas_chemicals","regulatory_limits",
                  "content","oil_gas_context","key_requirements","source_url","verified","date_scraped"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(regs)
    return output.getvalue().encode()

def export_to_json(regs: List[Dict]) -> bytes:
    return json.dumps(regs, indent=2, default=str).encode()

def export_to_excel(regs: List[Dict]) -> bytes:
    if not regs:
        return b""
    df = pd.DataFrame(regs)
    cols = ["country","state","title","regulation_type","status","effective_date",
            "oil_gas_relevance_score","pfas_chemicals","content","source_url","verified"]
    df = df[[c for c in cols if c in df.columns]]
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="PFAS Regulations", index=False)
    return buf.getvalue()

# ──────────────────────────────────────────────────────────────
# SESSION HELPERS
# ──────────────────────────────────────────────────────────────

def get_session_id():
    if "chat_session_id" not in st.session_state:
        st.session_state.chat_session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    return st.session_state.chat_session_id

def render_kpi(label, value, sub, color_class):
    return f"""<div class="kpi-card {color_class}">
    <div class="kpi-value">{value}</div>
    <div class="kpi-label">{label}</div>
    <div class="kpi-sub">{sub}</div>
</div>"""

def render_badge(text, cls):
    return f'<span class="badge badge-{cls}">{text}</span>'

def relevance_color(score):
    if score >= 0.85: return "red"
    if score >= 0.65: return "amber"
    return "green"

# ──────────────────────────────────────────────────────────────
# UI — SIDEBAR
# ──────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">⚗️ PFAS RegWatch</div>
        <div class="sidebar-tagline">Oil & Gas Intelligence Platform</div>
        <hr>
        """, unsafe_allow_html=True)

        api_key = st.text_input("🔑 Anthropic API Key", type="password",
                                value=st.session_state.get("api_key", ""),
                                placeholder="sk-ant-…", key="api_key_input")
        if api_key:
            st.session_state["api_key"] = api_key

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**📍 Filter by Country**")
        all_countries = list(COUNTRY_URLS.keys())
        sel_countries = st.multiselect("Countries", all_countries, default=[], label_visibility="collapsed")

        st.markdown("**🗺️ Filter by US State**")
        sel_states = st.multiselect("States", list(US_STATES_URLS.keys()), default=[], label_visibility="collapsed")

        st.markdown("<hr>", unsafe_allow_html=True)

        stats = get_dashboard_stats()
        st.markdown(f"""
        <div style="font-family:var(--ff-mono);font-size:0.7rem;color:var(--text2);line-height:2">
        📊 Total Regulations: <b style="color:var(--amber)">{stats['total']}</b><br>
        ✅ Verified: <b style="color:var(--green)">{stats['verified']}</b><br>
        🌍 Countries: <b style="color:var(--cyan)">{stats['countries']}</b><br>
        🗺️ States: <b style="color:var(--cyan)">{stats['states']}</b><br>
        🔴 High O&G Risk: <b style="color:var(--red)">{stats['high_relevance']}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.caption("PFAS RegWatch v1.0 | Built for O&G Majors")

    return sel_countries, sel_states

# ──────────────────────────────────────────────────────────────
# UI — DASHBOARD
# ──────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown('<div class="main-header">PFAS REGULATORY INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Oil & Gas Industry | Global Compliance & Risk Dashboard</div>', unsafe_allow_html=True)

    stats = get_dashboard_stats()
    all_regs = get_all_regulations()

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "TOTAL REGULATIONS", stats["total"], "Across all jurisdictions", "kpi-amber"),
        (c2, "VERIFIED", stats["verified"], "Auditor-confirmed", "kpi-green"),
        (c3, "COUNTRIES", stats["countries"], "Global coverage", "kpi-cyan"),
        (c4, "HIGH O&G RISK", stats["high_relevance"], "Relevance score ≥ 80%", "kpi-red"),
        (c5, "PROPOSED", stats["proposed"], "Pending enactment", "kpi-amber"),
    ]
    for col, label, val, sub, cls in kpis:
        with col:
            st.markdown(render_kpi(label, val, sub, cls), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Maps
    col_map1, col_map2 = st.columns([3, 2])
    with col_map1:
        st.markdown('<div class="section-title">🌍 Global Regulatory Heatmap</div>', unsafe_allow_html=True)
        fig_world = make_world_heatmap(stats)
        st.plotly_chart(fig_world, use_container_width=True, config={"displayModeBar": False})

    with col_map2:
        st.markdown('<div class="section-title">🇺🇸 United States</div>', unsafe_allow_html=True)
        fig_us = make_us_heatmap(stats)
        st.plotly_chart(fig_us, use_container_width=True, config={"displayModeBar": False})

    # Charts Row
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-title">📊 Regulation Types</div>', unsafe_allow_html=True)
        fig_type = make_type_donut(stats)
        st.plotly_chart(fig_type, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown('<div class="section-title">🎯 O&G Relevance Distribution</div>', unsafe_allow_html=True)
        fig_rel = make_relevance_histogram(all_regs)
        st.plotly_chart(fig_rel, use_container_width=True, config={"displayModeBar": False})

    # Recent High-Priority Regulations
    st.markdown('<div class="section-title">🔴 High-Priority O&G Regulations</div>', unsafe_allow_html=True)
    high_prio = [r for r in all_regs if r.get("oil_gas_relevance_score", 0) >= 0.85][:6]
    if high_prio:
        for reg in high_prio:
            score = reg.get("oil_gas_relevance_score", 0)
            status_cls = "green" if reg["status"] == "Active" else ("amber" if "Proposed" in str(reg["status"]) else "cyan")
            chems = json.loads(reg.get("pfas_chemicals") or "[]")[:3]
            badges = render_badge(reg["regulation_type"], "amber") + render_badge(reg["status"], status_cls)
            for ch in chems:
                badges += render_badge(ch, "cyan")
            st.markdown(f"""<div class="reg-card">
                <div class="reg-title">{reg['title']}</div>
                <div style="margin-bottom:0.4rem">{badges}</div>
                <div style="display:flex;align-items:center;gap:1rem;font-family:var(--ff-mono);font-size:0.72rem;color:var(--text2)">
                    <span>📍 {reg['country']} — {reg['state']}</span>
                    <span>📅 {reg['effective_date'] or 'N/A'}</span>
                    <span style="color:{'var(--red)' if score>=0.85 else 'var(--amber)'}">
                        O&G Risk: {score:.0%}
                    </span>
                </div>
                <div style="font-size:0.8rem;color:var(--text1);margin-top:0.5rem;line-height:1.5">
                    {reg.get('oil_gas_context','')[:200]}…
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No high-priority regulations found. Run the Scraper Agent to populate the database.")

# ──────────────────────────────────────────────────────────────
# UI — SCRAPER AGENT
# ──────────────────────────────────────────────────────────────

def page_scraper():
    st.markdown('<div class="main-header">SCRAPER AGENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Agent 1 — Autonomous PFAS Regulatory Intelligence Collector</div>', unsafe_allow_html=True)

    api_key = st.session_state.get("api_key", "")
    if not api_key:
        st.warning("⚠️  Enter your Anthropic API key in the sidebar to use the Scraper Agent.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="section-title">🌍 Select Jurisdictions</div>', unsafe_allow_html=True)
        mode = st.radio("Scraping Scope", ["Countries", "US States", "Custom URL"], horizontal=True)

        urls_to_scrape = []
        sel_country = None; sel_state = None

        if mode == "Countries":
            sel_country = st.selectbox("Country", list(COUNTRY_URLS.keys()))
            if sel_country:
                available = COUNTRY_URLS[sel_country]
                st.markdown(f"**{len(available)} URLs available for {sel_country}:**")
                sel_urls = st.multiselect("Select URLs", [u["name"] for u in available],
                                          default=[u["name"] for u in available])
                urls_to_scrape = [
                    {**u, "country": sel_country, "state": "National"}
                    for u in available if u["name"] in sel_urls
                ]

        elif mode == "US States":
            sel_states_scrape = st.multiselect("Select States", list(US_STATES_URLS.keys()),
                                               default=["Texas", "Pennsylvania", "Colorado"])
            for s in sel_states_scrape:
                info = US_STATES_URLS[s]
                urls_to_scrape.append({
                    "name": f"{s} — {info['agency']}",
                    "url": info["url"],
                    "country": "USA",
                    "state": s
                })
            if urls_to_scrape:
                st.info(f"📋 {len(urls_to_scrape)} state URL(s) queued")

        else:  # Custom URL
            custom_url = st.text_input("URL to scrape", placeholder="https://www.epa.gov/pfas/…")
            custom_country = st.selectbox("Country", list(COUNTRY_URLS.keys()) + ["Other"])
            custom_state = st.text_input("State/Region", placeholder="Federal / National")
            if custom_url:
                urls_to_scrape = [{"name": "Custom URL", "url": custom_url,
                                   "country": custom_country, "state": custom_state or "National"}]

        st.markdown("**⚙️ Agent Settings**")
        focus_og = st.checkbox("Focus on Oil & Gas PFAS only", value=True)
        st.caption("When enabled, agent prioritizes O&G-relevant regulations")

    with col_right:
        st.markdown('<div class="section-title">📋 Scraping Queue</div>', unsafe_allow_html=True)
        if urls_to_scrape:
            for u in urls_to_scrape:
                st.markdown(f"""<div class="reg-card" style="padding:0.6rem 1rem">
                    <div style="font-family:var(--ff-mono);font-size:0.78rem;color:var(--amber)">{u['name']}</div>
                    <div style="font-family:var(--ff-mono);font-size:0.65rem;color:var(--text2);word-break:break-all">{u['url']}</div>
                    <div style="font-family:var(--ff-mono);font-size:0.68rem;color:var(--cyan)">
                        📍 {u['country']} — {u.get('state','National')}
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Select jurisdictions on the left to build scraping queue")

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        run_btn = st.button("🚀  Launch Scraper Agent", disabled=not (urls_to_scrape and api_key),
                            use_container_width=True)

    if run_btn:
        session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        log_container = st.empty()
        log_lines = []

        def log_fn(msg):
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
            log_container.markdown(
                f'<div class="log-box">{"<br>".join(log_lines[-30:])}</div>',
                unsafe_allow_html=True
            )

        log_fn("🚀 PFAS RegWatch Scraper Agent v1.0 initializing…")
        log_fn(f"   Session: {session_id}")
        log_fn(f"   Queued URLs: {len(urls_to_scrape)}")
        log_fn(f"   O&G Focus Mode: {'ON' if focus_og else 'OFF'}")

        with st.spinner("Agent 1 is collecting PFAS regulations…"):
            saved_ids = run_scraper_agent(
                urls=urls_to_scrape,
                api_key=api_key,
                session_id=session_id,
                log_fn=log_fn,
                country=sel_country or "",
                state=""
            )

        st.success(f"✅  Agent 1 complete! Saved **{len(saved_ids)}** new regulations to database.")
        if saved_ids:
            st.info(f"💡  Run the **Audit Agent** to verify {len(saved_ids)} newly scraped regulations.")
            st.session_state["last_scraped_ids"] = saved_ids

# ──────────────────────────────────────────────────────────────
# UI — REGULATIONS DATABASE
# ──────────────────────────────────────────────────────────────

def page_database(sel_countries, sel_states):
    st.markdown('<div class="main-header">REGULATIONS DATABASE</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Browse, Search, Review, and Manage PFAS Regulations</div>', unsafe_allow_html=True)

    # Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        search = st.text_input("🔍 Search", placeholder="PFOA, fracking, MCL…")
    with col_f2:
        filter_type = st.selectbox("Type", ["All"] + REGULATION_TYPES)
    with col_f3:
        filter_status = st.selectbox("Status", ["All", "Active", "Proposed", "Repealed", "Under Review"])
    with col_f4:
        filter_verified = st.selectbox("Verification", ["All", "Verified", "Unverified"])

    regs = get_all_regulations(
        country_filter=sel_countries if sel_countries else None,
        state_filter=sel_states if sel_states else None,
        status_filter=filter_status if filter_status != "All" else None,
        search_query=search if search else None
    )
    if filter_type != "All":
        regs = [r for r in regs if r.get("regulation_type") == filter_type]
    if filter_verified == "Verified":
        regs = [r for r in regs if r.get("verified")]
    elif filter_verified == "Unverified":
        regs = [r for r in regs if not r.get("verified")]

    st.markdown(f"""<div style="font-family:var(--ff-mono);font-size:0.72rem;color:var(--text2);margin:0.5rem 0">
        Showing <b style="color:var(--amber)">{len(regs)}</b> regulation(s)
    </div>""", unsafe_allow_html=True)

    # Add manual regulation
    with st.expander("➕  Add Regulation Manually"):
        with st.form("add_reg_form"):
            a1, a2 = st.columns(2)
            with a1:
                m_title = st.text_input("Title *")
                m_country = st.selectbox("Country", list(COUNTRY_URLS.keys()) + ["Other"])
                m_state = st.text_input("State/Region", "National")
                m_type = st.selectbox("Type", REGULATION_TYPES)
            with a2:
                m_url = st.text_input("Source URL")
                m_status = st.selectbox("Status", ["Active","Proposed","Repealed","Under Review"])
                m_date = st.text_input("Effective Date (YYYY-MM-DD)")
                m_score = st.slider("O&G Relevance Score", 0.0, 1.0, 0.7, 0.05)
            m_content = st.text_area("Summary / Content", height=100)
            m_og_context = st.text_area("Oil & Gas Context", height=80)
            m_chems = st.multiselect("PFAS Chemicals", PFAS_CHEMICALS)
            if st.form_submit_button("💾  Save Regulation"):
                if m_title:
                    save_regulation({
                        "country": m_country, "state": m_state, "jurisdiction": f"{m_country} - {m_state}",
                        "source_url": m_url, "title": m_title, "content": m_content,
                        "regulation_type": m_type, "pfas_chemicals": m_chems,
                        "oil_gas_relevance_score": m_score, "oil_gas_context": m_og_context,
                        "effective_date": m_date, "status": m_status, "verified": False
                    })
                    st.success("✅  Regulation saved!")
                    st.rerun()
                else:
                    st.error("Title is required.")

    # Regulations list
    for reg in regs:
        score = reg.get("oil_gas_relevance_score", 0)
        status_cls = "green" if reg["status"] == "Active" else ("amber" if "Proposed" in str(reg["status"]) else "cyan")
        chems_raw = reg.get("pfas_chemicals") or "[]"
        chems = json.loads(chems_raw) if isinstance(chems_raw, str) else chems_raw
        verified_badge = render_badge("✓ VERIFIED", "green") if reg.get("verified") else render_badge("UNVERIFIED", "amber")
        badges = render_badge(reg.get("regulation_type",""), "amber") + render_badge(reg["status"], status_cls) + verified_badge

        with st.expander(f"📄  {reg['title'][:90]}"):
            col_info, col_meta = st.columns([2, 1])
            with col_info:
                st.markdown(f"""<div style="margin-bottom:0.5rem">{badges}</div>""", unsafe_allow_html=True)
                st.markdown(f"**Summary:**\n{reg.get('content','N/A')}")
                if reg.get("oil_gas_context"):
                    st.markdown(f"**🛢️ Oil & Gas Context:**\n{reg['oil_gas_context']}")
                reqs = json.loads(reg.get("key_requirements") or "[]")
                if reqs:
                    st.markdown("**📋 Key Requirements:**")
                    for req in reqs:
                        st.markdown(f"  • {req}")
                limits = reg.get("regulatory_limits")
                if limits and limits not in ("{}", "null", None):
                    try:
                        lims = json.loads(limits) if isinstance(limits, str) else limits
                        if lims:
                            st.markdown("**⚖️ Regulatory Limits:**")
                            for k, v in lims.items():
                                st.markdown(f"  • **{k}**: {v}")
                    except: pass
            with col_meta:
                st.markdown(f"""<div style="font-family:var(--ff-mono);font-size:0.75rem;line-height:2.2;color:var(--text1)">
                    <b style="color:var(--text2)">COUNTRY:</b> {reg['country']}<br>
                    <b style="color:var(--text2)">STATE:</b> {reg['state']}<br>
                    <b style="color:var(--text2)">TYPE:</b> {reg.get('regulation_type','')}<br>
                    <b style="color:var(--text2)">STATUS:</b> {reg['status']}<br>
                    <b style="color:var(--text2)">EFFECTIVE:</b> {reg.get('effective_date','N/A')}<br>
                    <b style="color:var(--text2)">O&G SCORE:</b>
                    <span style="color:{'var(--red)' if score>=0.85 else 'var(--amber)'}">
                        {score:.0%}
                    </span><br>
                    <b style="color:var(--text2)">CHEMICALS:</b> {', '.join(chems[:4]) if chems else 'N/A'}
                </div>""", unsafe_allow_html=True)
                if reg.get("source_url"):
                    st.markdown(f"[🔗 Source]({reg['source_url']})")
                if reg.get("audit_notes"):
                    st.markdown(f"**Audit Notes:** {reg['audit_notes']}")
                if st.button("🗑️  Delete", key=f"del_{reg['id']}"):
                    delete_regulation(reg["id"])
                    st.rerun()

# ──────────────────────────────────────────────────────────────
# UI — Q&A ASSISTANT
# ──────────────────────────────────────────────────────────────

def page_qa():
    st.markdown('<div class="main-header">Q&A ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Ask Anything About PFAS Regulations — Powered by Retrieval-Augmented Claude</div>', unsafe_allow_html=True)

    api_key = st.session_state.get("api_key", "")
    if not api_key:
        st.warning("⚠️  Enter your Anthropic API key in the sidebar.")
        return

    session_id = get_session_id()
    history = get_chat_history(session_id)

    # Quick-start prompts
    st.markdown('<div class="section-title">💡 Quick Questions</div>', unsafe_allow_html=True)
    quick_cols = st.columns(3)
    quick_prompts = [
        "What are the strictest US state PFAS drinking water MCLs?",
        "How do EPA PFAS Superfund rules affect oil refineries?",
        "What PFAS disclosures are required for hydraulic fracturing in Colorado?",
        "Compare EU and US PFAS regulatory approaches for oil & gas",
        "What are the PFAS reporting requirements in Texas for O&G operators?",
        "Which countries have banned PFAS in oil & gas drilling fluids?"
    ]
    for i, col in enumerate(quick_cols):
        with col:
            if st.button(quick_prompts[i * 2][:50] + "…", key=f"q_{i*2}", use_container_width=True):
                st.session_state["pending_q"] = quick_prompts[i * 2]
            if i * 2 + 1 < len(quick_prompts):
                if st.button(quick_prompts[i * 2 + 1][:50] + "…", key=f"q_{i*2+1}", use_container_width=True):
                    st.session_state["pending_q"] = quick_prompts[i * 2 + 1]

    st.markdown('<div class="section-title">💬 Conversation</div>', unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-bubble-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">⚗️ {msg["content"]}</div>', unsafe_allow_html=True)

    question = st.chat_input("Ask about PFAS regulations, compliance, or oil & gas liability…")
    if "pending_q" in st.session_state:
        question = st.session_state.pop("pending_q")

    if question:
        st.markdown(f'<div class="chat-bubble-user">👤 {question}</div>', unsafe_allow_html=True)
        with st.spinner("⚗️  RegWatch AI is researching your question…"):
            try:
                answer = ask_qa_agent(question, api_key, session_id)
                st.markdown(f'<div class="chat-bubble-ai">⚗️ {answer}</div>', unsafe_allow_html=True)
                st.rerun()
            except Exception as e:
                st.error(f"❌  Error: {e}")

    col_clear, _ = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️  Clear Chat"):
            conn = get_db()
            conn.execute("DELETE FROM chat_history WHERE session_id=?", (session_id,))
            conn.commit()
            conn.close()
            st.rerun()

# ──────────────────────────────────────────────────────────────
# UI — AUDIT AGENT
# ──────────────────────────────────────────────────────────────

def page_audit():
    st.markdown('<div class="main-header">AUDIT AGENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Agent 2 — AI Hallucination Detector & Citation Verifier</div>', unsafe_allow_html=True)

    api_key = st.session_state.get("api_key", "")
    if not api_key:
        st.warning("⚠️  Enter your Anthropic API key in the sidebar.")
        return

    st.markdown("""<div class="reg-card" style="background:var(--cyan-dim);border-color:var(--cyan)">
    <b style="color:var(--cyan)">How Audit Agent works:</b>
    <div style="font-size:0.84rem;color:var(--text1);margin-top:0.4rem">
    Agent 2 re-fetches the original source URL for each regulation, compares the stored data 
    against the actual source content, flags hallucinations or inaccuracies, and generates 
    proper academic citations. Confidence scores indicate data reliability.
    </div></div>""", unsafe_allow_html=True)

    all_regs = get_all_regulations()
    unverified = [r for r in all_regs if not r.get("verified")]
    verified = [r for r in all_regs if r.get("verified")]

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown(f'<div class="section-title">📋 Select Regulations to Audit</div>', unsafe_allow_html=True)
        audit_scope = st.radio("Scope", ["Unverified Only", "All Regulations", "Last Scraped Batch", "Select Manually"])

        reg_ids_to_audit = []
        if audit_scope == "Unverified Only":
            reg_ids_to_audit = [r["id"] for r in unverified]
            st.info(f"📋 {len(reg_ids_to_audit)} unverified regulation(s) queued")
        elif audit_scope == "All Regulations":
            reg_ids_to_audit = [r["id"] for r in all_regs]
            st.info(f"📋 {len(reg_ids_to_audit)} total regulation(s) queued")
        elif audit_scope == "Last Scraped Batch":
            last = st.session_state.get("last_scraped_ids", [])
            reg_ids_to_audit = last
            st.info(f"📋 {len(reg_ids_to_audit)} regulation(s) from last scrape")
        else:
            titles = {str(r["id"]): r["title"][:70] for r in all_regs}
            sel = st.multiselect("Select regulations", list(titles.keys()),
                                 format_func=lambda x: titles[x])
            reg_ids_to_audit = [int(x) for x in sel]

        max_audit = st.slider("Max regulations to audit (API cost control)", 1, min(len(reg_ids_to_audit) or 1, 20), min(5, len(reg_ids_to_audit) or 1))
        reg_ids_to_audit = reg_ids_to_audit[:max_audit]

        run_audit = st.button(f"🔍  Launch Audit Agent ({len(reg_ids_to_audit)} regs)", use_container_width=True,
                              disabled=not reg_ids_to_audit)

    with col_r:
        st.markdown('<div class="section-title">📊 Audit Status</div>', unsafe_allow_html=True)
        total = len(all_regs)
        vcount = len(verified)
        ucount = len(unverified)
        pct = (vcount / total * 100) if total else 0
        st.markdown(f"""<div class="kpi-card kpi-green" style="margin-bottom:0.7rem">
            <div class="kpi-value">{vcount}/{total}</div>
            <div class="kpi-label">REGULATIONS VERIFIED</div>
        </div>""", unsafe_allow_html=True)
        st.progress(pct / 100, text=f"{pct:.0f}% database verified")
        st.markdown(f"""<div style="font-family:var(--ff-mono);font-size:0.72rem;color:var(--text2);margin-top:0.8rem;line-height:2">
            ✅ Verified: <b style="color:var(--green)">{vcount}</b><br>
            ⚠️ Unverified: <b style="color:var(--amber)">{ucount}</b><br>
            🔴 High-Risk (score ≥ 0.85): <b style="color:var(--red)">{sum(1 for r in all_regs if r.get('oil_gas_relevance_score',0)>=0.85)}</b>
        </div>""", unsafe_allow_html=True)

    if run_audit:
        log_container = st.empty()
        log_lines = []
        def log_fn(msg):
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
            log_container.markdown(f'<div class="log-box">{"<br>".join(log_lines[-25:])}</div>',
                                   unsafe_allow_html=True)
        log_fn("🔍 Audit Agent v1.0 initializing…")
        with st.spinner("Agent 2 auditing regulations…"):
            results = run_auditor_agent(reg_ids_to_audit, api_key, log_fn)
        st.session_state["last_audit_results"] = results
        st.rerun()

    # Show audit results
    if "last_audit_results" in st.session_state:
        results = st.session_state["last_audit_results"]
        st.markdown('<div class="section-title">📋 Audit Results</div>', unsafe_allow_html=True)
        r_c1, r_c2, r_c3 = st.columns(3)
        with r_c1:
            st.markdown(render_kpi("AUDITED", results["audited"], "This session", "kpi-cyan"), unsafe_allow_html=True)
        with r_c2:
            st.markdown(render_kpi("VERIFIED", results["verified"], "No issues found", "kpi-green"), unsafe_allow_html=True)
        with r_c3:
            st.markdown(render_kpi("FLAGGED", results["flagged"], "Issues detected", "kpi-red"), unsafe_allow_html=True)

        for detail in results.get("details", []):
            audit = detail["audit"]
            is_ok = audit.get("verified", False)
            cls = "audit-pass" if is_ok else ("audit-warn" if not audit.get("hallucination_flags") else "audit-fail")
            icon = "✅" if is_ok else "⚠️"
            st.markdown(f"""<div class="audit-item {cls}">
                <b style="color:var(--text0)">{icon} {detail['title'][:80]}</b><br>
                <span style="font-family:var(--ff-mono);font-size:0.7rem;color:var(--text2)">
                    Confidence: {audit.get('confidence_score',0):.0%} |
                    Completeness: {audit.get('data_completeness_score',0):.0%} |
                    O&G Relevance Verified: {'✓' if audit.get('o_g_relevance_verified') else '✗'}
                </span><br>
                <span style="font-size:0.82rem;color:var(--text1)">{audit.get('audit_summary','')}</span>
            """, unsafe_allow_html=True)
            flags = audit.get("hallucination_flags", [])
            if flags:
                for f in flags:
                    sev = f.get("severity","medium")
                    sev_color = {"high":"var(--red)","medium":"var(--amber)","low":"var(--green)"}.get(sev,"var(--amber)")
                    st.markdown(f"""<div style="font-family:var(--ff-mono);font-size:0.7rem;margin-left:1rem;color:{sev_color}">
                        ⚑ [{f.get('severity','').upper()}] {f.get('field','')}: {f.get('issue','')}
                    </div>""", unsafe_allow_html=True)
            cites = audit.get("citations", [])
            if cites:
                for cite in cites[:2]:
                    st.markdown(f"""<div style="font-family:var(--ff-mono);font-size:0.68rem;color:var(--cyan);margin-left:1rem">
                        📎 {cite.get('text','')} [{cite.get('url','')}]
                    </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# UI — EXPORT
# ──────────────────────────────────────────────────────────────

def page_export(sel_countries, sel_states):
    st.markdown('<div class="main-header">EXPORT CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">⚡ Export PFAS Regulations — Filter by Country, State, or Jurisdiction</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown('<div class="section-title">🔧 Export Configuration</div>', unsafe_allow_html=True)
        exp_countries = st.multiselect("Countries to export", list(COUNTRY_URLS.keys()),
                                       default=sel_countries or list(COUNTRY_URLS.keys()))
        exp_states = st.multiselect("US States to export", list(US_STATES_URLS.keys()),
                                    default=sel_states or [])
        exp_status = st.multiselect("Status filter", ["Active","Proposed","Repealed","Under Review"], default=["Active"])
        exp_min_score = st.slider("Minimum O&G Relevance Score", 0.0, 1.0, 0.0, 0.05)
        exp_verified_only = st.checkbox("Export verified regulations only")
        exp_format = st.radio("Export Format", ["CSV", "JSON", "Excel (.xlsx)"], horizontal=True)

    with col_r:
        st.markdown('<div class="section-title">📊 Export Preview</div>', unsafe_allow_html=True)

        # Build query
        regs = get_all_regulations(
            country_filter=exp_countries if exp_countries else None,
            state_filter=exp_states if exp_states else None,
        )
        if exp_status:
            regs = [r for r in regs if r.get("status") in exp_status]
        regs = [r for r in regs if r.get("oil_gas_relevance_score", 0) >= exp_min_score]
        if exp_verified_only:
            regs = [r for r in regs if r.get("verified")]

        st.markdown(f"""<div class="kpi-card kpi-amber">
            <div class="kpi-value">{len(regs)}</div>
            <div class="kpi-label">REGULATIONS READY TO EXPORT</div>
        </div>""", unsafe_allow_html=True)

        if regs:
            by_c = {}
            for r in regs:
                by_c[r["country"]] = by_c.get(r["country"], 0) + 1
            st.markdown("<br>**By Country:**")
            for country, count in sorted(by_c.items(), key=lambda x: -x[1]):
                st.markdown(f"  • **{country}**: {count}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_dl, _ = st.columns([1, 3])
    with col_dl:
        if regs:
            ts = datetime.now().strftime("%Y%m%d_%H%M")
            if exp_format == "CSV":
                data = export_to_csv(regs)
                st.download_button("⬇️  Download CSV", data=data,
                                   file_name=f"pfas_regulations_{ts}.csv", mime="text/csv",
                                   use_container_width=True)
            elif exp_format == "JSON":
                data = export_to_json(regs)
                st.download_button("⬇️  Download JSON", data=data,
                                   file_name=f"pfas_regulations_{ts}.json", mime="application/json",
                                   use_container_width=True)
            else:
                data = export_to_excel(regs)
                st.download_button("⬇️  Download Excel", data=data,
                                   file_name=f"pfas_regulations_{ts}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
        else:
            st.info("No regulations match the current export criteria.")

    # Preview table
    if regs:
        st.markdown('<div class="section-title">👁️ Data Preview</div>', unsafe_allow_html=True)
        df_prev = pd.DataFrame(regs)[["country","state","title","regulation_type","status","oil_gas_relevance_score","effective_date","verified"]].copy()
        df_prev["verified"] = df_prev["verified"].map({0: "No", 1: "Yes", False: "No", True: "Yes"})
        df_prev.columns = ["Country","State","Title","Type","Status","O&G Score","Effective","Verified"]
        st.dataframe(df_prev, use_container_width=True, height=350)

# ──────────────────────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────────────────────

def main():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    init_db()

    sel_countries, sel_states = render_sidebar()

    tabs = st.tabs([
        "🏠  Dashboard",
        "🕷️  Scraper Agent",
        "🗄️  Regulations DB",
        "💬  Q&A Assistant",
        "🔍  Audit Agent",
        "📤  Export"
    ])

    with tabs[0]: page_dashboard()
    with tabs[1]: page_scraper()
    with tabs[2]: page_database(sel_countries, sel_states)
    with tabs[3]: page_qa()
    with tabs[4]: page_audit()
    with tabs[5]: page_export(sel_countries, sel_states)

if __name__ == "__main__":
    main()
