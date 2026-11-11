# AI Resume Screening & HR Assistant

An intelligent, full-stack HR recruitment assistant built with **Streamlit**, **Groq LLM** (`llama-3.1-8b-instant`), **Tesseract OCR**, and **scikit-learn**.

The application streamlines candidate screening by generating job descriptions, extracting candidate details from multiple resume formats (PDF, PNG, JPG), computing similarity scores against job requirements, storing candidate records in an SQLite database, and providing an interactive AI chatbot to query candidate data.

---

## Features

- **Job Description Generator**: Quickly generate structured job descriptions from job titles and required skills using Groq's high-speed inference.
- **Multi-Format Resume Extraction**:
  - Direct text parsing from PDFs using `pypdf`.
  - Fallback OCR extraction for scanned PDFs and image resumes (`.jpg`, `.jpeg`, `.png`) using `pdf2image` and `pytesseract`.
- **Structured Candidate Parsing**: Extracts candidate information (`Name`, `Email`, `Phone`, `Skills`, `Summary`) into clean JSON via Groq.
- **Match Score Calculation**: Computes semantic text similarity between the Job Description and Resume using TF-IDF vectorization and Cosine Similarity.
- **Candidate Database**: Automatically logs screened candidates and their status (`Shortlisted` vs. `Reviewed`) into a local SQLite database (`candidates.db`).
- **Interactive HR Chatbot**: Ask natural language questions about all screened candidates (e.g. *"Who has experience in Python and Docker?"* or *"List all shortlisted candidates"*).

---

## Tech Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **LLM Engine**: [Groq Cloud](https://console.groq.com/) (`llama-3.1-8b-instant`)
- **Document / Image Processing**: `pypdf`, `pdf2image`, `pytesseract`, `Pillow`
- **Text Matching**: `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`)
- **Database**: SQLite3

---

## Prerequisites

### 1. System Dependencies (OCR & PDF Rendering)

- **macOS** (via Homebrew):
  ```bash
  brew install tesseract poppler
  ```
- **Ubuntu / Debian**:
  ```bash
  sudo apt update
  sudo apt install -y tesseract-ocr poppler-utils
  ```

---

## Setup & Installation

### 1. Clone the repository & create a virtual environment

```bash
git clone <repo-url>
cd resume-scanner

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (cmd/PowerShell):
# venv\Scripts\activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Secrets

Create `.streamlit/secrets.toml` in the project root:

```bash
mkdir -p .streamlit
touch .streamlit/secrets.toml
```

Add your [Groq API Key](https://console.groq.com/keys) to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_groq_api_key_here"
```

---

## Running the Application

Ensure your virtual environment is active, then launch Streamlit:

```bash
streamlit run app.py
```

The application will open in your default browser at:
```text
http://localhost:8501
```

---

## Project Structure

```text
resume-scanner/
├── .devcontainer/       # DevContainer setup for VS Code / GitHub Codespaces
├── .streamlit/
│   └── secrets.toml     # Groq API key configuration (ignored by git)
├── app.py               # Main Streamlit application
├── packages.txt         # System package requirements for Linux / cloud deployment
├── requirements.txt     # Python package dependencies
├── .gitignore           # Git ignore file for secrets and environments
└── README.md            # Project documentation
```
