import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_NAME = "candidates.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department TEXT,
            location TEXT,
            experience_level TEXT,
            required_skills TEXT,
            description TEXT,
            status TEXT DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create candidates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            summary TEXT,
            match_score REAL,
            status TEXT DEFAULT 'Applied',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE SET NULL
        )
    ''')
    
    # Handle schema evolution for existing databases safely across all SQLite versions
    cursor.execute("PRAGMA table_info(candidates)")
    cols = [col[1] for col in cursor.fetchall()]
    if "job_id" not in cols:
        cursor.execute("ALTER TABLE candidates ADD COLUMN job_id INTEGER")
    if "notes" not in cols:
        cursor.execute("ALTER TABLE candidates ADD COLUMN notes TEXT")
    if "created_at" not in cols:
        # SQLite < 3.31.0 disallows non-constant defaults like CURRENT_TIMESTAMP in ALTER TABLE ADD COLUMN.
        # Add column without default, then backfill existing records with datetime('now').
        cursor.execute("ALTER TABLE candidates ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE candidates SET created_at = datetime('now') WHERE created_at IS NULL")

    # Also verify jobs table columns if table existed from an older version
    cursor.execute("PRAGMA table_info(jobs)")
    job_cols = [col[1] for col in cursor.fetchall()]
    if "created_at" not in job_cols:
        cursor.execute("ALTER TABLE jobs ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE jobs SET created_at = datetime('now') WHERE created_at IS NULL")
        
    conn.commit()
    conn.close()

def seed_demo_data_if_empty():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if jobs exist
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    job_count = cursor.fetchone()["count"]
    
    if job_count == 0:
        sample_jobs = [
            (
                "Senior Python & AI Engineer",
                "Engineering",
                "San Francisco, CA (Hybrid)",
                "Senior (5+ yrs)",
                json.dumps(["Python", "FastAPI", "Docker", "PostgreSQL", "Machine Learning", "LLM APIs", "Redis"]),
                "We are seeking an experienced Senior Python & AI Engineer to build scalable backend microservices and integrate LLM-based autonomous workflows. Requires strong proficiency in Python, modern API frameworks like FastAPI, relational databases (PostgreSQL), Docker, and production AI application development.",
                "Open",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "Frontend React & UI/UX Developer",
                "Product & Design",
                "Remote (US / EU)",
                "Mid-Senior (3-5 yrs)",
                json.dumps(["React", "TypeScript", "Next.js", "Tailwind CSS", "Redux", "REST APIs", "Jest"]),
                "Join our frontend team building responsive, high-performance dashboards and rich web applications. Strong command over React 18+, TypeScript, Next.js, modern CSS/Tailwind, and state management is required. Passion for intuitive UI/UX design is a huge plus.",
                "Open",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "DevOps & Cloud Infrastructure Lead",
                "Infrastructure & SRE",
                "Austin, TX",
                "Lead (6+ yrs)",
                json.dumps(["AWS", "Kubernetes", "Terraform", "CI/CD", "Docker", "Linux", "Monitoring"]),
                "Looking for a Cloud Infrastructure Lead to architect resilient multi-region infrastructure on AWS using Terraform and Kubernetes (EKS). Responsible for setting up automated CI/CD deployment pipelines, system observability (Prometheus/Grafana), and security compliance.",
                "Open",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        ]
        
        cursor.executemany('''
            INSERT INTO jobs (title, department, location, experience_level, required_skills, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_jobs)
        conn.commit()
    
    # Check if candidates exist
    cursor.execute("SELECT COUNT(*) as count FROM candidates")
    cand_count = cursor.fetchone()["count"]
    
    if cand_count == 0:
        # Fetch job IDs
        cursor.execute("SELECT id, title FROM jobs ORDER BY id ASC")
        job_rows = cursor.fetchall()
        job_map = {row["title"]: row["id"] for row in job_rows}
        
        python_job_id = job_map.get("Senior Python & AI Engineer")
        frontend_job_id = job_map.get("Frontend React & UI/UX Developer")
        devops_job_id = job_map.get("DevOps & Cloud Infrastructure Lead")
        
        sample_candidates = [
            (
                python_job_id,
                "Alex Rivera",
                "alex.rivera@techmail.io",
                "+1 (555) 234-8901",
                json.dumps(["Python", "FastAPI", "Docker", "PostgreSQL", "LLM APIs", "PyTorch", "Redis"]),
                "Senior backend engineer with 6 years experience architecting high-throughput distributed systems in Python and FastAPI. Led integration of OpenAI and Groq LLMs for automated data pipelines. Proficient in Docker containerization and PostgreSQL indexing.",
                92.5,
                "Interview",
                "Strong technical background in Python and LLM integrations. Passed initial HR screen with flying colors.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                python_job_id,
                "Samantha Patel",
                "samantha.patel@datasolutions.com",
                "+1 (555) 345-6712",
                json.dumps(["Python", "Django", "PostgreSQL", "Machine Learning", "Docker", "Git"]),
                "Full stack Python developer with 4.5 years experience specializing in Django REST and data engineering pipelines. Experienced with PostgreSQL optimization and basic NLP models.",
                84.0,
                "Shortlisted",
                "Solid Python fundamentals. Scheduled for technical panel round next Tuesday.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                python_job_id,
                "David Kim",
                "david.kim92@fastmail.com",
                "+1 (555) 890-4321",
                json.dumps(["Python", "Flask", "SQLite", "HTML/CSS"]),
                "Junior backend programmer with 1.5 years experience building Flask apps and basic REST endpoints. Keen learner exploring machine learning and Docker.",
                58.5,
                "Screening",
                "A bit junior for Senior role, but strong communication. Keep in mind for Mid-level openings.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                frontend_job_id,
                "Elena Rostova",
                "elena.rostova@frontendcraft.dev",
                "+1 (555) 678-1290",
                json.dumps(["React", "TypeScript", "Next.js", "Tailwind CSS", "Redux", "Jest"]),
                "Frontend architect with 5 years building scalable web apps with React, TypeScript, and Next.js. Authored custom design system with Tailwind CSS and achieved 95%+ test coverage using Jest and RTL.",
                94.0,
                "Shortlisted",
                "Exceptional portfolio and UI architecture skills. High priority candidate.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                frontend_job_id,
                "Marcus Vance",
                "marcus.v@creativestudio.org",
                "+1 (555) 789-3412",
                json.dumps(["React", "JavaScript", "Tailwind CSS", "REST APIs", "Figma"]),
                "UI developer with 3 years building responsive client interfaces in React and Tailwind. Strong eye for micro-interactions and collaborative design workflows with Figma.",
                76.5,
                "Interview",
                "Completed portfolio review. Great cultural fit and eye for design.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                frontend_job_id,
                "Chloe Bennett",
                "chloe.b@mailbox.net",
                "+1 (555) 123-9874",
                json.dumps(["HTML", "CSS", "jQuery", "WordPress", "Basic React"]),
                "Web designer with experience in WordPress theme customization and landing page styling. Familiar with introductory React components.",
                42.0,
                "Rejected",
                "Lacks required modern React, TypeScript, and Next.js proficiency.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                devops_job_id,
                "Vikram Malhotra",
                "vikram.m@cloudinfra.io",
                "+1 (555) 432-8765",
                json.dumps(["AWS", "Kubernetes", "Terraform", "CI/CD", "Docker", "Linux", "Prometheus"]),
                "Senior Cloud & DevOps engineer with 7+ years hands-on experience managing multi-cluster Kubernetes on AWS EKS, GitOps via ArgoCD, and infrastructure as code with Terraform.",
                95.0,
                "Hired",
                "Offer accepted! Starting next month as DevOps Lead.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                devops_job_id,
                "Jordan Lee",
                "jordan.lee@sysops.tech",
                "+1 (555) 876-5432",
                json.dumps(["AWS", "Docker", "Linux", "Jenkins", "Bash"]),
                "System administrator with 4 years maintaining AWS EC2 instances, Jenkins build pipelines, and Linux server patching. Currently learning Kubernetes.",
                68.0,
                "Applied",
                "New applicant. Needs review on Kubernetes depth.",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        ]
        
        cursor.executemany('''
            INSERT INTO candidates (job_id, name, email, phone, skills, summary, match_score, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_candidates)
        conn.commit()
        
    conn.close()

# --- JOB CRUD OPERATIONS ---
def get_jobs(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
        SELECT j.*, 
               COUNT(c.id) as applicant_count,
               COALESCE(AVG(c.match_score), 0) as avg_match_score
        FROM jobs j
        LEFT JOIN candidates c ON j.id = c.job_id
    '''
    params = []
    if status:
        query += ' WHERE j.status = ?'
        params.append(status)
    query += ' GROUP BY j.id ORDER BY j.id DESC'
    
    rows = cursor.execute(query, params).fetchall()
    jobs = []
    for r in rows:
        skills = []
        if r['required_skills']:
            try:
                skills = json.loads(r['required_skills'])
            except Exception:
                skills = [s.strip() for s in r['required_skills'].split(',') if s.strip()]
        jobs.append({
            "id": r['id'],
            "title": r['title'],
            "department": r['department'] or "General",
            "location": r['location'] or "Remote",
            "experience_level": r['experience_level'] or "Not specified",
            "required_skills": skills,
            "description": r['description'] or "",
            "status": r['status'] or "Open",
            "created_at": r['created_at'],
            "applicant_count": r['applicant_count'],
            "avg_match_score": round(float(r['avg_match_score']), 1)
        })
    conn.close()
    return jobs

def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute('''
        SELECT j.*, 
               COUNT(c.id) as applicant_count,
               COALESCE(AVG(c.match_score), 0) as avg_match_score
        FROM jobs j
        LEFT JOIN candidates c ON j.id = c.job_id
        WHERE j.id = ?
        GROUP BY j.id
    ''', (job_id,)).fetchone()
    conn.close()
    if not row:
        return None
    skills = []
    if row['required_skills']:
        try:
            skills = json.loads(row['required_skills'])
        except Exception:
            skills = [s.strip() for s in row['required_skills'].split(',') if s.strip()]
    return {
        "id": row['id'],
        "title": row['title'],
        "department": row['department'] or "General",
        "location": row['location'] or "Remote",
        "experience_level": row['experience_level'] or "Not specified",
        "required_skills": skills,
        "description": row['description'] or "",
        "status": row['status'] or "Open",
        "created_at": row['created_at'],
        "applicant_count": row['applicant_count'],
        "avg_match_score": round(float(row['avg_match_score']), 1)
    }

def create_job(title: str, department: str, location: str, experience_level: str, required_skills: List[str], description: str, status: str = "Open") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    skills_json = json.dumps(required_skills) if isinstance(required_skills, list) else str(required_skills)
    cursor.execute('''
        INSERT INTO jobs (title, department, location, experience_level, required_skills, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        title.strip(),
        department.strip(),
        location.strip(),
        experience_level.strip(),
        skills_json,
        description.strip(),
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def update_job_status(job_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (new_status, job_id))
    conn.commit()
    conn.close()

def delete_job(job_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE job_id = ?", (job_id,))
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

# --- CANDIDATE CRUD OPERATIONS ---
def get_candidates(job_id: Optional[int] = None, status: Optional[str] = None, search: Optional[str] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT c.*, j.title as job_title, j.department as job_department
        FROM candidates c
        LEFT JOIN jobs j ON c.job_id = j.id
        WHERE 1=1
    '''
    params = []
    
    if job_id:
        query += " AND c.job_id = ?"
        params.append(job_id)
        
    if status and status != "All":
        query += " AND c.status = ?"
        params.append(status)
        
    if min_score is not None:
        query += " AND c.match_score >= ?"
        params.append(min_score)
        
    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query += " AND (LOWER(c.name) LIKE ? OR LOWER(c.skills) LIKE ? OR LOWER(c.summary) LIKE ? OR LOWER(c.email) LIKE ?)"
        params.extend([term, term, term, term])
        
    query += " ORDER BY c.match_score DESC, c.id DESC"
    
    rows = cursor.execute(query, params).fetchall()
    candidates = []
    for r in rows:
        skills = []
        if r['skills']:
            try:
                skills = json.loads(r['skills'])
                if not isinstance(skills, list):
                    skills = [str(skills)]
            except Exception:
                skills = [s.strip() for s in str(r['skills']).split(',') if s.strip()]
        candidates.append({
            "id": r['id'],
            "job_id": r['job_id'],
            "job_title": r['job_title'] or "General Application",
            "job_department": r['job_department'] or "N/A",
            "name": r['name'] or "Unknown Candidate",
            "email": r['email'] or "N/A",
            "phone": r['phone'] or "N/A",
            "skills": skills,
            "summary": r['summary'] or "",
            "match_score": round(float(r['match_score'] or 0.0), 1),
            "status": r['status'] or "Applied",
            "notes": r['notes'] or "",
            "created_at": r['created_at']
        })
    conn.close()
    return candidates

def get_candidate_by_id(candidate_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute('''
        SELECT c.*, j.title as job_title, j.required_skills as job_skills
        FROM candidates c
        LEFT JOIN jobs j ON c.job_id = j.id
        WHERE c.id = ?
    ''', (candidate_id,)).fetchone()
    conn.close()
    if not row:
        return None
    skills = []
    if row['skills']:
        try:
            skills = json.loads(row['skills'])
        except Exception:
            skills = [str(row['skills'])]
    return {
        "id": row['id'],
        "job_id": row['job_id'],
        "job_title": row['job_title'] or "General",
        "job_skills": row['job_skills'],
        "name": row['name'],
        "email": row['email'],
        "phone": row['phone'],
        "skills": skills,
        "summary": row['summary'],
        "match_score": round(float(row['match_score'] or 0.0), 1),
        "status": row['status'],
        "notes": row['notes'] or "",
        "created_at": row['created_at']
    }

def insert_candidate(job_id: Optional[int], info: Dict[str, Any], match_score: float, status: Optional[str] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    skills = info.get("Skills", [])
    if not isinstance(skills, list):
        skills = [str(skills)] if skills else []
        
    if not status:
        if match_score >= 75.0:
            status = "Shortlisted"
        elif match_score >= 50.0:
            status = "Screening"
        else:
            status = "Applied"
            
    cursor.execute('''
        INSERT INTO candidates (job_id, name, email, phone, skills, summary, match_score, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id,
        str(info.get("Name", "N/A")),
        str(info.get("Email", "N/A")),
        str(info.get("Phone", "N/A")),
        json.dumps(skills),
        str(info.get("Summary", "")),
        round(float(match_score), 1),
        status,
        info.get("Notes", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_candidate_status(candidate_id: int, new_status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
    conn.commit()
    conn.close()

def update_candidate_notes(candidate_id: int, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET notes = ? WHERE id = ?", (notes, candidate_id))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()

# --- AGGREGATED METRICS FOR DASHBOARD ---
def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Jobs count
    total_jobs = cursor.execute("SELECT COUNT(*) as cnt FROM jobs").fetchone()["cnt"]
    open_jobs = cursor.execute("SELECT COUNT(*) as cnt FROM jobs WHERE status = 'Open'").fetchone()["cnt"]
    
    # Candidate stats
    total_candidates = cursor.execute("SELECT COUNT(*) as cnt FROM candidates").fetchone()["cnt"]
    shortlisted = cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE status = 'Shortlisted'").fetchone()["cnt"]
    hired = cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE status = 'Hired'").fetchone()["cnt"]
    in_interview = cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE status = 'Interview'").fetchone()["cnt"]
    
    avg_score_row = cursor.execute("SELECT AVG(match_score) as avg_score FROM candidates").fetchone()
    avg_score = round(float(avg_score_row["avg_score"] or 0.0), 1)
    
    top_candidate_row = cursor.execute("SELECT name, match_score FROM candidates ORDER BY match_score DESC LIMIT 1").fetchone()
    top_candidate = {"name": top_candidate_row["name"], "score": round(float(top_candidate_row["match_score"]), 1)} if top_candidate_row else None
    
    # Status breakdown
    status_counts_rows = cursor.execute('''
        SELECT status, COUNT(*) as cnt FROM candidates GROUP BY status
    ''').fetchall()
    status_counts = {r["status"]: r["cnt"] for r in status_counts_rows}
    
    # Ensure all standard stages exist in dict
    stages = ["Applied", "Screening", "Shortlisted", "Interview", "Hired", "Rejected"]
    for s in stages:
        if s not in status_counts:
            status_counts[s] = 0
            
    # Score distribution
    score_bins = {
        "High Fit (80-100%)": cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE match_score >= 80").fetchone()["cnt"],
        "Moderate Fit (60-79%)": cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE match_score >= 60 AND match_score < 80").fetchone()["cnt"],
        "Potential Fit (40-59%)": cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE match_score >= 40 AND match_score < 60").fetchone()["cnt"],
        "Low Fit (<40%)": cursor.execute("SELECT COUNT(*) as cnt FROM candidates WHERE match_score < 40").fetchone()["cnt"]
    }
    
    # Skills frequency
    all_skills_rows = cursor.execute("SELECT skills FROM candidates").fetchall()
    skill_freq = {}
    for r in all_skills_rows:
        if r["skills"]:
            try:
                s_list = json.loads(r["skills"])
                if isinstance(s_list, list):
                    for skill in s_list:
                        sk = str(skill).strip().title()
                        if sk:
                            skill_freq[sk] = skill_freq.get(sk, 0) + 1
            except Exception:
                pass
                
    # Sort top skills
    top_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    conn.close()
    
    return {
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "shortlist_rate": round((shortlisted / total_candidates * 100), 1) if total_candidates > 0 else 0.0,
        "hired": hired,
        "in_interview": in_interview,
        "avg_score": avg_score,
        "top_candidate": top_candidate,
        "status_counts": status_counts,
        "score_bins": score_bins,
        "top_skills": top_skills
    }

