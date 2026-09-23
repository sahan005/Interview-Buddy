from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# Document & Analysis Models
class ParsedDocument(BaseModel):
    text: str
    num_pages: int
    sections: List[str] = []
    file_type: str
    filename: str

class StartInterviewRequest(BaseModel):
    resume_text: str
    job_description: str
    interview_type: Literal["Technical", "Behavioral", "Mixed"] = "Mixed"
    difficulty: Literal["Adaptive", "Easy", "Medium", "Hard"] = "Adaptive"
    num_questions: int = 8

class PreInterviewInsight(BaseModel):
    candidate_profile: str
    strong_areas: List[str]
    areas_to_probe: List[str]
    role_focus: List[str]
    raw_resume_snippet: Optional[str] = None
    raw_jd_snippet: Optional[str] = None

class RAGChunk(BaseModel):
    id: str
    source: Literal["resume", "job_description"]
    section: Optional[str] = None
    page: Optional[int] = None
    text: str
    score: float = 0.0

class Question(BaseModel):
    question_index: int
    question: str
    category: Literal[
        "Resume/project",
        "Technical fundamentals",
        "System design",
        "Problem solving",
        "Behavioral",
        "Role-specific",
        "Follow-up"
    ]
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    reason: str
    requires_resume_context: bool = False
    context_bullet: Optional[str] = None
    retrieved_chunks: List[RAGChunk] = []

class AnswerSubmissionRequest(BaseModel):
    session_id: str
    question_index: int
    answer: str

class AnswerEvaluation(BaseModel):
    question_index: int
    score: float = Field(..., ge=0.0, le=10.0)
    summary_indicator: str  # e.g., "Strong answer" or "Needs more technical depth"
    strengths: List[str] = []
    weaknesses: List[str] = []
    missing_points: List[str] = []
    suggested_followup: Optional[str] = None
    difficulty_adjustment: Literal["increase", "maintain", "decrease"] = "maintain"

class CategoryScore(BaseModel):
    category: str
    score: float  # 0 to 100
    description: str

class QuestionReviewItem(BaseModel):
    question_index: int
    question: str
    topic: str
    category: str
    candidate_answer: str
    score: float
    summary_indicator: str
    strengths: List[str]
    areas_to_improve: List[str]

class FinalReport(BaseModel):
    session_id: str
    overall_score: int
    category_performance: List[CategoryScore]
    demonstrated_skills: List[str]
    strengths: List[str]
    areas_to_improve: List[str]
    question_reviews: List[QuestionReviewItem]
    recommended_preparation: List[str]
    interview_type: str
    total_questions: int

class SessionResponse(BaseModel):
    session_id: str
    insight: PreInterviewInsight
    first_question: Question
    total_questions: int
    current_difficulty: str
    interview_type: str
    topics_covered: List[str] = []
    remaining_topics: List[str] = []

class AnswerResponse(BaseModel):
    session_id: str
    is_completed: bool
    evaluation_summary: str
    last_evaluation: AnswerEvaluation
    next_question: Optional[Question] = None
    progress: Dict[str, Any]
    final_report: Optional[FinalReport] = None
