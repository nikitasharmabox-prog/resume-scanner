import os
import io
import sys
import json
import re
import shutil
from typing import Dict, Any, List, Tuple, Optional
import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

GROQ_MODEL = "openai/gpt-oss-120b"

def configure_tesseract() -> bool:
    """
    Auto-detect and configure the Tesseract OCR executable path across Windows, macOS, and Linux.
    Fixes Windows 'tesseract is not installed or it's not in your PATH' errors.
    """
    # 1. Check custom path in secrets or environment variable
    custom_path = None
    try:
        custom_path = st.secrets.get("TESSERACT_PATH")
    except Exception:
        pass
    if not custom_path:
        custom_path = os.environ.get("TESSERACT_PATH")
        
    if custom_path and os.path.isfile(custom_path):
        pytesseract.pytesseract.tesseract_cmd = custom_path
        return True

    # 2. Check if tesseract binary is already available on system PATH
    if shutil.which("tesseract"):
        return True

    # 3. Check common Windows installation paths
    if sys.platform.startswith("win"):
        win_candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Tesseract-OCR\tesseract.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Tesseract-OCR\tesseract.exe"),
        ]
        for p in win_candidates:
            if os.path.isfile(p):
                pytesseract.pytesseract.tesseract_cmd = p
                return True

    # 4. Check common macOS paths
    for mac_path in ["/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract", "/usr/bin/tesseract"]:
        if os.path.isfile(mac_path):
            pytesseract.pytesseract.tesseract_cmd = mac_path
            return True

    return False

def get_groq_client() -> Groq:
    """Initialize Groq client with API key from secrets or environment."""
    api_key = None
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
        
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured! Please add it to .streamlit/secrets.toml or set GROQ_API_KEY environment variable.")
    return Groq(api_key=api_key)

def extract_text_from_file(file) -> str:
    """Extract text from uploaded PDF or image file with OCR fallback and Windows auto-detection."""
    ext = os.path.splitext(file.name)[1].lower()
    text = ""
    file.seek(0)
    file_bytes = file.read()
    
    # Auto-detect Tesseract executable on the system (e.g. Windows Program Files)
    tesseract_available = configure_tesseract()

    if ext == ".pdf":
        # First attempt native digital text extraction via pypdf (requires zero OCR tools)
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception:
            pass

        # If PDF is scanned (no native text) and Tesseract is available, try OCR
        if not text.strip() or len(text.strip()) < 40:
            if tesseract_available:
                try:
                    images = convert_from_bytes(file_bytes)
                    ocr_text = ""
                    for img in images:
                        ocr_text += pytesseract.image_to_string(img) + "\n"
                    if ocr_text.strip():
                        text = ocr_text
                except Exception as e:
                    if not text.strip():
                        return f"Error: OCR extraction failed ({str(e)})"
            else:
                if not text.strip():
                    return (
                        "Error: Could not extract text from this scanned PDF, and Tesseract OCR is not installed on this machine.\n\n"
                        "To fix this on Windows:\n"
                        "1. Download the Windows installer from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                        "2. Run the installer (installs to C:\\Program Files\\Tesseract-OCR)\n\n"
                        "💡 Quick Alternative: Upload a digital PDF (saved from Word/Docs/Canva) or paste the resume text in the box below!"
                    )
    elif ext in [".jpg", ".jpeg", ".png"]:
        if not tesseract_available:
            return (
                "Error: Image OCR requires Tesseract OCR, which is not installed or not in PATH on this Windows laptop.\n\n"
                "### How to fix on Windows (takes 1 minute):\n"
                "1. Download and run the official Windows installer: [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)\n"
                "2. Complete the setup (it installs by default to `C:\\Program Files\\Tesseract-OCR`).\n"
                "3. Restart the Streamlit app — our auto-detection will immediately find it!\n\n"
                "💡 **Instant Workaround**: Upload your resume as a standard PDF file or paste the plain text directly in the box below!"
            )
        try:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
        except Exception as e:
            return (
                f"Error: Image OCR extraction failed ({str(e)}).\n\n"
                "Please verify Tesseract is installed at `C:\\Program Files\\Tesseract-OCR\\tesseract.exe` or paste the resume text directly."
            )
    else:
        return f"Error: Unsupported file format '{ext}'"

    return text.strip() if text.strip() else "Error: No text could be extracted from this document."

def generate_job_description(title: str, skills: str, department: str = "", experience: str = "") -> str:
    """Generate a comprehensive job description using Groq LLM."""
    client = get_groq_client()
    prompt = f"""
You are an expert HR Talent Acquisition Specialist. 
Write a professional, comprehensive, and engaging Job Description for:
- Job Title: {title}
- Department: {department if department else 'Engineering / Operations'}
- Experience Level: {experience if experience else 'Mid-Senior'}
- Core Required Skills: {skills}

Include the following sections with markdown headings:
1. **Role Overview** (A compelling summary of the mission and impact)
2. **Key Responsibilities** (5-7 clear, actionable bullet points)
3. **Required Qualifications & Technical Skills** (detailed requirements)
4. **Nice-to-Have Skills** (complementary technologies and soft skills)
5. **What We Offer** (culture, compensation highlights, growth opportunities)
"""
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

