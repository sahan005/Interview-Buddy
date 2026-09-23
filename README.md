# Resume Interview Agent

A production-style, adaptive technical and behavioral interview web application powered by **Retrieval-Augmented Generation (RAG)** and an **Agentic AI architecture**.

Built with a restrained, high-density **developer/productivity SaaS aesthetic** (Linear/Vercel styling, dark charcoal palette, sharp typography, zero emojis).

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph Client [Frontend (React + TypeScript + Tailwind)]
        UI_Upload[Resume Upload & JD Input]
        UI_Insight[Pre-Interview Briefing]
        UI_Session[Adaptive Interview Arena]
        UI_Report[Performance Scorecard & Review]
    end

    subgraph Backend [FastAPI Backend]
        Parser[Document Parser (PyMuPDF / docx)]
        RAG[RAG Vector Engine (Cosine TF-IDF Chunk Index)]
        
        subgraph Agents [Agentic Interview Engine]
            Planner[1. Interview Planner]
            Interviewer[2. Adaptive Interviewer Agent]
            Evaluator[3. Evaluator Agent]
            ReportGen[4. Report Generator]
        end
        
        LLM[Google Gemini API / Contextual Fallback]
    end

    UI_Upload -->|PDF / DOCX & JD Text| Parser
    Parser --> RAG
    RAG --> Planner
    Planner --> UI_Insight
    UI_Insight --> Interviewer
    Interviewer --> UI_Session
    UI_Session -->|Candidate Answer| Evaluator
    Evaluator -->|Score & Difficulty Adjustment| Interviewer
    Interviewer -->|Next Adaptive Question| UI_Session
    Evaluator -->|Full Transcript| ReportGen
    ReportGen --> UI_Report
    
    Agents <--> LLM
    Agents <--> RAG
```

---

## 2. Why This Is Agentic

Traditional interview bots iterate through static script questions. **Resume Interview Agent** operates as an autonomous multi-step loop with distinct responsibilities:

1. **Stateful Trajectory Management**:
   The agent maintains an evolving memory of `covered_topics`, `remaining_topics`, `candidate_answers`, and prior `evaluations`.
2. **Dynamic Topic Selection**:
   Rather than asking random questions, the agent interleaves candidate-confirmed strengths with target-role gaps identified during RAG analysis.
3. **Adaptive Difficulty Scaling**:
   The Evaluator agent scores responses on technical depth, relevance, and specificity. Strong answers bump subsequent questions to higher difficulty levels (probing edge cases, observability, and scaling bottlenecks), while brief answers prompt clarification or fundamental questions.
4. **Context-Grounded Follow-ups**:
   When an answer introduces an interesting design choice or misses critical failure modes, the agent can trigger targeted follow-up questions directly grounded in that exchange.

---

## 3. Why This Uses RAG

Standard LLM prompting suffers from hallucinations or generic questions that sound identical for every candidate. This application uses **grounded retrieval**:

1. **Dual Source Ingestion**:
   Resumes and job descriptions are chunked and tagged with source metadata (`resume` vs `job_description`) and section headers.
2. **Context-Aware Retrieval**:
   Before generating a question about a specific topic (e.g., PostgreSQL query optimization), the agent retrieves the exact bullet points from the candidate's resume and the corresponding requirements from the job description.
3. **No Experience Hallucination**:
   The agent strictly differentiates between skills confirmed on the resume and skills required by the job. It never falsely claims a candidate has experience in technologies not found in their resume.

---

## 4. Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Lucide React (SVG icons), Vite
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Document Extraction**: PyMuPDF (`pymupdf`), `python-docx`
- **RAG / Vector Engine**: Scikit-Learn (TF-IDF sublinear vectorizer + Cosine Similarity chunk index)
- **AI / LLM**: Google Gemini (`google-genai` SDK), with structured JSON schema enforcement and a deterministic context-aware fallback for immediate offline demonstration.

---

## 5. Quick Start Guide

### Prerequisites
- Node.js v18+ and npm
- Python 3.10+

### Step 1: Clone & Set Up Backend

```bash
# In project root
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# (Optional) Set your Gemini API key in .env
echo "GEMINI_API_KEY=your_key_here" > backend/.env
```

### Step 2: Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

### Step 3: Run the Application

In terminal 1 (Backend):
```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

In terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Visit **`http://localhost:5173`** in your browser.

---

## 6. End-to-End Workflow

1. **Setup Screen**:
   - Upload your own resume (PDF/DOCX) or click **"Load Sample Data (Backend Role)"** to test immediately with realistic data.
   - Enter job description and choose interview parameters (Technical, Behavioral, or Mixed; Adaptive, Easy, Medium, or Hard; 5, 8, or 10 questions).
   - Click **"Start Interview"**.
2. **Analysis Transition**:
   - Watch smooth progress states as the system parses the documents, chunks the content, and indexes embeddings into the vector store.
3. **Pre-Interview Briefing**:
   - Review synthesized candidate profile, verified strong areas, areas to probe, and primary role themes.
   - Click **"Begin Interview"**.
4. **Adaptive Interview Arena**:
   - Answer questions one at a time using the keyboard (`⌘ + Enter` / `Ctrl + Enter`).
   - Notice the subtle evaluation badge on the previous response and live difficulty adjustments.
   - Inspect the live session context in the right sidebar.
5. **Final Performance Report**:
   - Comprehensive overall calculated score (e.g. 78/100).
   - Category performance breakdown bars (Technical Skills, Problem Solving, Communication, Role Fit, System Architecture).
   - Confirmed key strengths and areas for improvement.
   - Collapsible question-by-question review with scores and feedback.
   - Actionable preparation recommendations.
   - Click **"Retake Interview"** to restart anytime.

---

## 7. Running Verification Tests

Run the backend unit & integration tests:
```bash
source .venv/bin/activate
python backend/test_backend.py
python backend/test_api_flow.py
```

Run frontend production build:
```bash
cd frontend
npm run build
```
