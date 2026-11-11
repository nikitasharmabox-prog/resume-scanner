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
    page_title="TalentMatch AI | HR Recruiter Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database and Seed Demo Data
db.init_db()
db.seed_demo_data_if_empty()

# --- CUSTOM CSS FOR MODERN DARK ATS SUITE ---
st.markdown("""
<style>
    /* Global layout & typography */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
    
    /* Modern Metric Cards (Dashboard) */
    .metric-card {
        background: linear-gradient(145deg, #151e32 0%, #0d1526 100%);
        border: 1px solid #26344d;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1.15;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #38bdf8;
        margin-top: 0.4rem;
        font-weight: 600;
    }
    
    /* Status Badges */
    .badge-applied { background-color: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid #475569; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-screening { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #b45309; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-shortlisted { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #2563eb; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-interview { background-color: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid #9333ea; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-hired { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #059669; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .badge-rejected { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #dc2626; padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    
    /* Glowing Score Pills */
    .score-high {
        color: #34d399;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.35);
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-block;
    }
    .score-mid {
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-block;
    }
    .score-low {
        color: #f87171;
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.35);
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        display: inline-block;
    }

    /* Skills Chips */
    .skill-tag {
        display: inline-block;
        background: #1e293b;
        color: #cbd5e1;
        border: 1px solid #334155;
        padding: 2px 7px;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 500;
    }
    .skill-tag-match {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 9px;
        margin: 2px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .skill-tag-miss {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 3px 9px;
        margin: 2px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Modern container border enhancement */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #26344d !important;
        border-radius: 12px !important;
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
        titleFontSize=12
    ).configure_legend(
        labelColor='#cbd5e1',
        titleColor='#f8fafc'
    )

# --- SESSION STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "recruiter_name" not in st.session_state:
    st.session_state["recruiter_name"] = "Sarah Jenkins"

if "recruiter_role" not in st.session_state:
    st.session_state["recruiter_role"] = "Lead Technical Recruiter"

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Hello! I am your AI HR Recruiter Assistant. I can analyze screened candidates, compare applicant scores against Job Descriptions, or draft interview invitations. How can I help you today?"}
    ]

if "created_jd_text" not in st.session_state:
    st.session_state["created_jd_text"] = ""

# --- RECRUITER LOGIN PAGE ---
def render_login_page():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="display: inline-flex; background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 16px; border-radius: 20px; font-size: 2.8rem; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35); margin-bottom: 1rem;">
                💼
            </div>
            <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">TalentMatch AI</h1>
            <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 0.4rem;">
                Enterprise HR Recruitment & Candidate Scoring Suite
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0; color: #ffffff; font-weight: 700;'>HR Recruiter Sign In</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Enter your credentials to access your recruitment pipeline and active jobs.</p>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Recruiter Work Email", value="recruiter@company.com", placeholder="e.g. sarah.jenkins@company.com")
                password = st.text_input("Password", type="password", value="recruiter123", placeholder="Enter your password")
                remember = st.checkbox("Remember this session", value=True)
                
                submitted = st.form_submit_button("Sign In to Recruiter Portal", use_container_width=True, type="primary")
                if submitted:
                    if email.strip() and password.strip():
                        st.session_state["authenticated"] = True
                        st.session_state["recruiter_name"] = email.split("@")[0].replace(".", " ").title() if "@" in email else "Recruiter"
                        st.success("Authentication successful! Redirecting to recruitment dashboard...")
                        st.rerun()
                    else:
                        st.error("Please enter a valid recruiter email and password.")

            st.divider()
            st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; text-align: center;'>Demo Evaluation Mode is Active</p>", unsafe_allow_html=True)
            if st.button("⚡ One-Click Instant Demo Login", use_container_width=True):
                st.session_state["authenticated"] = True
                st.session_state["recruiter_name"] = "Sarah Jenkins"
                st.session_state["recruiter_role"] = "Lead Technical Recruiter"
                st.rerun()

# --- SIDEBAR COMPONENT ---
def render_sidebar():
    with st.sidebar:
        # Branding
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.2rem;">
            <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); padding: 8px; border-radius: 10px; font-size: 1.4rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);">
                💼
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #ffffff;">TalentMatch</h3>
                <span style="font-size: 0.72rem; color: #818cf8; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">HR Recruiter Suite</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recruiter Profile Card
        st.markdown(f"""
        <div style="background: #151d30; border: 1px solid #26334d; border-radius: 12px; padding: 0.85rem; margin-bottom: 1.4rem; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #3b82f6, #6366f1); color: white; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);">
                    {st.session_state['recruiter_name'][0] if st.session_state['recruiter_name'] else 'R'}
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #f8fafc;">{st.session_state['recruiter_name']}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500;">{st.session_state['recruiter_role']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.4rem;'>Navigation</p>", unsafe_allow_html=True)
        
        nav_choice = st.radio(
            "Go to",
            options=[
                "📊 Dashboard",
                "💼 Jobs & JD Management",
                "📋 Candidate Board",
                "💬 AI Recruiter Chat"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        
        # Quick Statistics in Sidebar
        stats = db.get_dashboard_stats()
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.5rem;'>Live Pipeline Summary</p>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Open Jobs", stats["open_jobs"])
            st.metric("Shortlisted", stats["shortlisted"])
        with col_s2:
            st.metric("Candidates", stats["total_candidates"])
            st.metric("Avg Score", f"{stats['avg_score']}%")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Reset / Demo data helper
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
            st.session_state["authenticated"] = False
            st.rerun()
            
    return nav_choice

# --- 1. DASHBOARD VIEW ---
def render_dashboard():
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">Recruitment Analytics Dashboard</h1>
        <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Real-time hiring metrics, candidate pipeline health, and scoring intelligence.</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = db.get_dashboard_stats()
    
    # KPI Metric Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Open Jobs</div>
            <div class="metric-value">{stats['open_jobs']}</div>
            <div class="metric-sub">Across {stats['total_jobs']} Total Roles</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Candidates Screened</div>
            <div class="metric-value">{stats['total_candidates']}</div>
            <div class="metric-sub">{stats['in_interview']} Currently in Interview</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Shortlisted Candidates</div>
            <div class="metric-value">{stats['shortlisted']}</div>
            <div class="metric-sub">{stats['shortlist_rate']}% Shortlist Conversion</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        top_name = stats['top_candidate']['name'] if stats['top_candidate'] else "None"
        top_val = f"{stats['top_candidate']['score']}%" if stats['top_candidate'] else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Candidate Match</div>
            <div class="metric-value">{stats['avg_score']}%</div>
            <div class="metric-sub">Top Match: {top_name} ({top_val})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    chart_col1, chart_col2 = st.columns([1.1, 0.9])
    
    with chart_col1:
        st.markdown("<h4 style='font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;'>Candidate Pipeline Funnel</h4>", unsafe_allow_html=True)
        stages_order = ["Applied", "Screening", "Shortlisted", "Interview", "Hired", "Rejected"]
        pipeline_data = pd.DataFrame([
            {"Stage": stage, "Count": stats["status_counts"].get(stage, 0)}
            for stage in stages_order
        ])
        
        color_scale = alt.Scale(
            domain=stages_order,
            range=["#94a3b8", "#f59e0b", "#3b82f6", "#a855f7", "#10b981", "#ef4444"]
        )
        
        chart_pipeline = alt.Chart(pipeline_data).mark_bar(cornerRadius=6, size=32).encode(
            x=alt.X("Stage:N", sort=stages_order, title="Pipeline Stage", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Count:Q", title="Number of Candidates"),
            color=alt.Color("Stage:N", scale=color_scale, legend=None),
            tooltip=["Stage", "Count"]
        ).properties(height=260)
        
        st.altair_chart(style_altair_dark(chart_pipeline), use_container_width=True)

    with chart_col2:
        st.markdown("<h4 style='font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;'>Candidate Match Score Distribution</h4>", unsafe_allow_html=True)
        score_df = pd.DataFrame([
            {"Tier": tier, "Candidates": count}
            for tier, count in stats["score_bins"].items()
        ])
        
        score_colors = alt.Scale(
            domain=list(stats["score_bins"].keys()),
            range=["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
        )
        
        chart_score = alt.Chart(score_df).mark_bar(cornerRadius=6, size=28).encode(
            x=alt.X("Candidates:Q", title="Candidate Count"),
            y=alt.Y("Tier:N", sort=list(stats["score_bins"].keys()), title=None),
            color=alt.Color("Tier:N", scale=score_colors, legend=None),
            tooltip=["Tier", "Candidates"]
        ).properties(height=260)
        
        st.altair_chart(style_altair_dark(chart_score), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lower Section: Top Skills & Recent Screened Candidates
    sec_col1, sec_col2 = st.columns([1, 1.2])
    
    with sec_col1:
        st.markdown("<h4 style='font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;'>Top In-Demand Skills in Candidate Pool</h4>", unsafe_allow_html=True)
        if stats["top_skills"]:
            skills_df = pd.DataFrame(stats["top_skills"], columns=["Skill", "Frequency"])
            chart_skills = alt.Chart(skills_df).mark_bar(cornerRadius=4, color="#6366f1").encode(
                x=alt.X("Frequency:Q", title="Candidate Count"),
                y=alt.Y("Skill:N", sort="-x", title=None),
                tooltip=["Skill", "Frequency"]
            ).properties(height=280)
            st.altair_chart(style_altair_dark(chart_skills), use_container_width=True)
        else:
            st.info("No skill data available yet. Screen candidates to build skill insights.")

    with sec_col2:
        st.markdown("<h4 style='font-size: 1.15rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;'>Top Matching Candidates (Leaderboard)</h4>", unsafe_allow_html=True)
        top_candidates = db.get_candidates()[:5]
        if top_candidates:
            for cand in top_candidates:
                score = cand["match_score"]
                score_class = "score-high" if score >= 80 else ("score-mid" if score >= 60 else "score-low")
                badge_class = f"badge-{cand['status'].lower()}"
                
                skills_html = "".join([f"<span class='skill-tag'>{s}</span>" for s in cand["skills"][:4]])
                
                st.markdown(f"""
                <div style="background: #151e32; border: 1px solid #26344d; border-radius: 10px; padding: 0.85rem 1.1rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                    <div>
                        <div style="font-weight: 700; font-size: 0.98rem; color: #ffffff;">{cand['name']}</div>
                        <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 2px;">Applied for: <strong style="color: #cbd5e1;">{cand['job_title']}</strong></div>
                        <div style="margin-top: 6px;">{skills_html}</div>
                    </div>
                    <div style="text-align: right;">
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
        <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">Job Postings & Candidate Scoring</h1>
        <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Manage active Job Descriptions (JDs), generate new JDs with AI, and review candidate scoring percentages tailored to each JD.</p>
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
            
            # Select Job Selector
            col_sel, col_stat = st.columns([2, 1])
            with col_sel:
                selected_job_label = st.selectbox("Select a Job to inspect candidates & JD scoring:", options=list(job_options.keys()))
                selected_job_id = job_options[selected_job_label]
            
            selected_job = db.get_job_by_id(selected_job_id)
            
            if selected_job:
                # Job Header Card
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #151e32 0%, #0e1628 100%); border: 1px solid #26344d; border-radius: 14px; padding: 1.4rem; margin-top: 0.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="background: #3b82f6; color: white; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em;">{selected_job['status'].upper()}</span>
                            <h2 style="margin: 0.6rem 0 0.3rem 0; font-size: 1.55rem; color: #ffffff; font-weight: 800;">{selected_job['title']}</h2>
                            <p style="margin: 0; color: #94a3b8; font-size: 0.92rem;">
                                🏢 <span style="color: #cbd5e1;">{selected_job['department']}</span> &nbsp;|&nbsp; 📍 <span style="color: #cbd5e1;">{selected_job['location']}</span> &nbsp;|&nbsp; ⏳ <span style="color: #cbd5e1;">{selected_job['experience_level']}</span>
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff;">{selected_job['applicant_count']} Applicants</div>
                            <div style="font-size: 0.9rem; color: #34d399; font-weight: 700;">Avg Score: {selected_job['avg_match_score']}%</div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid #26344d;">
                        <span style="font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-right: 6px;">Required Skills:</span>
                        {"".join([f"<span class='skill-tag-match'>✓ {s}</span>" for s in selected_job['required_skills']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📄 View Full Job Description (JD) Context"):
                    st.markdown(selected_job["description"] if selected_job["description"] else "No detailed description stored.")
                
                st.markdown("<h3 style='font-size: 1.3rem; font-weight: 800; color: #ffffff; margin-top: 1rem;'>Evaluated Candidates for this Job</h3>", unsafe_allow_html=True)
                
                job_candidates = db.get_candidates(job_id=selected_job_id)
                if not job_candidates:
                    st.info(f"No candidates evaluated for '{selected_job['title']}' yet. Switch to the 'Screen New Candidate' tab to upload resumes for this role.")
                else:
                    for cand in job_candidates:
                        with st.container(border=True):
                            c_col1, c_col2, c_col3 = st.columns([1.5, 1.5, 1])
                            
                            # Candidate Info
                            with c_col1:
                                st.markdown(f"**Candidate:** <span style='font-size: 1.15rem; font-weight: 800; color: #ffffff;'>{cand['name']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<span style='color: #94a3b8; font-size: 0.85rem;'>📧 {cand['email']} | 📞 {cand['phone']}</span>", unsafe_allow_html=True)
                                st.markdown(f"<p style='font-size: 0.85rem; color: #cbd5e1; margin-top: 6px; line-height: 1.4;'>{cand['summary']}</p>", unsafe_allow_html=True)
                            
                            # Scoring Percentage as per JD breakdown
                            with c_col2:
                                score = cand['match_score']
                                score_label = "Strong Fit" if score >= 80 else ("Moderate Fit" if score >= 60 else "Low Match")
                                score_color = "#34d399" if score >= 80 else ("#fbbf24" if score >= 60 else "#f87171")
                                
                                st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span style="font-weight: 700; font-size: 0.95rem; color: #ffffff;">JD Match Percentage</span>
                                    <span style="font-size: 1.25rem; font-weight: 800; color: {score_color};">{score}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.progress(min(int(score), 100))
                                
                                # Compare required skills vs candidate skills
                                req_set = set([s.lower() for s in selected_job["required_skills"]])
                                cand_skills = cand["skills"]
                                matched_skills = [s for s in cand_skills if any(req in s.lower() or s.lower() in req for req in req_set)]
                                missing_skills = [r for r in selected_job["required_skills"] if not any(r.lower() in s.lower() or s.lower() in r.lower() for s in cand_skills)]
                                
                                st.markdown("<div style='font-size: 0.82rem; margin-top: 8px;'><strong style='color: #cbd5e1;'>Matched Skills:</strong> " + 
                                            ("".join([f"<span class='skill-tag-match'>✓ {s}</span>" for s in matched_skills[:5]]) if matched_skills else "<span style='color: #94a3b8;'>None detected</span>") + 
                                            "</div>", unsafe_allow_html=True)
                                if missing_skills:
                                    st.markdown("<div style='font-size: 0.82rem; margin-top: 4px;'><strong style='color: #cbd5e1;'>Missing Skills:</strong> " + 
                                                "".join([f"<span class='skill-tag-miss'>✗ {s}</span>" for s in missing_skills[:4]]) + 
                                                "</div>", unsafe_allow_html=True)
                            
                            # Pipeline Status Actions
                            with c_col3:
                                st.markdown("<strong style='color: #ffffff; font-size: 0.9rem;'>Current Status:</strong>", unsafe_allow_html=True)
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
                                    st.toast(f"Updated {cand['name']} status to {new_status}!", icon="✅")
                                    st.rerun()

                                # Notes expander
                                with st.expander("📝 Recruiter Notes"):
                                    rec_notes = st.text_area("Notes", value=cand["notes"], key=f"notes_{cand['id']}", height=70, label_visibility="collapsed")
                                    if st.button("Save Note", key=f"save_note_{cand['id']}"):
                                        db.update_candidate_notes(cand["id"], rec_notes)
                                        st.success("Note saved!")

    # --- TAB 2: AI JOB DESCRIPTION GENERATOR & CREATE JOB ---
    with tab_create:
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 800; color: #ffffff;'>✨ Create New Job Description with Groq AI</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Fill in the core job criteria and use Groq LLM to automatically author a complete, professional Job Description.</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            new_title = st.text_input("Job Title *", placeholder="e.g. Senior Machine Learning Engineer")
            new_dept = st.selectbox("Department", ["Engineering", "Product & Design", "Data & AI", "Infrastructure & DevOps", "Sales & Marketing", "Human Resources", "Finance"])
            new_location = st.text_input("Location / Work Model", value="San Francisco, CA (Hybrid)", placeholder="e.g. Remote (US), London, UK")
        with c2:
            new_exp = st.selectbox("Experience Level", ["Entry Level (0-2 yrs)", "Mid Level (2-4 yrs)", "Senior Level (5+ yrs)", "Lead / Staff (7+ yrs)", "Director / Executive"])
            new_skills = st.text_input("Required Skills (comma separated) *", placeholder="e.g. Python, PyTorch, LangChain, Docker, AWS")
            
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
            height=250,
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
        st.markdown("<h3 style='font-size: 1.3rem; font-weight: 800; color: #ffffff;'>➕ Screen & Score Candidate Against a Job Description</h3>", unsafe_allow_html=True)
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
                            # 1. Parse candidate information with LLM
                            candidate_info = ai_helper.parse_candidate_resume(resume_text)
                            
                            # 2. Compute scoring percentage against target Job's JD
                            match_details = ai_helper.compute_jd_match_score(
                                jd_text=target_job["description"],
                                required_skills=target_job["required_skills"],
                                resume_text=resume_text,
                                candidate_skills=candidate_info.get("Skills", [])
                            )
                            
                            final_score = match_details["score"]
                            
                            # 3. Store in Database
                            cand_id = db.insert_candidate(
                                job_id=target_job_id,
                                info=candidate_info,
                                match_score=final_score
                            )
                            
                            st.success(f"Candidate '{candidate_info.get('Name')}' successfully screened and scored!")
                            
                            # Display Instant Scorecard
                            with st.container(border=True):
                                st.markdown(f"<h3 style='color: #ffffff; margin-top: 0;'>🎯 Screening Scorecard: <span style='color: #34d399;'>{final_score}% Match</span></h3>", unsafe_allow_html=True)
                                st.progress(min(int(final_score), 100))
                                
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
    <div style="margin-bottom: 1.2rem;">
        <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">Interactive Candidate Board</h1>
        <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Track applicants across recruitment stages, update candidate statuses in real time, and inspect qualification scores.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter Bar
    with st.container(border=True):
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
    
    # Define Kanban Stages with dark-theme tuned translucent accents
    stages = [
        {"name": "Applied", "color": "#94a3b8", "bg": "rgba(148, 163, 184, 0.12)", "border": "#475569", "icon": "📥"},
        {"name": "Screening", "color": "#fbbf24", "bg": "rgba(245, 158, 11, 0.12)", "border": "#b45309", "icon": "🔍"},
        {"name": "Shortlisted", "color": "#60a5fa", "bg": "rgba(96, 165, 250, 0.12)", "border": "#2563eb", "icon": "⭐"},
        {"name": "Interview", "color": "#c084fc", "bg": "rgba(192, 132, 252, 0.12)", "border": "#9333ea", "icon": "📅"},
        {"name": "Hired", "color": "#34d399", "bg": "rgba(52, 211, 153, 0.12)", "border": "#059669", "icon": "🤝"},
        {"name": "Rejected", "color": "#f87171", "bg": "rgba(248, 113, 113, 0.12)", "border": "#dc2626", "icon": "❌"}
    ]
    
    # Group candidates by status
    stage_buckets = {s["name"]: [] for s in stages}
    for c in candidates:
        status = c["status"]
        if status in stage_buckets:
            stage_buckets[status].append(c)
        else:
            stage_buckets["Applied"].append(c)
            
    # Render Columns
    cols = st.columns(len(stages))
    
    for idx, stage in enumerate(stages):
        stage_name = stage["name"]
        stage_cands = stage_buckets[stage_name]
        
        with cols[idx]:
            # Stage Header
            st.markdown(f"""
            <div style="background: {stage['bg']}; border-top: 3px solid {stage['color']}; border-left: 1px solid {stage['border']}; border-right: 1px solid {stage['border']}; border-bottom: 1px solid {stage['border']}; border-radius: 10px; padding: 0.65rem 0.5rem; text-align: center; margin-bottom: 0.85rem;">
                <span style="font-weight: 700; font-size: 0.9rem; color: #ffffff;">{stage['icon']} {stage_name}</span>
                <span style="background: {stage['bg']}; color: {stage['color']}; border: 1px solid {stage['border']}; font-weight: 800; font-size: 0.8rem; padding: 2px 7px; border-radius: 10px; margin-left: 6px;">{len(stage_cands)}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Candidate cards in this stage
            if not stage_cands:
                st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem; font-style: italic; margin-top: 1rem;'>No candidates</p>", unsafe_allow_html=True)
            else:
                for cand in stage_cands:
                    score = cand["match_score"]
                    score_class = "score-high" if score >= 80 else ("score-mid" if score >= 60 else "score-low")
                    skills_chips = "".join([f"<span class='skill-tag'>{s}</span>" for s in cand["skills"][:3]])
                    
                    with st.container(border=True):
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                            <strong style="color: #ffffff; font-size: 0.98rem; font-weight: 700;">{cand['name']}</strong>
                            <span class="{score_class}">🎯 {score}%</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px;">💼 {cand['job_title']}</div>
                        <div style="margin-bottom: 10px;">{skills_chips}</div>
                        """, unsafe_allow_html=True)
                        
                        # Move Stage Dropdown
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
    <div style="margin-bottom: 1.2rem;">
        <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">💬 Interactive AI Recruiter Chat Assistant</h1>
        <p style="margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">Ask questions about candidates, compare qualifications across job postings, draft outreach emails, or discover top talent.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prompt suggestions
    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #94a3b8; margin-bottom: 0.4rem;'>Suggested Inquiries:</p>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("🏆 Top 3 Candidates Overall", use_container_width=True):
            st.session_state["user_prompt_input"] = "Who are the top 3 highest scoring candidates overall and what makes them stand out?"
    with p_col2:
        if st.button("🐍 Python Role Comparison", use_container_width=True):
            st.session_state["user_prompt_input"] = "Compare the candidates who applied for the Senior Python Engineer position."
    with p_col3:
        if st.button("✉️ Draft Interview Invite", use_container_width=True):
            st.session_state["user_prompt_input"] = "Draft a warm, professional interview invitation email for the top shortlisted candidate."
    with p_col4:
        if st.button("🔍 Find Docker & AWS Talent", use_container_width=True):
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
        # Add to chat history
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
