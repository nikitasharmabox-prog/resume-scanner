import os
import io
import json
import sqlite3
import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import pypdf
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# Set page configuration
st.set_page_config(page_title="AI HR Assistant", layout="wide")

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
        skills = []
        if row['skills']:
            try:
                skills = json.loads(row['skills'])
                if not isinstance(skills, list):
                    skills = [str(skills)]
            except Exception:
                skills = [str(row['skills'])]
        candidates.append({
            "Name": row['name'],
            "Email": row['email'],
            "Phone": row['phone'],
            "Skills": skills,
            "Summary": row['summary'],
            "Match Score": f"{row['match_score']}%",
            "Status": row['status']
        })
    conn.close()
    return candidates

def insert_candidate(info: dict, match_score: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    skills = info.get("Skills", [])
    if not isinstance(skills, list):
        skills = [str(skills)] if skills else []

    cursor.execute('''
        INSERT INTO candidates (name, email, phone, skills, summary, match_score, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(info.get("Name", "N/A")),
        str(info.get("Email", "N/A")),
        str(info.get("Phone", "N/A")),
        json.dumps(skills),
        str(info.get("Summary", "")),
        match_score,
        "Shortlisted" if match_score >= 50.0 else "Reviewed"
    ))
    conn.commit()
    conn.close()

# --- HELPER FUNCTIONS ---
def get_groq_client():
    api_key = st.secrets.get("GROQ_API_KEY") 
    if not api_key:
        st.error("GROQ_API_KEY is missing! Please set it in .streamlit/secrets.toml.")
        st.stop()
    return Groq(api_key=api_key)

def extract_text(file) -> str:
    ext = os.path.splitext(file.name)[1].lower()
    text = ""
    file.seek(0)
    file_bytes = file.read()

    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception:
            pass
        if not text.strip():
            try:
                images = convert_from_bytes(file_bytes)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                return f"Error: OCR extraction failed ({str(e)})"
    elif ext in [".jpg", ".jpeg", ".png"]:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
        except Exception as e:
            return f"Error: Image extraction failed ({str(e)})"
    else:
        return f"Error: Unsupported file format '{ext}'"

    return text.strip() if text.strip() else "No text extracted."

def compute_similarity(text1: str, text2: str) -> float:
    if not text1.strip() or not text2.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0

# Initialize session state variables
if "jd_text" not in st.session_state:
    st.session_state["jd_text"] = ""

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- APP INTERFACE ---
st.title("🤖 Groq AI Resume Screening & HR Assistant")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Generate Job Description")
    job_title = st.text_input("Job Title", placeholder="e.g. Senior Python Developer")
    req_skills = st.text_input("Required Skills", placeholder="e.g. Python, Streamlit, SQL, Docker")
    
    if st.button("Generate JD with Groq"):
        if not job_title.strip():
            st.warning("Please enter a Job Title.")
        else:
            with st.spinner("Generating Job Description with Groq..."):
                try:
                    client = get_groq_client()
                    prompt = f"Write a professional job description for: '{job_title}' requiring skills: '{req_skills}'."
                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.session_state["jd_text"] = res.choices[0].message.content
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating JD: {e}")

    jd_text = st.text_area(
        "Job Description Context", 
        value=st.session_state.get("jd_text", ""), 
        height=180,
        placeholder="Job description will appear here, or you can type/paste your own..."
    )
    # Sync manual edits back to session_state
    st.session_state["jd_text"] = jd_text

with col2:
    st.subheader("2. Candidate Resume Upload")
    uploaded_file = st.file_uploader("Upload PDF / JPG / PNG", type=["pdf", "jpg", "png", "jpeg"])
    raw_text_input = st.text_area("Or Paste Resume Raw Text", height=100, placeholder="Paste resume plain text here...")
    
    if st.button("Screen & Save Candidate"):
        resume_text = ""
        if uploaded_file:
            with st.spinner("Extracting text from file..."):
                resume_text = extract_text(uploaded_file)
        elif raw_text_input.strip():
            resume_text = raw_text_input.strip()
        else:
            st.warning("Please upload a resume file or paste resume raw text.")
            st.stop()

        if resume_text.startswith("Error:"):
            st.error(resume_text)
        elif resume_text == "No text extracted.":
            st.warning("Could not extract any readable text from the file.")
        else:
            with st.spinner("Screening candidate and extracting details with Groq..."):
                try:
                    client = get_groq_client()
                    prompt = (
                        "You are a helpful assistant designed to output JSON.\n"
                        "Extract details as a valid JSON object containing the keys: 'Name', 'Email', 'Phone', 'Skills' (array of strings), 'Summary'.\n"
                        f"Resume:\n{resume_text[:4000]}"
                    )
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"}
                    )
                    parsed = json.loads(completion.choices[0].message.content)
                    if not isinstance(parsed, dict):
                        st.error("Model did not return a valid candidate JSON object.")
                    else:
                        eval_context = jd_text.strip() if jd_text.strip() else "General Evaluation"
                        score = compute_similarity(eval_context, resume_text)
                        insert_candidate(parsed, score)
                        st.success(f"Candidate '{parsed.get('Name', 'Unknown')}' screened & added to Database!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error during screening: {e}")

st.divider()
st.subheader("📊 Screened Candidates Database")
candidates = get_candidates()
if candidates:
    st.dataframe(candidates, use_container_width=True)
else:
    st.info("No candidates screened yet. Upload a resume or paste text to screen.")

st.divider()
st.subheader("💬 3. Interactive HR Chatbot Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question about candidates..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("HR Assistant is thinking..."):
        try:
            client = get_groq_client()
            db_candidates = get_candidates()
            system_prompt = (
                "You are an AI HR assistant. Use the candidate database provided below to answer questions accurately and helpfully.\n"
                f"Candidate Database: {json.dumps(db_candidates)}"
            )
            chat_context = [{"role": "system", "content": system_prompt}]
            # Include recent chat history
            for msg in st.session_state.messages[-6:]:
                chat_context.append({"role": msg["role"], "content": msg["content"]})

            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=chat_context
            )
            reply = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        except Exception as e:
            st.error(f"Chatbot error: {e}")
