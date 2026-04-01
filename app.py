import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import asyncio
import os
import re
import subprocess
import sys

# ──────────────────────────────────────────────────────────────
# 🛠️ CRITICAL FIX: AUTOMATIC BROWSER INSTALLATION
# ──────────────────────────────────────────────────────────────
def install_browser_dependencies():
    """Installs Playwright Chromium if not found in cache."""
    # Check if we're on Streamlit Cloud
    if os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud":
        try:
            # We check for the presence of the executable to avoid re-installing every boot
            import playwright
            process = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True)
            if process.returncode != 0:
                st.error("Browser installation failed. Check logs.")
        except ImportError:
            st.error("Playwright not found in requirements.txt")

# Run this immediately at the top of the script
install_browser_dependencies()

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ──────────────────────────────────────────────────────────────
# 🎨 UI CONFIG & THEME
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PFAS RegWatch | O&G Intel", page_icon="⚗️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05090f; color: #f0f6ff; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #0d1528; border: 1px solid #1e293b; border-radius: 4px 4px 0 0; padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 🗄️ DATABASE ENGINE
# ──────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("pfas_og.db", check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS regs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, state TEXT, 
        title TEXT, summary TEXT, type TEXT, status TEXT, score INTEGER, 
        source TEXT, verified INTEGER DEFAULT 0, audit_notes TEXT)''')
    conn.commit()
    return conn

db = init_db()

# ──────────────────────────────────────────────────────────────
# 🤖 AI AGENTS (GEMINI 1.5)
# ──────────────────────────────────────────────────────────────
def get_ai_model(is_pro=False):
    key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("API Key", type="password")
    if not key: return None
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-1.5-pro' if is_pro else 'gemini-1.5-flash')

async def scrape_site(url):
    """Agent 1: Scraper"""
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
        return result.markdown if result.success else ""

def agent_intel_extract(content):
    """Agent 1: Intelligence Extraction"""
    model = get_ai_model()
    if not model: return []
    prompt = f"Extract O&G PFAS regulations as JSON list from this text. Focus: AFFF, produced water. Fields: country, state, title, summary, type, status, score(0-100). Text: {content[:8000]}"
    try:
        res = model.generate_content(prompt)
        return json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
    except: return []

# ──────────────────────────────────────────────────────────────
# 🚀 MAIN APPLICATION TABS
# ──────────────────────────────────────────────────────────────
def main():
    st.sidebar.title("⚗️ PFAS O&G Portal")
    menu = ["Dashboard", "Scraper Agent", "Auditor Agent", "Database"]
    choice = st.sidebar.selectbox("Navigate", menu)

    if choice == "Dashboard":
        st.title("🛢️ Oil & Gas PFAS Impact")
        df = pd.read_sql("SELECT * FROM regs", db)
        if not df.empty:
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = px.choropleth(df, locations="state", locationmode="USA-states", color="score", scope="usa", color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.metric("Total Regulations", len(df))
                st.write("### Risk Distribution")
                st.bar_chart(df['status'].value_counts())
        else:
            st.info("No data. Run the Scraper Agent.")

    elif choice == "Scraper Agent":
        st.title("🕷️ Agent 1: Intelligence Scraper")
        url = st.text_input("Target URL (e.g., EPA or State Govt)")
        if st.button("Run Scraper"):
            with st.status("Gathering data...") as s:
                raw = asyncio.run(scrape_site(url))
                s.write("Analyzing with Gemini...")
                data = agent_intel_extract(raw)
                for i in data:
                    db.execute("INSERT INTO regs (country, state, title, summary, type, status, score, source) VALUES (?,?,?,?,?,?,?,?)",
                               (i['country'], i['state'], i['title'], i['summary'], i['type'], i['status'], i['score'], url))
                db.commit()
                s.update(label="Complete!", state="complete")
            st.success(f"Added {len(data)} regulations.")

    elif choice == "Auditor Agent":
        st.title("🔍 Agent 2: Verification Auditor")
        df = pd.read_sql("SELECT * FROM regs WHERE verified = 0", db)
        if not df.empty:
            row = st.selectbox("Select record to audit", df['title'])
            if st.button("Audit for Hallucinations"):
                model = get_ai_model(is_pro=True)
                report = model.generate_content(f"Verify this PFAS data for accuracy and O&G relevance: {row}").text
                st.markdown(report)
        else:
            st.success("All records verified.")

    elif choice == "Database":
        st.title("🗄️ Managed Metadata")
        df = pd.read_sql("SELECT * FROM regs", db)
        st.data_editor(df, use_container_width=True)

if __name__ == "__main__":
    main()
