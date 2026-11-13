import os
import json
import sqlite3
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime

import db
import ai_helper

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ResumeScanner AI | HR Recruiter Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Seed Demo Data
db.init_db()
db.seed_demo_data_if_empty()

# --- CUSTOM CSS FOR MODERN DARK ATS SUITE & RESPONSIVE ENGINE ---
st.markdown("""
<style>
    /* =====================================================================
       1. GLOBAL RESET, TYPOGRAPHY & FLUID VIEWPORT SIZING
       ===================================================================== */
    :root {
        --bg-main: #0b0f19;
        --bg-card: #131b2e;
        --bg-card-hover: #18233c;
        --border-color: rgba(255, 255, 255, 0.08);
        --border-color-hover: rgba(99, 102, 241, 0.45);
        --primary: #6366f1;
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        --accent-sky: #0ea5e9;
        --accent-purple: #a855f7;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
    }

    /* Modern Dark Theme Background with Ambient Radial Glows */
    .stApp {
        background-color: var(--bg-main) !important;
        background-image: 
            radial-gradient(circle at 10% 12%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 90% 18%, rgba(14, 165, 233, 0.07) 0%, transparent 40%),
            radial-gradient(circle at 50% 85%, rgba(168, 85, 247, 0.05) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Responsive Main Block Container */
    .main .block-container {
        max-width: 1440px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    @media (max-width: 1024px) {
        .main .block-container {
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
            padding-top: 1.2rem !important;
        }
    }

    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
    }

    /* Headings */
    h1, h2, h3, h4 {
        letter-spacing: -0.025em;
        font-weight: 800;
        color: #ffffff !important;
    }

    /* =====================================================================
       2. RESPONSIVE GRID ENGINE FOR STREAMLIT COLUMNS
       ===================================================================== */
    [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
        gap: 1rem !important;
    }

    /* --- KPI Metric Cards Row (4 Columns Responsive Breakpoints) --- */
    [data-testid="stHorizontalBlock"]:has(.metric-card) {
        align-items: stretch !important;
    }
    @media (max-width: 1120px) and (min-width: 641px) {
        [data-testid="stHorizontalBlock"]:has(.metric-card) {
            flex-wrap: wrap !important;
            row-gap: 1rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.metric-card) > div[data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
            max-width: calc(50% - 0.5rem) !important;
        }
    }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"]:has(.metric-card) {
            flex-wrap: wrap !important;
            row-gap: 0.85rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.metric-card) > div[data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* --- Dashboard Charts Row & Lower Section (2 Columns Responsive) --- */
    @media (max-width: 960px) {
        [data-testid="stHorizontalBlock"]:has(.chart-card-marker),
        [data-testid="stHorizontalBlock"]:has(.dashboard-lower-marker) {
            flex-wrap: wrap !important;
            row-gap: 1.25rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.chart-card-marker) > div[data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.dashboard-lower-marker) > div[data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* --- Filter Bar (Candidate Board) --- */
    @media (max-width: 860px) {
        [data-testid="stHorizontalBlock"]:has(.filter-bar-marker) {
            flex-direction: column !important;
            row-gap: 0.75rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.filter-bar-marker) > div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* --- Job Candidate Evaluation Cards (3 Columns: info, score, status) --- */
    @media (max-width: 920px) {
        [data-testid="stHorizontalBlock"]:has(.job-candidate-card-marker) {
            flex-direction: column !important;
            row-gap: 1.25rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.job-candidate-card-marker) > div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* --- General Form Grids (2 Columns) --- */
    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"]:has(.form-row-marker) {
            flex-direction: column !important;
            row-gap: 0.75rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.form-row-marker) > div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* --- Chat Suggested Prompts (4 Buttons) --- */
    @media (max-width: 1024px) and (min-width: 641px) {
        [data-testid="stHorizontalBlock"]:has(.chat-prompt-marker) {
            flex-wrap: wrap !important;
            row-gap: 0.75rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.chat-prompt-marker) > div[data-testid="column"] {
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
            max-width: calc(50% - 0.5rem) !important;
        }
    }
    @media (max-width: 640px) {
        [data-testid="stHorizontalBlock"]:has(.chat-prompt-marker) {
            flex-wrap: wrap !important;
            row-gap: 0.6rem !important;
        }
        [data-testid="stHorizontalBlock"]:has(.chat-prompt-marker) > div[data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* =====================================================================
       3. MODERN SAAS KPI METRIC CARDS
       ===================================================================== */
    .metric-card {
        background: linear-gradient(155deg, #131c31 0%, #0d1425 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.32);
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .metric-card.accent-indigo::before { background: linear-gradient(90deg, #6366f1, #818cf8); }
    .metric-card.accent-sky::before { background: linear-gradient(90deg, #0ea5e9, #38bdf8); }
    .metric-card.accent-purple::before { background: linear-gradient(90deg, #a855f7, #c084fc); }
    .metric-card.accent-emerald::before { background: linear-gradient(90deg, #10b981, #34d399); }

    .metric-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #94a3b8;
    }
    .metric-icon-badge {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .metric-value {
        font-size: clamp(1.8rem, 2.3vw, 2.4rem);
        font-weight: 800;
        color: #ffffff;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* =====================================================================
       4. KANBAN BOARD (FLUID HORIZONTAL SCROLL & RESPONSIVENESS)
       ===================================================================== */
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 1.25rem !important;
        gap: 1.1rem !important;
        scroll-snap-type: x proximity;
        -webkit-overflow-scrolling: touch;
    }
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header)::-webkit-scrollbar {
        height: 8px;
    }
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header)::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 4px;
    }
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header)::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header)::-webkit-scrollbar-thumb:hover {
        background: #6366f1;
    }
    [data-testid="stHorizontalBlock"]:has(.kanban-stage-header) > div[data-testid="column"] {
        flex: 0 0 290px !important;
        min-width: 290px !important;
        max-width: 320px !important;
        scroll-snap-align: start;
    }

    /* Stage Header */
    .kanban-stage-header {
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
        font-size: 0.88rem;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .kanban-count-pill {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.76rem;
        font-weight: 800;
    }

    /* =====================================================================
       5. REFINED STATUS BADGES & SCORE PILLS
       ===================================================================== */
    .badge-applied { background-color: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
    .badge-screening { background-color: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
    .badge-shortlisted { background-color: rgba(59, 130, 246, 0.12); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
    .badge-interview { background-color: rgba(168, 85, 247, 0.12); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
    .badge-hired { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }
    .badge-rejected { background-color: rgba(244, 63, 94, 0.12); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.35); padding: 3px 9px; border-radius: 12px; font-size: 0.74rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }

    /* Glowing Score Pills */
    .score-high {
        color: #34d399;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.35);
        font-weight: 750;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .score-mid {
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.14);
        border: 1px solid rgba(245, 158, 11, 0.35);
        font-weight: 750;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .score-low {
        color: #fb7185;
        background: rgba(244, 63, 94, 0.14);
        border: 1px solid rgba(244, 63, 94, 0.35);
        font-weight: 750;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }

    /* Skills Chips */
    .skill-tag {
        display: inline-block;
        background: #1a2235;
        color: #cbd5e1;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 2px 7px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 500;
    }
    .skill-tag-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.14);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 9px;
        margin: 2px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .skill-tag-miss {
        display: inline-block;
        background: rgba(244, 63, 94, 0.12);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 3px 9px;
        margin: 2px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* =====================================================================
       6. SIDEBAR STYLING ENHANCEMENTS
       ===================================================================== */
    div[data-testid="stSidebar"] {
        background-color: #0d121f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }
    div[data-testid="stSidebarContent"] {
        padding-top: 1.5rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
    }

    /* Sidebar Navigation Options styling */
    div[data-testid="stSidebar"] div[data-testid="stRadio"] {
        width: 100% !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 0.35rem !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"] {
        padding: 0.45rem 0.65rem !important;
        border-radius: 8px !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stRadio"] [data-testid="stRadioOption"]:hover {
        background: rgba(99, 102, 241, 0.08) !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
    }

    /* Mini stat cards in sidebar */
    .sidebar-stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.6rem 0.75rem;
        text-align: center;
    }
    .sidebar-stat-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94a3b8;
    }
    .sidebar-stat-val {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 2px;
    }

    /* =====================================================================
       7. LOGIN PAGE RESPONSIVE CENTERED CARD
       ===================================================================== */
    .block-container:has(.login-page-marker) {
        max-width: 480px !important;
        margin: 2.5rem auto !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
    @media (max-width: 520px) {
        .block-container:has(.login-page-marker) {
            margin: 1.2rem auto !important;
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
        }
    }

    /* Form Container & Vertical Block enhancements */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        background: rgba(19, 27, 46, 0.65) !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }

    /* Streamlit Primary Buttons */
    div[data-testid="stBaseButton-primary"] button,
    button[kind="primary"] {
        background: var(--primary-gradient) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stBaseButton-primary"] button:hover,
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* Secondary Buttons */
    div[data-testid="stBaseButton-secondary"] button,
    button[kind="secondary"] {
        background: #182238 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stBaseButton-secondary"] button:hover,
    button[kind="secondary"]:hover {
        border-color: var(--primary) !important;
        color: #ffffff !important;
    }

    /* Streamlit Tabs styling */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.6rem 1.2rem !important;
        color: #94a3b8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #6366f1 !important;
    }

    /* Leaderboard Card styling */
    .leaderboard-card {
        background: #131b2e;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.9rem 1.15rem;
        margin-bottom: 0.65rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .leaderboard-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .avatar-ring {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        min-width: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to style Altair charts for dark mode
def style_altair_dark(chart):
    return chart.configure_view(
        strokeWidth=0
    ).configure_axis(
        labelColor='#94a3b8',
        titleColor='#cbd5e1',
        gridColor='#1e293b',
        domainColor='#334155',
        labelFontSize=11,
        titleFontSize=12,
        labelFont="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
        titleFont="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    ).configure_legend(
        labelColor='#cbd5e1',
        titleColor='#f8fafc',
        labelFont="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
        titleFont="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    )

NAV_OPTIONS = [
    "📊 Dashboard",
    "💼 Jobs & JD Management",
    "📋 Candidate Board",
    "💬 AI Recruiter Chat"
]

# --- SESSION RESTORE & STATE INITIALIZATION ---
auth_token = st.query_params.get("auth")
if auth_token and not st.session_state.get("authenticated", False):
    session_data = db.get_session(auth_token)
    if session_data:
        st.session_state["authenticated"] = True
        st.session_state["recruiter_name"] = session_data["name"]
        st.session_state["recruiter_role"] = session_data["role"]
        st.session_state["session_token"] = auth_token
    else:
        st.query_params.clear()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "recruiter_name" not in st.session_state:
    st.session_state["recruiter_name"] = "Sarah Jenkins"

if "recruiter_role" not in st.session_state:
    st.session_state["recruiter_role"] = "Lead Technical Recruiter"

if "session_token" not in st.session_state:
    st.session_state["session_token"] = auth_token or ""

# Keep active tab in sync with URL query param without double-clicks
url_tab = st.query_params.get("tab")
if "active_tab" not in st.session_state:
    if url_tab in NAV_OPTIONS:
        st.session_state["active_tab"] = url_tab
    else:
        st.session_state["active_tab"] = NAV_OPTIONS[0]
elif url_tab and url_tab in NAV_OPTIONS and url_tab != st.session_state["active_tab"]:
    st.session_state["active_tab"] = url_tab

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hello! I am your AI HR Recruiter Assistant. I can analyze screened candidates, compare applicant scores against Job Descriptions, or draft interview invitations. How can I help you today?"}
    ]

if "created_jd_text" not in st.session_state:
    st.session_state["created_jd_text"] = ""

# --- RECRUITER LOGIN PAGE ---
def render_login_page():
    # Injects the login marker so .block-container is automatically centered & constrained to 480px on desktop & 100% on mobile
    st.markdown('<div class="login-page-marker"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.75rem;">
        <div style="display: inline-flex; background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 16px; border-radius: 20px; font-size: 2.6rem; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4); margin-bottom: 1.1rem;">
            💼
        </div>
        <div style="display: block; margin-bottom: 0.6rem;">
            <span style="display: inline-block; background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; padding: 3px 11px; border-radius: 20px;">
                Enterprise Recruitment Intelligence
            </span>
        </div>
        <h1 style="margin: 0; font-size: 2.15rem; font-weight: 800; color: #ffffff; letter-spacing: -0.025em;">ResumeScanner AI</h1>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.4rem; line-height: 1.45;">
            Candidate scoring, JD matching, and talent pipeline suite.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h3 style='margin:0 0 4px 0; color: #ffffff; font-weight: 700; font-size: 1.2rem;'>HR Recruiter Sign In</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 1.1rem;'>Enter your credentials to access your recruitment pipeline.</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Recruiter Work Email", value="recruiter@company.com", placeholder="e.g. sarah.jenkins@company.com")
            password = st.text_input("Password", type="password", value="recruiter123", placeholder="Enter your password")
            remember = st.checkbox("Remember this session", value=True)
            
            submitted = st.form_submit_button("Sign In to Recruiter Portal", use_container_width=True, type="primary")
            if submitted:
                if email.strip() and password.strip():
                    rec_name = email.split("@")[0].replace(".", " ").title() if "@" in email else "Recruiter"
                    rec_role = "Technical Recruiter"
                    token = db.create_session(email.strip(), rec_name, rec_role)
                    st.query_params["auth"] = token
                    st.session_state["authenticated"] = True
                    st.session_state["recruiter_name"] = rec_name
                    st.session_state["recruiter_role"] = rec_role
                    st.session_state["session_token"] = token
                    st.success("Authentication successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Please enter a valid recruiter email and password.")

        st.divider()
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.08); border: 1px dashed rgba(99, 102, 241, 0.3); border-radius: 10px; padding: 0.75rem; text-align: center; margin-bottom: 0.85rem;">
            <div style="font-size: 0.74rem; font-weight: 700; color: #818cf8; text-transform: uppercase; letter-spacing: 0.06em;">Demo Mode Active</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">One-click instant login pre-seeded with candidates & JDs</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ One-Click Instant Demo Login", use_container_width=True, type="secondary"):
            token = db.create_session("recruiter@company.com", "Sarah Jenkins", "Lead Technical Recruiter")
            st.query_params["auth"] = token
            st.session_state["authenticated"] = True
            st.session_state["recruiter_name"] = "Sarah Jenkins"
            st.session_state["recruiter_role"] = "Lead Technical Recruiter"
            st.session_state["session_token"] = token
            st.rerun()

# --- SIDEBAR COMPONENT ---
def render_sidebar():
    with st.sidebar:
        # Branding
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.25rem;">
            <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 8px; border-radius: 10px; font-size: 1.35rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);">
                💼
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.2rem; font-weight: 800; color: #ffffff;">ResumeScanner</h3>
                <span style="font-size: 0.7rem; color: #818cf8; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">HR Recruiter Suite</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recruiter Profile Card with Status Indicator
        st.markdown(f"""
        <div style="background: #141c2f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.85rem; margin-bottom: 1.3rem; box-shadow: 0 4px 12px rgba(0,0,0,0.25);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #3b82f6, #6366f1); color: white; border-radius: 50%; width: 38px; height: 38px; min-width: 38px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);">
                    {st.session_state['recruiter_name'][0] if st.session_state['recruiter_name'] else 'R'}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state['recruiter_name']}</div>
                    <div style="font-size: 0.74rem; color: #94a3b8; font-weight: 500;">{st.session_state['recruiter_role']}</div>
                    <div style="font-size: 0.68rem; color: #34d399; font-weight: 600; margin-top: 2px;">● Active Recruiter</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; margin-bottom: 0.4rem;'>Navigation</p>", unsafe_allow_html=True)
        
        def on_nav_change():
            st.query_params["tab"] = st.session_state["active_tab"]
        
        nav_choice = st.radio(
            "Go to",
            options=NAV_OPTIONS,
            key="active_tab",
            on_change=on_nav_change,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        
        # Responsive 2x2 mini-stat grid in Sidebar (never breaks or squishes)
        stats = db.get_dashboard_stats()
        st.markdown("<p style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #94a3b8; margin-bottom: 0.6rem;'>Live Pipeline Summary</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 1.2rem;">
            <div class="sidebar-stat-card">
                <div class="sidebar-stat-label">Open Jobs</div>
                <div class="sidebar-stat-val" style="color: #818cf8;">{stats['open_jobs']}</div>
            </div>
            <div class="sidebar-stat-card">
                <div class="sidebar-stat-label">Candidates</div>
                <div class="sidebar-stat-val" style="color: #38bdf8;">{stats['total_candidates']}</div>
            </div>
            <div class="sidebar-stat-card">
                <div class="sidebar-stat-label">Shortlisted</div>
                <div class="sidebar-stat-val" style="color: #c084fc;">{stats['shortlisted']}</div>
            </div>
            <div class="sidebar-stat-card">
                <div class="sidebar-stat-label">Avg Match</div>
                <div class="sidebar-stat-val" style="color: #34d399;">{stats['avg_score']}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System Tools
        with st.expander("⚙️ System Tools"):
            if st.button("Reload Sample Demo Data", use_container_width=True):
                db.seed_demo_data_if_empty()
                st.success("Sample data loaded!")
                st.rerun()
            if st.button("Clear Candidate Database", use_container_width=True):
                conn = db.get_connection()
                conn.execute("DELETE FROM candidates")
                conn.commit()
                conn.close()
                st.warning("Candidate database reset.")
                st.rerun()

        # Logout button
        if st.button("🚪 Sign Out", use_container_width=True):
            session_tok = st.session_state.get("session_token")
            if session_tok:
                db.delete_session(session_tok)
            st.session_state["authenticated"] = False
            st.session_state["session_token"] = ""
            st.session_state["active_tab"] = NAV_OPTIONS[0]
            st.query_params.clear()
            st.rerun()
            
    return nav_choice

# --- 1. DASHBOARD VIEW ---
def render_dashboard():
    st.markdown("""
    <div style="margin-bottom: 1.6rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <div>
                <h1 style="margin: 0; font-size: clamp(1.6rem, 2.5vw, 2.15rem); font-weight: 800; color: #ffffff;">Recruitment Analytics Dashboard</h1>
                <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Real-time hiring metrics, candidate pipeline health, and scoring intelligence.</p>
            </div>
            <div style="background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.7rem;">●</span> Live ATS Feed
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    stats = db.get_dashboard_stats()
    
    # KPI Metric Cards (Responsive 4 -> 2x2 -> 1x1 via CSS)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="metric-card accent-indigo">
            <div class="metric-header">
                <div class="metric-title">Active Open Jobs</div>
                <div class="metric-icon-badge">💼</div>
            </div>
            <div class="metric-value">{stats['open_jobs']}</div>
            <div class="metric-sub" style="color: #818cf8;">Across {stats['total_jobs']} Total Roles</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="metric-card accent-sky">
            <div class="metric-header">
                <div class="metric-title">Candidates Screened</div>
                <div class="metric-icon-badge">👥</div>
            </div>
            <div class="metric-value">{stats['total_candidates']}</div>
            <div class="metric-sub" style="color: #38bdf8;">{stats['in_interview']} Currently in Interview</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="metric-card accent-purple">
            <div class="metric-header">
                <div class="metric-title">Shortlisted Candidates</div>
                <div class="metric-icon-badge">⭐</div>
            </div>
            <div class="metric-value">{stats['shortlisted']}</div>
            <div class="metric-sub" style="color: #c084fc;">{stats['shortlist_rate']}% Shortlist Conversion</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        top_name = stats['top_candidate']['name'] if stats['top_candidate'] else "None"
        top_val = f"{stats['top_candidate']['score']}%" if stats['top_candidate'] else "N/A"
        st.markdown(f"""
        <div class="metric-card accent-emerald">
            <div class="metric-header">
                <div class="metric-title">Avg Candidate Match</div>
                <div class="metric-icon-badge">🎯</div>
            </div>
            <div class="metric-value">{stats['avg_score']}%</div>
            <div class="metric-sub" style="color: #34d399;">Top Match: {top_name} ({top_val})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row (Responsive 2-col to 1-col stack via CSS)
    st.markdown('<div class="chart-card-marker"></div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns([1.1, 0.9])
    
    with chart_col1:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 1.12rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;'>Candidate Pipeline Funnel</h4>", unsafe_allow_html=True)
            stages_order = ["Applied", "Screening", "Shortlisted", "Interview", "Hired", "Rejected"]
            pipeline_data = pd.DataFrame([
                {"Stage": stage, "Count": stats["status_counts"].get(stage, 0)}
                for stage in stages_order
            ])
            
            color_scale = alt.Scale(
                domain=stages_order,
                range=["#94a3b8", "#f59e0b", "#3b82f6", "#a855f7", "#10b981", "#f43f5e"]
            )
            
            chart_pipeline = alt.Chart(pipeline_data).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Stage:N", sort=stages_order, title="Pipeline Stage", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Count:Q", title="Number of Candidates"),
                color=alt.Color("Stage:N", scale=color_scale, legend=None),
                tooltip=["Stage", "Count"]
            ).properties(height=260)
            
            st.altair_chart(style_altair_dark(chart_pipeline), use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 1.12rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;'>Candidate Match Score Distribution</h4>", unsafe_allow_html=True)
            score_df = pd.DataFrame([
                {"Tier": tier, "Candidates": count}
                for tier, count in stats["score_bins"].items()
            ])
            
            score_colors = alt.Scale(
                domain=list(stats["score_bins"].keys()),
                range=["#10b981", "#3b82f6", "#f59e0b", "#f43f5e"]
            )
            
            chart_score = alt.Chart(score_df).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6).encode(
                x=alt.X("Candidates:Q", title="Candidate Count"),
                y=alt.Y("Tier:N", sort=list(stats["score_bins"].keys()), title=None),
                color=alt.Color("Tier:N", scale=score_colors, legend=None),
                tooltip=["Tier", "Candidates"]
            ).properties(height=260)
            
            st.altair_chart(style_altair_dark(chart_score), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lower Section: Top Skills & Recent Screened Candidates
    st.markdown('<div class="dashboard-lower-marker"></div>', unsafe_allow_html=True)
    sec_col1, sec_col2 = st.columns([1, 1.2])
    
    with sec_col1:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 1.12rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;'>Top In-Demand Skills in Candidate Pool</h4>", unsafe_allow_html=True)
            if stats["top_skills"]:
                skills_df = pd.DataFrame(stats["top_skills"], columns=["Skill", "Frequency"])
                chart_skills = alt.Chart(skills_df).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#6366f1").encode(
                    x=alt.X("Frequency:Q", title="Candidate Count"),
                    y=alt.Y("Skill:N", sort="-x", title=None),
                    tooltip=["Skill", "Frequency"]
                ).properties(height=280)
                st.altair_chart(style_altair_dark(chart_skills), use_container_width=True)
            else:
                st.info("No skill data available yet. Screen candidates to build skill insights.")

    with sec_col2:
        with st.container(border=True):
            st.markdown("<h4 style='font-size: 1.12rem; font-weight: 700; color: #ffffff; margin-bottom: 0.75rem;'>Top Matching Candidates (Leaderboard)</h4>", unsafe_allow_html=True)
            top_candidates = db.get_candidates()[:5]
            if top_candidates:
                for cand in top_candidates:
                    score = cand["match_score"]
                    score_class = "score-high" if score >= 80 else ("score-mid" if score >= 60 else "score-low")
                    badge_class = f"badge-{cand['status'].lower()}"
                    
                    skills_html = "".join([f"<span class='skill-tag'>{s}</span>" for s in cand["skills"][:4]])
                    
                    st.markdown(f"""
                    <div class="leaderboard-card">
                        <div style="display: flex; align-items: center; gap: 12px; overflow: hidden;">
                            <div class="avatar-ring">{cand['name'][0] if cand['name'] else 'C'}</div>
                            <div style="overflow: hidden;">
                                <div style="font-weight: 700; font-size: 0.96rem; color: #ffffff;">{cand['name']}</div>
                                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 1px;">Applied: <strong style="color: #cbd5e1;">{cand['job_title']}</strong></div>
                                <div style="margin-top: 5px; flex-wrap: wrap;">{skills_html}</div>
                            </div>
                        </div>
                        <div style="text-align: right; min-width: 85px; margin-left: 10px;">
                            <span class="{score_class}">🎯 {score}%</span>
                            <div style="margin-top: 6px;"><span class="{badge_class}">{cand['status']}</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No candidates screened yet.")

# --- 2. JOBS PAGE & JD MATCH SCORING ---
def render_jobs_page():
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="margin: 0; font-size: clamp(1.6rem, 2.5vw, 2.15rem); font-weight: 800; color: #ffffff;">Job Postings & Candidate Scoring</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Manage active Job Descriptions (JDs), author new JDs with Groq AI, and inspect candidate scoring percentages per JD.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_view, tab_create, tab_screen = st.tabs([
        "📋 Job Openings & Candidates Scoring",
        "✨ AI Job Description (JD) Generator",
        "➕ Screen New Candidate for Job"
    ])
    
    # --- TAB 1: VIEW ALL JOBS & CANDIDATE SCORING PER JD ---
    with tab_view:
        jobs = db.get_jobs()
        if not jobs:
            st.info("No jobs posted yet. Use the 'AI Job Description Generator' tab to create your first job posting.")
        else:
            job_options = {f"{j['title']} ({j['department']}) - {j['applicant_count']} Applicants": j["id"] for j in jobs}
            
            selected_job_label = st.selectbox("Select a Job to inspect candidates & JD scoring:", options=list(job_options.keys()))
            selected_job_id = job_options[selected_job_label]
            selected_job = db.get_job_by_id(selected_job_id)
            
            if selected_job:
                # Responsive Job Header Card
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #141c2f 0%, #0d1424 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 1.35rem; margin-top: 0.6rem; margin-bottom: 1.4rem; box-shadow: 0 4px 18px rgba(0,0,0,0.25);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                        <div>
                            <span style="background: #3b82f6; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em;">{selected_job['status'].upper()}</span>
                            <h2 style="margin: 0.5rem 0 0.3rem 0; font-size: 1.45rem; color: #ffffff; font-weight: 800;">{selected_job['title']}</h2>
                            <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">
                                🏢 <span style="color: #cbd5e1;">{selected_job['department']}</span> &nbsp;|&nbsp; 📍 <span style="color: #cbd5e1;">{selected_job['location']}</span> &nbsp;|&nbsp; ⏳ <span style="color: #cbd5e1;">{selected_job['experience_level']}</span>
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.5rem; font-weight: 800; color: #ffffff;">{selected_job['applicant_count']} Applicants</div>
                            <div style="font-size: 0.88rem; color: #34d399; font-weight: 700;">Avg Match: {selected_job['avg_match_score']}%</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255, 255, 255, 0.07); display: flex; align-items: center; flex-wrap: wrap; gap: 4px;">
                        <span style="font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-right: 6px;">Required Skills:</span>
                        {"".join([f"<span class='skill-tag-match'>✓ {s}</span>" for s in selected_job['required_skills']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📄 View Full Job Description (JD) Context"):
                    st.markdown(selected_job["description"] if selected_job["description"] else "No detailed description stored.")
                
                st.markdown("<h3 style='font-size: 1.25rem; font-weight: 800; color: #ffffff; margin-top: 1.2rem; margin-bottom: 0.8rem;'>Evaluated Candidates for this Job</h3>", unsafe_allow_html=True)
                
                job_candidates = db.get_candidates(job_id=selected_job_id)
                if not job_candidates:
                    st.info(f"No candidates evaluated for '{selected_job['title']}' yet. Switch to the 'Screen New Candidate' tab to upload resumes for this role.")
                else:
                    for cand in job_candidates:
                        with st.container(border=True):
                            st.markdown('<div class="job-candidate-card-marker"></div>', unsafe_allow_html=True)
                            c_col1, c_col2, c_col3 = st.columns([1.4, 1.4, 1.2])
                            
                            # Candidate Info
                            with c_col1:
                                st.markdown(f"**Candidate:** <span style='font-size: 1.1rem; font-weight: 800; color: #ffffff;'>{cand['name']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span style='color: #94a3b8; font-size: 0.82rem;'>📧 {cand['email']} | 📞 {cand['phone']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size: 0.84rem; color: #cbd5e1; margin-top: 6px; line-height: 1.45;'>{cand['summary']}</p>", unsafe_allow_html=True)
                            
                            # Scoring Percentage as per JD breakdown
                            with c_col2:
                                score = cand['match_score']
                                score_color = "#34d399" if score >= 80 else ("#fbbf24" if score >= 60 else "#f87171")
                                
                                st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span style="font-weight: 700; font-size: 0.9rem; color: #ffffff;">JD Match Percentage</span>
                                    <span style="font-size: 1.2rem; font-weight: 800; color: {score_color};">{score}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.progress(min(int(score), 100))
                                
                                req_set = set([s.lower() for s in selected_job["required_skills"]])
                                cand_skills = cand["skills"]
                                matched_skills = [s for s in cand_skills if any(req in s.lower() or s.lower() in req for req in req_set)]
                                missing_skills = [r for r in selected_job["required_skills"] if not any(r.lower() in s.lower() or s.lower() in r.lower() for s in cand_skills)]
                                
                                st.markdown("<div style='font-size: 0.8rem; margin-top: 8px;'><strong style='color: #cbd5e1;'>Matched Skills:</strong> " + 
                                            ("".join([f"<span class='skill-tag-match'>✓ {s}</span>" for s in matched_skills[:5]]) if matched_skills else "<span style='color: #94a3b8;'>None detected</span>") + 
                                            "</div>", unsafe_allow_html=True)
                                if missing_skills:
                                    st.markdown("<div style='font-size: 0.8rem; margin-top: 4px;'><strong style='color: #cbd5e1;'>Missing Skills:</strong> " + 
                                                "".join([f"<span class='skill-tag-miss'>✗ {s}</span>" for s in missing_skills[:4]]) + 
                                                "</div>", unsafe_allow_html=True)
                            
                            # Pipeline Status Actions
                            with c_col3:
                                st.markdown("<strong style='color: #ffffff; font-size: 0.88rem;'>Current Stage:</strong>", unsafe_allow_html=True)
                                current_status = cand["status"]
                                status_options = ["Applied", "Screening", "Shortlisted", "Interview", "Hired", "Rejected"]
                                new_status = st.selectbox(
                                    "Update Stage",
                                    options=status_options,
                                    index=status_options.index(current_status) if current_status in status_options else 0,
                                    key=f"status_select_job_{cand['id']}",
                                    label_visibility="collapsed"
                                )
                                if new_status != current_status:
                                    db.update_candidate_status(cand["id"], new_status)
                                    st.toast(f"Updated {cand['name']} stage to {new_status}!", icon="✅")
                                    st.rerun()

                                with st.expander("📝 Recruiter Notes"):
                                    rec_notes = st.text_area("Notes", value=cand["notes"], key=f"notes_{cand['id']}", height=70, label_visibility="collapsed")
                                    if st.button("Save Note", key=f"save_note_{cand['id']}", use_container_width=True):
                                        db.update_candidate_notes(cand["id"], rec_notes)
                                        st.success("Note saved!")

    # --- TAB 2: AI JOB DESCRIPTION GENERATOR & CREATE JOB ---
    with tab_create:
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 800; color: #ffffff;'>✨ Create New Job Description with Groq AI</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Fill in the core job criteria and use Groq LLM to automatically generate a complete, professional Job Description.</p>", unsafe_allow_html=True)
        
        st.markdown('<div class="form-row-marker"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("Job Title *", placeholder="e.g. Senior Machine Learning Engineer")
            new_dept = st.selectbox("Department", ["Engineering", "Product & Design", "Data & AI", "Infrastructure & DevOps", "Sales & Marketing", "Human Resources", "Finance"])
            new_location = st.text_input("Location / Work Model", value="San Francisco, CA (Hybrid)", placeholder="e.g. Remote (US), London, UK")
        with c2:
            new_exp = st.selectbox("Experience Level", ["Entry Level (0-2 yrs)", "Mid Level (2-4 yrs)", "Senior Level (5+ yrs)", "Lead / Staff (7+ yrs)", "Director / Executive"])
            new_skills = st.text_input("Required Skills (comma separated) *", placeholder="e.g. Python, PyTorch, LangChain, Docker, AWS")
            
        st.markdown('<div class="form-row-marker"></div>', unsafe_allow_html=True)
        gen_col1, gen_col2 = st.columns([1, 2])
        with gen_col1:
            if st.button("✨ Generate JD with Groq AI", type="secondary", use_container_width=True):
                if not new_title.strip() or not new_skills.strip():
                    st.warning("Please provide at least a Job Title and Required Skills.")
                else:
                    with st.spinner("Generating detailed Job Description using Groq AI..."):
                        try:
                            jd_content = ai_helper.generate_job_description(
                                title=new_title,
                                skills=new_skills,
                                department=new_dept,
                                experience=new_exp
                            )
                            st.session_state["created_jd_text"] = jd_content
                            st.success("Job Description generated successfully!")
                        except Exception as e:
                            st.error(f"Failed to generate JD: {e}")

        jd_editor = st.text_area(
            "Review & Edit Job Description Context",
            value=st.session_state.get("created_jd_text", ""),
            height=240,
            placeholder="Generated job description will appear here. You can also manually write or paste your own JD..."
        )
        st.session_state["created_jd_text"] = jd_editor
        
        if st.button("💾 Save & Publish Job Opening", type="primary", use_container_width=True):
            if not new_title.strip():
                st.error("Job Title is required.")
            elif not jd_editor.strip():
                st.error("Job Description cannot be empty.")
            else:
                skills_list = [s.strip() for s in new_skills.split(",") if s.strip()]
                new_id = db.create_job(
                    title=new_title,
                    department=new_dept,
                    location=new_location,
                    experience_level=new_exp,
                    required_skills=skills_list,
                    description=jd_editor,
                    status="Open"
                )
                st.success(f"Job '{new_title}' successfully created with ID #{new_id}!")
                st.session_state["created_jd_text"] = ""
                st.rerun()

    # --- TAB 3: SCREEN NEW CANDIDATE FOR JOB ---
    with tab_screen:
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 800; color: #ffffff;'>➕ Screen & Score Candidate Against a Job Description</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Upload a candidate's resume (PDF / Image) or paste resume text to evaluate their exact scoring percentage against the chosen JD.</p>", unsafe_allow_html=True)
        
        jobs = db.get_jobs()
        if not jobs:
            st.warning("Please create at least one Job Posting first.")
        else:
            job_choices = {f"{j['title']} ({j['department']})": j["id"] for j in jobs}
            target_job_name = st.selectbox("Select Target Job for Candidate Evaluation:", options=list(job_choices.keys()))
            target_job_id = job_choices[target_job_name]
            target_job = db.get_job_by_id(target_job_id)
            
            st.info(f"Evaluating candidate for: **{target_job['title']}** | Required Skills: {', '.join(target_job['required_skills'])}")
            
            st.markdown('<div class="form-row-marker"></div>', unsafe_allow_html=True)
            sc_col1, sc_col2 = st.columns(2)
            with sc_col1:
                uploaded_resume = st.file_uploader("Upload Resume (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
            with sc_col2:
                pasted_resume = st.text_area("Or Paste Candidate Resume Text", height=130, placeholder="Paste resume plain text here...")
                
            if st.button("🚀 Screen Candidate & Calculate Match Score", type="primary", use_container_width=True):
                resume_text = ""
                if uploaded_resume:
                    with st.spinner("Extracting text from resume file (with OCR fallback)..."):
                        resume_text = ai_helper.extract_text_from_file(uploaded_resume)
                elif pasted_resume.strip():
                    resume_text = pasted_resume.strip()
                else:
                    st.warning("Please upload a resume file or paste resume text.")
                    st.stop()
                    
                if resume_text.startswith("Error:"):
                    st.error(resume_text)
                else:
                    with st.spinner("Parsing resume details with Groq AI..."):
                        try:
                            candidate_info = ai_helper.parse_candidate_resume(resume_text)
                            match_details = ai_helper.compute_jd_match_score(
                                jd_text=target_job["description"],
                                required_skills=target_job["required_skills"],
                                resume_text=resume_text,
                                candidate_skills=candidate_info.get("Skills", [])
                            )
                            
                            final_score = match_details["score"]
                            cand_id = db.insert_candidate(
                                job_id=target_job_id,
                                info=candidate_info,
                                match_score=final_score
                            )
                            
                            st.success(f"Candidate '{candidate_info.get('Name')}' successfully screened and scored!")
                            
                            with st.container(border=True):
                                st.markdown(f"<h3 style='color: #ffffff; margin-top: 0;'>🎯 Screening Scorecard: <span style='color: #34d399;'>{final_score}% Match</span></h3>", unsafe_allow_html=True)
                                st.progress(min(int(final_score), 100))
                                
                                st.markdown('<div class="form-row-marker"></div>', unsafe_allow_html=True)
                                sc1, sc2 = st.columns(2)
                                with sc1:
                                    st.markdown(f"**Name:** <span style='color: #ffffff; font-weight: 700;'>{candidate_info.get('Name')}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**Email:** <span style='color: #94a3b8;'>{candidate_info.get('Email')}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**Phone:** <span style='color: #94a3b8;'>{candidate_info.get('Phone')}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**Summary:** <span style='color: #cbd5e1;'>{candidate_info.get('Summary')}</span>", unsafe_allow_html=True)
                                with sc2:
                                    st.markdown(f"**Target Role:** <span style='color: #ffffff; font-weight: 700;'>{target_job['title']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"**Skill Match Coverage:** <span style='color: #38bdf8; font-weight: 700;'>{match_details['skill_match_pct']}%</span>", unsafe_allow_html=True)
                                    st.markdown("<div style='margin-top: 6px;'><strong>Matched Skills:</strong> " + "".join([f"<span class='skill-tag-match'>✓ {s}</span>" for s in match_details['matched_skills']]) + "</div>", unsafe_allow_html=True)
                                    if match_details['missing_skills']:
                                        st.markdown("<div style='margin-top: 4px;'><strong>Missing Skills:</strong> " + "".join([f"<span class='skill-tag-miss'>✗ {s}</span>" for s in match_details['missing_skills']]) + "</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error during candidate screening: {e}")

# --- 3. INTERACTIVE CANDIDATE BOARD ---
def render_candidate_board():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="margin: 0; font-size: clamp(1.6rem, 2.5vw, 2.15rem); font-weight: 800; color: #ffffff;">Interactive Candidate Board</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Track applicants across recruitment stages, update candidate statuses in real time, and inspect qualification scores.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter Bar (Responsive on mobile)
    with st.container(border=True):
        st.markdown('<div class="filter-bar-marker"></div>', unsafe_allow_html=True)
        f_col1, f_col2, f_col3 = st.columns([1.5, 1.2, 1.3])
        
        jobs = db.get_jobs()
        job_filter_options = ["All Active Jobs"] + [f"{j['title']} (#{j['id']})" for j in jobs]
        
        with f_col1:
            selected_filter_job = st.selectbox("Filter by Job", job_filter_options)
            filter_job_id = None
            if selected_filter_job != "All Active Jobs":
                filter_job_id = int(selected_filter_job.split("(#")[-1].replace(")", ""))
                
        with f_col2:
            min_score = st.slider("Minimum Match Score %", min_value=0, max_value=100, value=0, step=5)
            
        with f_col3:
            search_query = st.text_input("Search Candidate or Skill", placeholder="e.g. Python, Elena, Docker...")
            
    # Fetch candidates based on filters
    candidates = db.get_candidates(job_id=filter_job_id, min_score=min_score, search=search_query)
    
    stages = [
        {"name": "Applied", "color": "#94a3b8", "bg": "rgba(148, 163, 184, 0.12)", "border": "rgba(148, 163, 184, 0.3)", "icon": "📥"},
        {"name": "Screening", "color": "#fbbf24", "bg": "rgba(245, 158, 11, 0.12)", "border": "rgba(245, 158, 11, 0.35)", "icon": "🔍"},
        {"name": "Shortlisted", "color": "#60a5fa", "bg": "rgba(96, 165, 250, 0.12)", "border": "rgba(96, 165, 250, 0.35)", "icon": "⭐"},
        {"name": "Interview", "color": "#c084fc", "bg": "rgba(192, 132, 252, 0.12)", "border": "rgba(192, 132, 252, 0.35)", "icon": "📅"},
        {"name": "Hired", "color": "#34d399", "bg": "rgba(52, 211, 153, 0.14)", "border": "rgba(52, 211, 153, 0.4)", "icon": "🤝"},
        {"name": "Rejected", "color": "#fb7185", "bg": "rgba(251, 113, 133, 0.12)", "border": "rgba(251, 113, 133, 0.35)", "icon": "❌"}
    ]
    
    stage_buckets = {s["name"]: [] for s in stages}
    for c in candidates:
        status = c["status"]
        if status in stage_buckets:
            stage_buckets[status].append(c)
        else:
            stage_buckets["Applied"].append(c)

    # Optional stage drill-down selector for small screens / quick mobile triage
    view_options = ["All Stages (Kanban Board)"] + [s["name"] for s in stages]
    col_view, _ = st.columns([2, 1])
    with col_view:
        active_stage_view = st.radio(
            "View Stage",
            options=view_options,
            horizontal=True,
            key="kanban_stage_view",
            label_visibility="collapsed"
        )

    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # If a specific stage is selected, show an expanded focused view
    if active_stage_view != "All Stages (Kanban Board)":
        target_stage_info = next(s for s in stages if s["name"] == active_stage_view)
        stage_name = target_stage_info["name"]
        stage_cands = stage_buckets[stage_name]
        
        st.markdown(f"""
        <div class="kanban-stage-header" style="background: {target_stage_info['bg']}; border-left: 4px solid {target_stage_info['color']};">
            <span style="color: #ffffff;">{target_stage_info['icon']} {stage_name} ({len(stage_cands)} Candidates)</span>
        </div>
        """, unsafe_allow_html=True)
        
        if not stage_cands:
            st.info(f"No candidates currently in the '{stage_name}' stage.")
        else:
            grid_cols = st.columns(min(len(stage_cands), 3) if len(stage_cands) > 1 else 1)
            for idx, cand in enumerate(stage_cands):
                col_target = grid_cols[idx % len(grid_cols)]
                with col_target:
                    score = cand["match_score"]
                    score_class = "score-high" if score >= 80 else ("score-mid" if score >= 60 else "score-low")
                    skills_chips = "".join([f"<span class='skill-tag'>{s}</span>" for s in cand["skills"][:4]])
                    
                    with st.container(border=True):
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                            <strong style="color: #ffffff; font-size: 1.02rem; font-weight: 750;">{cand['name']}</strong>
                            <span class="{score_class}">🎯 {score}%</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px;">💼 {cand['job_title']}</div>
                        <div style="margin-bottom: 10px;">{skills_chips}</div>
                        """, unsafe_allow_html=True)
                        
                        stage_options = [s["name"] for s in stages]
                        new_stage = st.selectbox(
                            "Move Stage",
                            options=stage_options,
                            index=stage_options.index(stage_name),
                            key=f"board_stage_focus_{cand['id']}",
                            label_visibility="collapsed"
                        )
                        if new_stage != stage_name:
                            db.update_candidate_status(cand["id"], new_stage)
                            st.toast(f"Moved {cand['name']} to {new_stage}!", icon="🎯")
                            st.rerun()
                            
                        with st.expander("👁️ Quick Details"):
                            st.markdown(f"<p style='font-size: 0.8rem; margin:0 0 3px 0; color: #cbd5e1;'><strong>Email:</strong> <span style='color:#94a3b8;'>{cand['email']}</span></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 0.8rem; margin:0 0 5px 0; color: #cbd5e1;'><strong>Phone:</strong> <span style='color:#94a3b8;'>{cand['phone']}</span></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 0.8rem; color: #94a3b8; line-height: 1.4; margin: 0 0 6px 0;'>{cand['summary'][:160]}...</p>", unsafe_allow_html=True)
                            if cand['notes']:
                                st.markdown(f"<p style='font-size: 0.8rem; color: #60a5fa;'><strong>Notes:</strong> {cand['notes']}</p>", unsafe_allow_html=True)
    else:
        # Full Horizontal Scrolling Kanban Board (290px min-width per column with touch scroll)
        cols = st.columns(len(stages))
        
        for idx, stage in enumerate(stages):
            stage_name = stage["name"]
            stage_cands = stage_buckets[stage_name]
            
            with cols[idx]:
                # Kanban stage header (also marks the container for horizontal scroll styling)
                st.markdown(f"""
                <div class="kanban-stage-header" style="background: {stage['bg']}; border-left: 3px solid {stage['color']};">
                    <span style="color: #ffffff;">{stage['icon']} {stage_name}</span>
                    <span class="kanban-count-pill" style="background: rgba(255,255,255,0.08); color: {stage['color']};">{len(stage_cands)}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if not stage_cands:
                    st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.82rem; font-style: italic; margin-top: 1.2rem;'>No candidates</p>", unsafe_allow_html=True)
                else:
                    for cand in stage_cands:
                        score = cand["match_score"]
                        score_class = "score-high" if score >= 80 else ("score-mid" if score >= 60 else "score-low")
                        skills_chips = "".join([f"<span class='skill-tag'>{s}</span>" for s in cand["skills"][:3]])
                        
                        with st.container(border=True):
                            st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                                <strong style="color: #ffffff; font-size: 0.98rem; font-weight: 750;">{cand['name']}</strong>
                                <span class="{score_class}">🎯 {score}%</span>
                            </div>
                            <div style="font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px;">💼 {cand['job_title']}</div>
                            <div style="margin-bottom: 10px;">{skills_chips}</div>
                            """, unsafe_allow_html=True)
                            
                            stage_options = [s["name"] for s in stages]
                            new_stage = st.selectbox(
                                "Move Stage",
                                options=stage_options,
                                index=stage_options.index(stage_name),
                                key=f"board_stage_{cand['id']}",
                                label_visibility="collapsed"
                            )
                            if new_stage != stage_name:
                                db.update_candidate_status(cand["id"], new_stage)
                                st.toast(f"Moved {cand['name']} to {new_stage}!", icon="🎯")
                                st.rerun()
                                
                            with st.expander("👁️ Quick Details"):
                                st.markdown(f"<p style='font-size: 0.8rem; margin:0 0 3px 0; color: #cbd5e1;'><strong>Email:</strong> <span style='color:#94a3b8;'>{cand['email']}</span></p>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size: 0.8rem; margin:0 0 5px 0; color: #cbd5e1;'><strong>Phone:</strong> <span style='color:#94a3b8;'>{cand['phone']}</span></p>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size: 0.78rem; color: #94a3b8; line-height: 1.4; margin: 0 0 6px 0;'>{cand['summary'][:140]}...</p>", unsafe_allow_html=True)
                                if cand['notes']:
                                    st.markdown(f"<p style='font-size: 0.78rem; color: #60a5fa;'><strong>Notes:</strong> {cand['notes']}</p>", unsafe_allow_html=True)

# --- 4. INTERACTIVE AI CHAT BOARD ---
def render_chat_board():
    st.markdown("""
    <div style="margin-bottom: 1.25rem;">
        <h1 style="margin: 0; font-size: clamp(1.6rem, 2.5vw, 2.15rem); font-weight: 800; color: #ffffff;">💬 Interactive AI Recruiter Chat Assistant</h1>
        <p style="margin: 0.35rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Ask questions about candidates, compare qualifications across job postings, draft outreach emails, or discover top talent.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prompt suggestions (Responsive 4 -> 2x2 -> 1x1 via CSS)
    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.5rem;'>Suggested Inquiries:</p>", unsafe_allow_html=True)
    st.markdown('<div class="chat-prompt-marker"></div>', unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("🏆 Top 3 Candidates", use_container_width=True):
            st.session_state["user_prompt_input"] = "Who are the top 3 highest scoring candidates overall and what makes them stand out?"
    with p_col2:
        if st.button("🐍 Python Role Match", use_container_width=True):
            st.session_state["user_prompt_input"] = "Compare the candidates who applied for the Senior Python Engineer position."
    with p_col3:
        if st.button("✉️ Draft Invite Email", use_container_width=True):
            st.session_state["user_prompt_input"] = "Draft a warm, professional interview invitation email for the top shortlisted candidate."
    with p_col4:
        if st.button("🔍 Find Cloud Talent", use_container_width=True):
            st.session_state["user_prompt_input"] = "Which candidates have proven experience with Docker, Kubernetes, or AWS?"

    st.divider()

    # Display chat history
    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Handle user input from suggestion or text input
    chat_prompt = st.chat_input("Ask anything about candidates, skills, or job descriptions...")
    
    user_input = None
    if "user_prompt_input" in st.session_state and st.session_state["user_prompt_input"]:
        user_input = st.session_state.pop("user_prompt_input")
    elif chat_prompt:
        user_input = chat_prompt

    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing candidate database & generating response..."):
                try:
                    jobs_data = db.get_jobs()
                    candidates_data = db.get_candidates()
                    reply = ai_helper.ask_hr_chat_assistant(
                        messages=st.session_state["chat_messages"],
                        jobs_data=jobs_data,
                        candidates_data=candidates_data
                    )
                    st.markdown(reply)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
                except Exception as e:
                    err_msg = f"Sorry, I encountered an error communicating with Groq: {e}"
                    st.error(err_msg)
                    st.session_state["chat_messages"].append({"role": "assistant", "content": err_msg})

# --- MAIN APP ENTRYPOINT ---
def main():
    if not st.session_state.get("authenticated", False):
        render_login_page()
    else:
        nav_choice = render_sidebar()
        
        if nav_choice == "📊 Dashboard":
            render_dashboard()
        elif nav_choice == "💼 Jobs & JD Management":
            render_jobs_page()
        elif nav_choice == "📋 Candidate Board":
            render_candidate_board()
        elif nav_choice == "💬 AI Recruiter Chat":
            render_chat_board()

if __name__ == "__main__":
    main()
