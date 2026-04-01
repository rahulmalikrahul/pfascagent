import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import asyncio
import os
import re
import io
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ──────────────────────────────────────────────────────────────
# SYSTEM FIX: Manual Playwright Installation for Streamlit Cloud
# ──────────────────────────────────────────────────────────────
def ensure_browser_installed():
    """Bypasses apt-get errors by installing chromium via playwright directly."""
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        try:
            subprocess.run(["playwright", "install", "chromium"], check=True)
            subprocess.run(["playwright", "install-deps", "chromium"], check=True)
        except Exception as e:
            st.error(f"Browser Setup Error: {e}")

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG & THEME
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PFAS RegWatch | O&G Intelligence",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

THEME_CSS = """
<style>
    .stApp { background-color: #05090f; color: #f0f6ff; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; }
    .section-title { color: #ffaa00; font-weight: bold; font-size: 1.2rem; margin-bottom: 1rem; }
    .stButton>button { background-color: #0d1528; border: 1px solid #00d4ff; color: white; }
</style>
"""

# ──────────────────────────────────────────────────────────────
# DATABASE ENGINE
# ──────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("pfas_og_intel.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT, state TEXT, title TEXT, 
            summary TEXT, regulation_type TEXT, 
            status TEXT, og_relevance_score INTEGER,
            source_url TEXT, effective_date TEXT,
            verified INTEGER DEFAULT 0, audit_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

db_conn = init_db()

# ──────────────────────────────────────────────────────────────
# AGENT LOGIC (GEMINI + CRAWL4AI)
# ──────────────────────────────────────────────────────────────
def get_gemini_model(model_type="flash"):
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    # Using Flash for scraping (fast) and Pro for Auditing (high reasoning)
    model_name = 'gemini-1.5-flash' if model_type == "flash" else 'gemini-1.5-pro'
    return genai.GenerativeModel(model_name)

async def run_scraper_task(urls):
    """Agent 1: High-speed web scraping"""
    browser_cfg = BrowserConfig(headless=True)
    run_cfg = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    results = []
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        for url in urls:
            res = await crawler.arun(url=url, config=run_cfg)
            if res.success:
                results.append(res.markdown)
    return results

def agent_extract_intel(raw_markdown):
    """Agent 1: Extract O&G specific PFAS data"""
    model = get_gemini_model("flash")
    if not model: return []
    
    prompt = f"""
    Analyze this text for PFAS regulations specifically impacting the Oil & Gas industry (Refineries, Fracking, AFFF).
    Return a JSON list of objects:
    [{"country": "...", "state": "...", "title": "...", "summary": "...", "type": "Law/Rule/Guidance", "og_score": 0-100, "status": "Active/Draft"}]
    
    Text: {raw_markdown[:8000]}
    """
    try:
        response = model.generate_content(prompt)
        # Clean JSON from markdown blocks
        clean_json = re.search(r'\[.*\]', response.text, re.DOTALL).group()
        return json.loads(clean_json)
    except:
        return []

def agent_audit_hallucination(reg_item):
    """Agent 2: Hallucination check and source verification"""
    model = get_gemini_model("pro")
    if not model: return "API Key Missing"
    
    prompt = f"Critically audit this extracted PFAS data for hallucinations. Cross-reference with known O&G industry standards for AFFF and produced water. Highlight errors or confirm accuracy: {reg_item}"
    return model.generate_content(prompt).text

# ──────────────────────────────────────────────────────────────
# UI PAGES
# ──────────────────────────────────────────────────────────────
def page_dashboard():
    st.title("🛢️ PFAS O&G Impact Dashboard")
    df = pd.read_sql("SELECT * FROM regulations", db_conn)
    
    if df.empty:
        st.info("No data available. Use the Scraper Agent to begin.")
        return

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Regulations", len(df))
    m2.metric("Avg O&G Risk Score", int(df['og_relevance_score'].mean()))
    m3.metric("Verified Data", f"{(df['verified'].sum()/len(df)*100):.1f}%")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-title">National Risk Heatmap</div>', unsafe_allow_html=True)
        fig = px.choropleth(df, locations="state", locationmode="USA-states", 
                            color="og_relevance_score", scope="usa",
                            color_continuous_scale="OrRd")
        fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">Risk by Status</div>', unsafe_allow_html=True)
        st.bar_chart(df['status'].value_counts())

def page_scraper():
    st.title("🕷️ Agent 1: Regulatory Intelligence Gatherer")
    urls_input = st.text_area("Enter target URLs (one per line)", placeholder="https://www.epa.gov/pfas...")
    
    if st.button("Start Agentic Scrape"):
        ensure_browser_installed()
        urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
        
        with st.status("Gathering Intelligence...") as status:
            st.write("Crawling government sites...")
            raw_data = asyncio.run(run_scraper_task(urls))
            
            st.write("Gemini Extracting O&G Relevance...")
            for page in raw_data:
                intel = agent_extract_intel(page)
                for item in intel:
                    db_conn.execute('''
                        INSERT INTO regulations (country, state, title, summary, regulation_type, status, og_relevance_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (item['country'], item['state'], item['title'], item['summary'], item['type'], item['status'], item['og_score']))
            db_conn.commit()
            status.update(label="Scrape Complete!", state="complete")
        st.success("Regulations added to database.")

def page_database():
    st.title("🗄️ Regulatory Database")
    df = pd.read_sql("SELECT * FROM regulations", db_conn)
    
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    
    if st.button("Apply Manual Changes"):
        edited_df.to_sql("regulations", db_conn, if_exists="replace", index=False)
        st.success("Database synchronized.")

def page_audit():
    st.title("🔍 Agent 2: Verification & Audit")
    df = pd.read_sql("SELECT * FROM regulations WHERE verified = 0", db_conn)
    
    if df.empty:
        st.success("All data points have been verified.")
        return

    target_id = st.selectbox("Select Record to Audit", df['id'])
    record = df[df['id'] == target_id].iloc[0].to_json()
    
    if st.button("Run Auditor Agent"):
        with st.spinner("Analyzing for hallucinations..."):
            report = agent_audit_hallucination(record)
            st.markdown(f"### Audit Report\n{report}")
            
            if st.button("Confirm & Verify"):
                db_conn.execute("UPDATE regulations SET verified=1, audit_notes=? WHERE id=?", (report, target_id))
                db_conn.commit()
                st.rerun()

# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    
    st.sidebar.title("PFAS O&G Portal")
    page = st.sidebar.radio("Navigate", ["Dashboard", "Scraper", "Database", "Audit"])
    
    if page == "Dashboard": page_dashboard()
    elif page == "Scraper": page_scraper()
    elif page == "Database": page_database()
    elif page == "Audit": page_audit()

if __name__ == "__main__":
    main()