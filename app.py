import os
import io
import json
import sqlite3
import numpy as np
import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# Set page configuration
st.set_page_config(page_title="AI HR Assistant", page_icon="🚀", layout="wide")

# --- DATABASE SETUP ---
DB_NAME = "candidates.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, skills TEXT,
            summary TEXT, match_score REAL, status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_candidates():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = conn.cursor().execute('SELECT * FROM candidates ORDER BY id DESC').fetchall()
    candidates = []
    for row in rows:
        candidates.append({
            "Name": row['name'], "Email": row['email'], "Phone": row['phone'],
            "Skills": json.loads(row['skills']) if row['skills'] else [],
            "Summary": row['summary'], "Match Score": f"{row['match_score']}%",
            "Status": row['status']
        })
    conn.close()
    return candidates

def insert_candidate(info, match_score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO candidates (name, email, phone, skills, summary, match_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        info.get("Name", "N/A"), info.get("Email", "N/A"), info.get("Phone", "N/A"),
        json.dumps(info.get("Skills", [])), info.get("Summary", ""), match_score,
        "Shortlisted" if match_score >= 50.0 else "Reviewed"
    ))
    conn.commit()
    conn.close()

# --- HELPER FUNCTIONS ---
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") 
    if not api_key:
        st.error("GROQ_API_KEY is missing! Please set it in Streamlit Secrets.")
        st.stop()
    return Groq(api_key=api_key)

def extract_text(file) -> str:
    ext = os.path.splitext(file.name)[1].lower()
    text = ""
    file_bytes = file.read()

    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                if page.extract_text(): text += page.extract_text() + "\n"
        except Exception: pass
        if not text.strip():
            try:
                images = convert_from_bytes(file_bytes)
                for img in images: text += pytesseract.image_to_string(img) + "\n"
            except Exception as e: return f"Error: {str(e)}"
    elif ext in [".jpg", ".jpeg", ".png"]:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
        except Exception as e: return f"Error: {str(e)}"
    return text if text.strip() else "No text extracted."

def compute_similarity(text1: str, text2: str) -> float:
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([text1, text2])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(float(score) * 100, 2)

# --- APP INTERFACE ---
st.title("🚀 Groq AI Resume Screening & HR Assistant")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Generate Job Description")
    job_title = st.text_input("Job Title")
    req_skills = st.text_input("Required Skills")
    if st.button("Generate JD with Groq"):
        client = get_groq_client()
        prompt = f"Write a job description for: '{job_title}' requiring skills: '{req_skills}'."
        res = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}])
        st.session_state['jd_text'] = res.choices[0].message.content

    jd_text = st.text_area("Job Description Context", value=st.session_state.get('jd_text', ''), height=180)

with col2:
    st.subheader("2. Candidate Resume Upload")
    uploaded_file = st.file_uploader("Upload PDF / JPG / PNG", type=["pdf", "jpg", "png", "jpeg"])
    raw_text_input = st.text_area("Or Paste Resume Raw Text", height=100)
    
    if st.button("Screen & Save Candidate"):
        resume_text = ""
        if uploaded_file: resume_text = extract_text(uploaded_file)
        elif raw_text_input.strip(): resume_text = raw_text_input
        
        if resume_text:
            client = get_groq_client()
            prompt = (
                "Extract details as JSON: 'Name', 'Email', 'Phone', 'Skills' (array), 'Summary'. "
                f"Resume:\n{resume_text[:3000]}"
            )
            parsed = json.loads(client.chat.completions.create(
                model="llama3-8b-8192", messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            ).choices[0].message.content)

            score = compute_similarity(jd_text if jd_text else "General Evaluation", resume_text)
            insert_candidate(parsed, score)
            st.success("Candidate screened & added to Database!")
            st.rerun()

st.divider()
st.subheader("Screened Candidates Database")
st.dataframe(get_candidates(), use_container_width=True)

st.divider()
st.subheader("3. Interactive HR Chatbot Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question about candidates..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    client = get_groq_client()
    candidates = get_candidates()
    bot_prompt = f"You are an AI HR assistant. Data: {json.dumps(candidates)}. User Query: {query}"
    res = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": bot_prompt}])
    reply = res.choices[0].message.content
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
