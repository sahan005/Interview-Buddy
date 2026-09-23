from typing import List, Dict, Any, Optional
from ..schemas import Question, RAGChunk, AnswerEvaluation
from .rag import VectorRAGIndex
from .llm import llm_service

class InterviewerAgent:
    """
    Component 2: Adaptive Interviewer Agent
    Maintains interview state, dynamically selects topics using LLM + ChromaDB RAG,
    adjusts difficulty, and synthesizes candidate-grounded questions.
    """
    def __init__(
        self,
        rag: VectorRAGIndex,
        total_questions: int = 8,
        interview_type: str = "Mixed",
        base_difficulty: str = "Adaptive"
    ):
        self.rag = rag
        self.total_questions = total_questions
        self.interview_type = interview_type
        self.base_difficulty = base_difficulty
        self.current_difficulty: str = "medium" if base_difficulty in ["Adaptive", "Medium"] else base_difficulty.lower()
        
        self.questions_asked: List[Question] = []
        self.evaluations: List[AnswerEvaluation] = []
        self.candidate_answers: List[str] = []
        self.topics_covered: List[str] = []
        self.remaining_topics: List[str] = []

    def _determine_category(self, q_num: int, last_eval: Optional[AnswerEvaluation]) -> str:
        if last_eval and last_eval.suggested_followup and q_num % 3 == 0:
            return "Follow-up"

        if self.interview_type == "Technical":
            categories = ["Resume/project", "Technical fundamentals", "System design", "Problem solving", "Role-specific"]
            return categories[q_num % len(categories)]
        elif self.interview_type == "Behavioral":
            categories = ["Behavioral", "Resume/project", "Problem solving"]
            return categories[q_num % len(categories)]
        else: # Mixed
            cycle = [
                "Resume/project",
                "Technical fundamentals",
                "Role-specific",
                "Problem solving",
                "Behavioral",
                "Follow-up",
                "System design",
                "Role-specific"
            ]
            return cycle[(q_num - 1) % len(cycle)]

    def adjust_difficulty(self, adjustment: str):
        if self.base_difficulty != "Adaptive":
            return
        levels = ["easy", "medium", "hard"]
        curr_idx = levels.index(self.current_difficulty) if self.current_difficulty in levels else 1
        if adjustment == "increase" and curr_idx < len(levels) - 1:
            self.current_difficulty = levels[curr_idx + 1]
        elif adjustment == "decrease" and curr_idx > 0:
            self.current_difficulty = levels[curr_idx - 1]

    def generate_next_question(
        self,
        last_eval: Optional[AnswerEvaluation] = None
    ) -> Question:
        q_index = len(self.questions_asked) + 1
        
        if last_eval:
            self.adjust_difficulty(last_eval.difficulty_adjustment)

        category = self._determine_category(q_index, last_eval)

        # Retrieve relevant chunks from ChromaDB for this interview stage
        retrieved_resume = self.rag.query("experience responsibilities tools projects", source_filter="resume", top_k=4)
        retrieved_jd = self.rag.query("responsibilities requirements qualifications role", source_filter="job_description", top_k=2)
        
        all_chunks = retrieved_resume + retrieved_jd
        resume_context = "\n".join([c.text for c in retrieved_resume])
        jd_context = "\n".join([c.text for c in retrieved_jd])

        prev_topics = ", ".join(self.topics_covered) if self.topics_covered else "None yet"
        prev_feedback = [f"Q{e.question_index}: {e.summary_indicator}" for e in self.evaluations[-2:]]

        # Call Gemini LLM to generate dynamically for ANY domain/role
        if llm_service.is_available():
            prompt = f"""
You are conducting an adaptive job interview.
Question #{q_index} of {self.total_questions}.
Category: {category}
Difficulty: {self.current_difficulty}
Previously Covered Topics: {prev_topics}
Recent Feedback: {prev_feedback}

Candidate Resume Background:
{resume_context[:1500]}

Target Job Requirements:
{jd_context[:1500]}

Task:
1. Choose a relevant topic for this question that has NOT been heavily covered yet.
2. Formulate a realistic, challenging, conversational question tailored specifically to this candidate and target role.
3. If referencing candidate experience, ground it strictly in the resume. Do NOT hallucinate.
4. No emojis.

Return ONLY a JSON object:
{{
  "topic": "Specific topic name (e.g. 'SQL Optimization', 'A/B Testing', 'Stakeholder Communication')",
  "question": "The exact question text to ask the candidate",
  "reason": "Why this question and topic was selected",
  "context_bullet": "Optional brief citation grounded in resume (e.g. 'Based on your experience with X') or null"
}}
"""
            res = llm_service.generate_json(
                prompt,
                system_instruction="You are a professional adaptive interviewer generating tailored questions based on candidate background and job requirements."
            )
            if res and res.get("question") and res.get("topic"):
                topic = res.get("topic")
                self.topics_covered.append(topic)
                q_obj = Question(
                    question_index=q_index,
                    question=res.get("question"),
                    category=category,
                    topic=topic,
                    difficulty=self.current_difficulty,
                    reason=res.get("reason", f"Assessing {topic} at {self.current_difficulty} difficulty"),
                    requires_resume_context=category in ["Resume/project", "Problem solving"],
                    context_bullet=res.get("context_bullet"),
                    retrieved_chunks=all_chunks
                )
                self.questions_asked.append(q_obj)
                return q_obj

        # Fallback if API completely unreachable
        topic = "Core Experience & Responsibilities"
        self.topics_covered.append(topic)
        q_obj = Question(
            question_index=q_index,
            question=f"Could you walk me through a major project from your experience that best demonstrates your qualifications for this role? What key challenges did you face and how did you resolve them?",
            category=category,
            topic=topic,
            difficulty=self.current_difficulty,
            reason="Assessing core experience",
            requires_resume_context=True,
            context_bullet=None,
            retrieved_chunks=all_chunks
        )
        self.questions_asked.append(q_obj)
        return q_obj
