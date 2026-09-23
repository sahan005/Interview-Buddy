# Interview Buddy

An adaptive mock interview application that tailors technical and behavioral questions to your actual resume and a target job description. 

Instead of asking static or generic questions from a fixed question bank, it indexes both documents into a vector store and uses an LLM to generate role-specific questions grounded in your past projects, evaluate your answers in real time, and dynamically adjust difficulty as the interview progresses.

---

## How It Works

### 1. Document Parsing & Ingestion
When you upload a resume (PDF or DOCX) and paste a job description, the backend extracts the text using PyMuPDF and python-docx, cleans it, and splits it into segments of around 150 words with sliding-window overlap. Keeping chunk sizes small ensures individual projects and work experiences stay distinct rather than getting blended together.

### 2. RAG Pipeline (ChromaDB)
All chunks are embedded and indexed into an in-memory ChromaDB collection created specifically for that session.
- **Source Filtering:** Chunks are tagged with metadata (`resume` vs `job_description`).
- **Grounded Retrieval:** When generating a question or analyzing candidate fit, the system runs semantic queries to fetch relevant experience chunks and matching job requirements. This grounds the questions directly in your verified background and prevents hallucinating experience you don't have.
- **Ephemeral Storage:** The vector store is in-memory and exists only for the duration of the interview, avoiding external database dependencies or cross-session data leaks.

### 3. Adaptive Interview Loop
- **Planning:** The planner analyzes retrieved chunks from both documents to identify core candidate strengths, target role focus areas, and potential gaps to probe.
- **Dynamic Questioning:** Questions cycle through categories (projects/experience, technical fundamentals, system design, problem solving, and behavioral). Each question references specific technologies or accomplishments found in your resume.
- **Real-Time Evaluation:** Answers are scored on technical depth, specificity, and structure. Scores trigger difficulty adjustments (increasing complexity to probe scaling, trade-offs, and edge cases, or decreasing if fundamentals need reinforcement).
- **Parallel Execution:** Answer evaluation and next-question generation run concurrently using thread workers, cutting per-question latency in half.

### 4. Performance Report
At the end of the session, the system aggregates all evaluations into a final scorecard:
- Overall score and category breakdowns (Technical Skills, Problem Solving, System Architecture, Communication, Role Fit).
- Concrete strengths and improvement areas extracted from your actual answers.
- Tailored study recommendations targeting weak spots identified during the interview.

---

## Tech Stack

- **Backend:** FastAPI, Python, ChromaDB, PyMuPDF, python-docx
- **LLM:** Google Gemini API (`gemini-3.1-flash-lite`)
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4
