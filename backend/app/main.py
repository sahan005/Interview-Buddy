import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas import (
    ParsedDocument,
    StartInterviewRequest,
    SessionResponse,
    AnswerSubmissionRequest,
    AnswerResponse,
    FinalReport,
    PreInterviewInsight
)
from .services.parser import parse_document
from .services.rag import VectorRAGIndex
from .services.planner import generate_plan
from .services.interviewer import InterviewerAgent
from .services.evaluator import evaluate_answer
from .services.report import generate_final_report
from .services.demo_data import SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION
from .services.llm import llm_service

load_dotenv()

app = FastAPI(
    title="Resume Interview Agent API",
    description="Adaptive technical & behavioral interview platform powered by RAG and Agentic AI",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory interview session store
class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def get(self, session_id: str):
        return self.sessions.get(session_id)

    def set(self, session_id: str, data: Dict):
        self.sessions[session_id] = data

    def delete(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

store = SessionStore()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": llm_service.is_available(),
        "active_sessions": len(store.sessions)
    }

@app.get("/api/demo-data")
def get_demo_data():
    """Return realistic pre-populated resume and job description for 1-click testing."""
    return {
        "sample_resume": SAMPLE_RESUME.strip(),
        "sample_job_description": SAMPLE_JOB_DESCRIPTION.strip(),
        "candidate_name": "Alex Rivera",
        "target_role": "Senior Backend Engineer - Distributed Systems"
    }

@app.post("/api/upload-resume", response_model=ParsedDocument)
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a PDF, DOCX, or text resume."""
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed = parse_document(contents, file.filename)
        return parsed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/api/interview/start", response_model=SessionResponse)
def start_interview(req: StartInterviewRequest):
    """
    RAG ingestion, interview planning, and first question generation.
    """
    resume_clean = req.resume_text.strip()
    jd_clean = req.job_description.strip()

    if not resume_clean:
        raise HTTPException(status_code=400, detail="Resume content is required.")
    if not jd_clean:
        raise HTTPException(status_code=400, detail="Job description is required.")

    # 1. Initialize and build RAG vector index
    rag = VectorRAGIndex()
    rag.build_index(resume_clean, jd_clean)

    # 2. Initialize Adaptive Interviewer Agent (no LLM call yet)
    interviewer = InterviewerAgent(
        rag=rag,
        total_questions=req.num_questions,
        interview_type=req.interview_type,
        base_difficulty=req.difficulty
    )

    # 3. Run planner + first question in parallel (independent LLM calls)
    with ThreadPoolExecutor(max_workers=2) as pool:
        plan_future = pool.submit(
            generate_plan, rag=rag, resume_text=resume_clean,
            jd_text=jd_clean, interview_type=req.interview_type
        )
        q_future = pool.submit(interviewer.generate_next_question)

        insight = plan_future.result()
        first_q = q_future.result()

    session_id = str(uuid.uuid4())
    store.set(session_id, {
        "rag": rag,
        "interviewer": interviewer,
        "insight": insight,
        "total_questions": req.num_questions,
        "interview_type": req.interview_type,
        "difficulty": req.difficulty,
        "final_report": None
    })

    return SessionResponse(
        session_id=session_id,
        insight=insight,
        first_question=first_q,
        total_questions=req.num_questions,
        current_difficulty=interviewer.current_difficulty,
        interview_type=req.interview_type,
        topics_covered=interviewer.topics_covered,
        remaining_topics=interviewer.remaining_topics
    )

@app.post("/api/interview/answer", response_model=AnswerResponse)
def submit_answer(req: AnswerSubmissionRequest):
    """
    Evaluate candidate response, update interview state, adapt difficulty,
    and generate next question or final performance report.
    """
    session = store.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session expired or not found.")

    interviewer: InterviewerAgent = session["interviewer"]
    rag: VectorRAGIndex = session["rag"]

    current_q_idx = req.question_index
    if current_q_idx > len(interviewer.questions_asked):
        raise HTTPException(status_code=400, detail="Invalid question index.")

    current_q = interviewer.questions_asked[current_q_idx - 1]
    
    # Store candidate answer
    interviewer.candidate_answers.append(req.answer)

    # Grounded context for evaluation
    grounded_context = " ".join([c.text for c in current_q.retrieved_chunks])

    is_last_question = len(interviewer.questions_asked) >= session["total_questions"]

    next_q = None
    final_rep = None

    if is_last_question:
        # Last question: evaluate then generate report (sequential, report needs eval)
        evaluation = evaluate_answer(
            question_text=current_q.question,
            topic=current_q.topic,
            category=current_q.category,
            candidate_answer=req.answer,
            question_index=current_q_idx,
            grounded_context=grounded_context
        )
        interviewer.evaluations.append(evaluation)

        final_rep = generate_final_report(
            session_id=req.session_id,
            questions=interviewer.questions_asked,
            answers=interviewer.candidate_answers,
            evaluations=interviewer.evaluations,
            interview_type=session["interview_type"]
        )
        session["final_report"] = final_rep
    else:
        # Mid-interview: run evaluation + next question in parallel
        with ThreadPoolExecutor(max_workers=2) as pool:
            eval_future = pool.submit(
                evaluate_answer,
                question_text=current_q.question,
                topic=current_q.topic,
                category=current_q.category,
                candidate_answer=req.answer,
                question_index=current_q_idx,
                grounded_context=grounded_context
            )
            # Fire next question immediately using previous eval for difficulty
            prev_eval = interviewer.evaluations[-1] if interviewer.evaluations else None
            q_future = pool.submit(interviewer.generate_next_question, last_eval=prev_eval)

            evaluation = eval_future.result()
            next_q = q_future.result()

        interviewer.evaluations.append(evaluation)
        # Apply difficulty adjustment from this eval for the question after next
        interviewer.adjust_difficulty(evaluation.difficulty_adjustment)

    return AnswerResponse(
        session_id=req.session_id,
        is_completed=is_last_question,
        evaluation_summary=evaluation.summary_indicator,
        last_evaluation=evaluation,
        next_question=next_q,
        progress={
            "current_index": len(interviewer.questions_asked) if not is_last_question else session["total_questions"],
            "total": session["total_questions"],
            "difficulty": interviewer.current_difficulty,
            "topics_covered": interviewer.topics_covered
        },
        final_report=final_rep
    )

@app.get("/api/interview/{session_id}/report", response_model=FinalReport)
def get_report(session_id: str):
    """Retrieve final report for a completed session."""
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    report = session.get("final_report")
    if not report:
        raise HTTPException(status_code=400, detail="Interview is still in progress.")
    return report

@app.post("/api/interview/{session_id}/end", response_model=FinalReport)
def end_interview_early(session_id: str):
    """Allow user to conclude interview early and receive report for completed questions."""
    session = store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    interviewer: InterviewerAgent = session["interviewer"]
    if not interviewer.evaluations:
        raise HTTPException(status_code=400, detail="No answers have been evaluated yet.")

    report = generate_final_report(
        session_id=session_id,
        questions=interviewer.questions_asked[:len(interviewer.evaluations)],
        answers=interviewer.candidate_answers,
        evaluations=interviewer.evaluations,
        interview_type=session["interview_type"]
    )
    session["final_report"] = report
    return report