def parse_candidate_resume(resume_text: str) -> Dict[str, Any]:
    """Parse candidate details from resume text into a structured JSON dictionary."""
    client = get_groq_client()
    prompt = f"""
You are an AI resume parser designed to output structured JSON only.
Analyze the following resume text and extract candidate profile details.

Return a valid JSON object with EXACTLY these keys:
- "Name": string (Candidate full name, or "Candidate" if not found)
- "Email": string (Email address, or "N/A" if not found)
- "Phone": string (Phone number, or "N/A" if not found)
- "Skills": array of strings (List of specific technical and domain skills)
- "Summary": string (2-3 sentence executive summary of the candidate's career, strengths, and background)
- "Experience_Years": number or string (estimated total years of professional experience)

Resume Content:
\"\"\"
{resume_text[:4500]}
\"\"\"
"""
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    
    parsed = json.loads(completion.choices[0].message.content)
    if not isinstance(parsed, dict):
        parsed = {}
        
    # Ensure expected keys
    parsed.setdefault("Name", "Candidate")
    parsed.setdefault("Email", "N/A")
    parsed.setdefault("Phone", "N/A")
    if "Skills" not in parsed or not isinstance(parsed["Skills"], list):
        parsed["Skills"] = []
    parsed.setdefault("Summary", "Candidate profile parsed from resume.")
    return parsed

def compute_jd_match_score(
    jd_text: str, 
    required_skills: List[str], 
    resume_text: str, 
    candidate_skills: List[str]
) -> Dict[str, Any]:
    """
    Computes an intuitive scoring percentage (0-100%) of a candidate against a specific Job Description.
    Combines skill keyword coverage and TF-IDF semantic cosine similarity.
    """
    if not jd_text.strip() or not resume_text.strip():
        return {
            "score": 0.0,
            "skill_match_pct": 0.0,
            "matched_skills": [],
            "missing_skills": required_skills or [],
            "tfidf_score": 0.0
        }
        
    # 1. Skill Overlap Matching
    matched_skills = []
    missing_skills = []
    
    resume_lower = resume_text.lower()
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    
    for req in required_skills:
        req_clean = req.strip()
        if not req_clean:
            continue
        req_l = req_clean.lower()
        # Check if in candidate extracted skills or directly in resume text
        if any(req_l in c_sk or c_sk in req_l for c_sk in candidate_skills_lower) or re.search(r'\b' + re.escape(req_l) + r'\b', resume_lower):
            matched_skills.append(req_clean)
        else:
            missing_skills.append(req_clean)
            
    total_req = len(required_skills)
    skill_match_pct = (len(matched_skills) / total_req * 100.0) if total_req > 0 else 75.0

    # 2. TF-IDF Text Cosine Similarity
    tfidf_score = 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf = vectorizer.fit_transform([jd_text, resume_text])
        cos_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        # Calibrate TF-IDF score (raw cosine on long docs is typically 0.20-0.60)
        tfidf_score = min(float(cos_sim) * 160.0, 100.0)
    except Exception:
        tfidf_score = 50.0

    # 3. Composite Score
    # 60% weight on specific required skills, 40% on semantic content similarity
    if total_req > 0:
        composite = 0.60 * skill_match_pct + 0.40 * tfidf_score
    else:
        composite = tfidf_score

    final_score = round(max(0.0, min(composite, 99.5)), 1)
    
    return {
        "score": final_score,
        "skill_match_pct": round(skill_match_pct, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "tfidf_score": round(tfidf_score, 1)
    }

def ask_hr_chat_assistant(messages: List[Dict[str, str]], jobs_data: List[Dict[str, Any]], candidates_data: List[Dict[str, Any]]) -> str:
    """Interactive HR Chat Assistant with contextual knowledge of all jobs and candidates."""
    client = get_groq_client()
    
    # Format a compact context for the LLM
    jobs_summary = [
        {
            "id": j["id"],
            "title": j["title"],
            "department": j["department"],
            "required_skills": j["required_skills"],
            "applicants": j["applicant_count"],
            "status": j["status"]
        } for j in jobs_data
    ]
    
    candidates_summary = [
        {
            "name": c["name"],
            "job_applied": c["job_title"],
            "match_score": f"{c['match_score']}%",
            "status": c["status"],
            "skills": c["skills"][:7],
            "summary": c["summary"][:160],
            "notes": c["notes"]
        } for c in candidates_data
    ]
    
    system_prompt = f"""
You are 'TalentMatch AI Assistant', an intelligent, proactive HR recruitment companion.
You have real-time access to the company's active Job Openings and Screened Candidates Database.

Active Jobs ({len(jobs_summary)}):
{json.dumps(jobs_summary, indent=2)}

Candidate Database ({len(candidates_summary)}):
{json.dumps(candidates_summary, indent=2)}

Guidelines:
- Answer questions accurately using the provided database.
- When asked for recommendations, compare candidate skills against job requirements.
- Format responses clearly using markdown tables, bullet points, and highlight scores.
- Offer actionable advice: suggest interview questions, highlight skill gaps, or draft outreach/interview invitation emails when requested.
- Maintain a professional, encouraging HR tone.
"""

    chat_context = [{"role": "system", "content": system_prompt}]
    # Keep last 8 turns of conversation
    for m in messages[-8:]:
        chat_context.append({"role": m["role"], "content": m["content"]})
        
    res = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=chat_context,
        temperature=0.5,
        max_tokens=1200
    )
    return res.choices[0].message.content

