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
# 🛠️ SYSTEM BOOTSTRAP: Playwright Bypass
# ──────────────────────────────────────────────────────────────
def bootstrap_environment():
    """Manually installs Chromium to bypass Streamlit Cloud apt-get errors."""
    if os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud":
        # Check if already installed in cache to save time
        marker_file = "/home/appuser/.playwright_installed"
        if not os.path.exists(marker_file):
            with st.spinner("Initializing Environment (First run may take 1-2 mins)..."):
                try:
                    # Install chromium via playwright CLI
                    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                    # Touch marker file
                    with open(marker_file, "w") as f: f.write("done")
                except Exception as e:
                    st.error(f"Critical Boot Error: {e}")

# Run the bootstrap BEFORE importing crawl4ai
bootstrap_environment()

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# ──────────────────────────────────────────────────────────────
# 🎨 UI & THEME (O&G Industrial)
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="PFAS RegWatch | O&G Intel", page_icon="⚗️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05090f; color: #f0f6ff; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Courier New'; }
    .stTabs [data-baseweb="tab-list"] { background-color: #0d1528; border-bottom: 1px solid #1e293b; }
    .main-header { color: #ffaa00; font-weight: bold; border-left: 4px solid #ffaa00; padding-left: 15px; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 🗄️ DATABASE
# ──────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("pfas_og_intel.db", check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS regulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, country TEXT, state TEXT, 
        title TEXT, summary TEXT, type TEXT, status TEXT, score INTEGER, 
        source_url TEXT, verified INTEGER DEFAULT 0, audit_notes TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# ──────────────────────────────────────────────────────────────
# 🤖 AGENT 1: SCRAPER & EXTRACTOR
# ──────────────────────────────────────────────────────────────
def get_gemini(is_pro=False):
    api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key: return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro' if is_pro else 'gemini-1.5-flash')

async def run_scrape(url):
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url=url, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS))
        return result.markdown if result.success else None

def extract_intel(content):
    model = get_gemini()
    if not model: return []
    prompt = f"""Extract PFAS regulations from text for an Oil & Gas major (Focus: AFFF, produced water).
    Return JSON list: [{{"country": "...", "state": "...", "title": "...", "summary": "...", "type": "...", "status": "...", "score": 0-100}}]
    Text: {content[:8000]}"""
    try:
        res = model.generate_content(prompt)
        return json.loads(re.search(r'\[.*\]', res.text, re.DOTALL).group())
    except: return []

# ──────────────────────────────────────────────────────────────
# 🚀 PAGE LOGIC
# ──────────────────────────────────────────────────────────────
def main():
    st.sidebar.title("⚗️ PFAS O&G Portal")
    page = st.sidebar.radio("Navigation", ["Dashboard", "Scraper Agent", "Audit Agent", "Database"])

    if page == "Dashboard":
        st.markdown('<h1 class="main-header">PFAS O&G Impact Analysis</h1>', unsafe_allow_html=True)
        df = pd.read_sql("SELECT * FROM regulations", db_conn)
        if not df.empty:
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = px.choropleth(df, locations="state", locationmode="USA-states", color="score", scope="usa", color_continuous_scale="Reds")
                fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.metric("Total Regulations", len(df))
                st.write("### Risk by Status")
                st.bar_chart(df['status'].value_counts())
        else:
            st.info("No data in system. Run Scraper Agent.")

    elif page == "Scraper Agent":
        st.title("🕷️ Agent 1: Intelligence Scraper")
        target = st.text_input("Target URL (e.g., EPA PFAS page)")
        if st.button("Execute Intelligence Gathering"):
            with st.status("Analyzing...") as s:
                raw = asyncio.run(run_scrape(target))
                if raw:
                    data = extract_intel(raw)
                    for i in data:
                        db_conn.execute("INSERT INTO regulations (country,state,title,summary,type,status,score,source_url) VALUES (?,?,?,?,?,?,?,?)",
                                       (i['country'],i['state'],i['title'],i['summary'],i['type'],i['status'],i['score'],target))
                    db_conn.commit()
                    s.update(label=f"Captured {len(data)} items!", state="complete")
                    st.success("Database updated.")

    elif page == "Audit Agent":
        st.title("🔍 Agent 2: Verification Auditor")
        df = pd.read_sql("SELECT * FROM regulations WHERE verified = 0", db_conn)
        if not df.empty:
            choice = st.selectbox("Select record to verify", df['title'])
            if st.button("Verify with Gemini Pro"):
                model = get_gemini(is_pro=True)
                report = model.generate_content(f"Audit this PFAS regulatory summary for accuracy/hallucination: {choice}").text
                st.markdown(report)
        else: st.success("Database fully verified.")

    elif page == "Database":
        st.title("🗄️ Metadata Management")
        df = pd.read_sql("SELECT * FROM regulations", db_conn)
        st.data_editor(df, use_container_width=True)

if __name__ == "__main__":
    main()
