# TalentMatch AI: HR Recruiter Portal & Resume Screening Assistant

An enterprise-ready HR recruitment portal and candidate screening platform built with **Streamlit**, **Groq LLM** (`openai/gpt-oss-120b`), **Tesseract OCR**, and **scikit-learn**.

The application equips HR recruiters with an end-to-end recruitment suite: an authentication portal, recruitment analytics dashboard, AI-powered Job Description (JD) generation, candidate scoring percentages matched directly against specific JDs, an interactive Kanban candidate board, and an interactive AI HR assistant.

---

## ✨ Features & User Journey

### 1. 🔐 HR Recruiter Login Portal
- Professional authentication screen for HR recruiters with session tracking.
- Pre-configured demo login toggle (`⚡ One-Click Instant Demo Login`) for rapid evaluation.
- Personalized recruiter profile in the sidebar with sign-out functionality.

### 2. 🧭 Standard Sidebar Page Layout
- Standard, persistent sidebar navigation:
  - **📊 Dashboard**: High-level recruitment analytics, pipeline funnel, and score distributions.
  - **💼 Jobs & JD Management**: Manage job openings, generate JDs with Groq AI, and inspect candidates scored specifically against each JD.
  - **📋 Candidate Board**: Interactive Kanban-style candidate pipeline tracker across 6 recruitment stages.
  - **💬 AI Recruiter Chat**: Conversational AI assistant with real-time access to the jobs and candidate database.
- Live sidebar pipeline counters (Open Jobs, Candidates Screened, Shortlisted, Avg Score).
- System tools to reload sample demo data or reset candidate tables.

### 3. 📊 Recruitment Analytics Dashboard
- **Key Metric KPI Cards**:
  - Active Open Jobs
  - Screened Candidates count & Interview volume
  - Shortlisted Candidates & Shortlist Conversion Rate (%)
  - Average Candidate Match Score (%) & Top Candidate Leaderboard highlight
- **Interactive Visualizations (Altair)**:
  - Candidate Pipeline Funnel (`Applied` → `Screening` → `Shortlisted` → `Interview` → `Hired` → `Rejected`)
  - Match Score Distribution (High Fit 80-100%, Moderate Fit 60-79%, Potential Fit 40-59%, Low Fit <40%)
  - Top In-Demand Skills frequency in the talent pool
- Top Matching Candidates leaderboard with instant status badges.

### 4. 💼 Jobs & JD Management
- **View All Jobs & Candidates Scored per JD**:
  - Inspect job opening details (department, location, experience, required skills).
  - List all candidates evaluated for that specific job.
  - **Scoring percentage as per JD** with progress bar indicators.
  - Clear breakdown of **Matched Skills** (green badges) vs **Missing Skills** (red badges) against the JD.
  - Update candidate stage directly from the job view.
- **✨ AI Job Description (JD) Generator**:
  - Fill in title, department, experience, and core skills.
  - Generate comprehensive, structured JDs with Groq AI in seconds.
  - Review, edit, and save opening to SQLite.
- **➕ Screen New Candidate for Job**:
  - Upload resumes (PDF, JPG, PNG) or paste plain text.
  - Automatic OCR fallback for scanned documents.
  - AI extraction into structured JSON (Name, Email, Phone, Skills, Career Summary).
  - Compute composite score % (skill coverage + semantic TF-IDF cosine similarity).
  - Instantly links candidate to the target Job in the database.

### 5. 📋 Interactive Candidate Board
- Multi-column pipeline Kanban board:
  - 📥 **Applied** | 🔍 **Screening** | ⭐ **Shortlisted** | 📅 **Interview** | 🤝 **Hired** | ❌ **Rejected**
- Stage count badges and candidate cards showing name, score, target job, and key skills.
- One-click **Move Stage** dropdown to transition candidates across stages in real-time.
- Interactive filter bar: Filter by Job, Minimum Match Score % slider, and search by Name/Skill.
- Candidate quick details expander with recruiter notes editing.

### 6. 💬 Interactive AI Recruiter Chat Assistant
- Chat interface connected to the active SQLite database.
- Answers recruitment queries, compares candidates, highlights strengths/skill gaps, and drafts interview invitation or rejection emails.
- Clickable quick prompt suggestions for common recruiter tasks.

---

## 🛠️ Tech Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **LLM Engine**: [Groq Cloud](https://console.groq.com/) (`openai/gpt-oss-120b`)
- **Document & Image OCR**: `pypdf`, `pdf2image`, `pytesseract`, `Pillow`
- **Text Similarity & Matching**: `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`)
- **Visualizations**: `altair`, `pandas`
- **Database**: SQLite3 (`candidates.db`)

---

## 🚀 Setup & Installation

### 1. Prerequisites (OCR & PDF Rendering)

- **macOS** (via Homebrew):
  ```bash
  brew install tesseract poppler
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt update
  sudo apt install -y tesseract-ocr poppler-utils
  ```

### 2. Virtual Environment & Dependencies

```bash
# Clone the repository
git clone <repo-url>
cd resume-scanner

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Groq API Key

Ensure `.streamlit/secrets.toml` has your Groq API key:

```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```text
resume-scanner/
├── app.py               # Main Streamlit app: Login, Sidebar, Dashboard, Jobs, Board & Chat
├── db.py                # SQLite database management, migrations, seed data & queries
├── ai_helper.py         # Groq LLM integration, JD generation, resume parser & score calculation
├── candidates.db        # SQLite database storing Jobs and Candidates
├── requirements.txt     # Python dependencies
├── packages.txt         # OS-level packages for cloud/Docker deployment
└── README.md            # Comprehensive project documentation
```
