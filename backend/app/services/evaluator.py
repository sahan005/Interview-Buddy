from typing import Dict, Any, Optional
from ..schemas import AnswerEvaluation
from .llm import llm_service

def evaluate_answer(
    question_text: str,
    topic: str,
    category: str,
    candidate_answer: str,
    question_index: int,
    grounded_context: str = ""
) -> AnswerEvaluation:
    """
    Component 3: Evaluator Agent
    Scores candidate answers on technical depth, relevance, specificity, and evidence.
    Determines summary badge, strengths, weaknesses, and difficulty adjustment.
    """
    answer_clean = candidate_answer.strip()
    word_count = len(answer_clean.split())

    # If Gemini is available
    if llm_service.is_available():
        prompt = f"""
Evaluate the following interview response with extreme technical precision.
Do NOT invent facts or give empty praise.
Consider the question, category, and retrieved contextual background.

Question: {question_text}
Topic: {topic}
Category: {category}
Context: {grounded_context[:1000]}

Candidate Answer:
{candidate_answer}

Return JSON with this schema:
{{
  "score": float between 1.0 and 10.0 (be realistic; good answers 7-8.5, exceptional 9-10, brief/vague 4-6),
  "summary_indicator": "Short phrase e.g. 'Strong technical depth', 'Good practical ownership', 'Lacks architecture specifics', or 'Needs more technical depth'",
  "strengths": ["1 to 2 bullet points describing concrete positives"],
  "weaknesses": ["1 to 2 bullet points describing missing depth, trade-offs, or precision"],
  "missing_points": ["1 key element that could have elevated the answer"],
  "suggested_followup": "Optional follow-up question if deeper probing is needed, else null",
  "difficulty_adjustment": "increase" (if score >= 8.0) or "decrease" (if score < 6.0) or "maintain"
}}
"""
        res = llm_service.generate_json(
            prompt,
            system_instruction="You are a rigorous technical interviewer evaluating answers objectively based on technical depth and communication."
        )
        if res and "score" in res:
            score = float(res.get("score", 7.0))
            score = max(1.0, min(10.0, round(score, 1)))
            adj = res.get("difficulty_adjustment", "maintain")
            if score >= 8.0:
                adj = "increase"
            elif score < 5.5:
                adj = "decrease"

            return AnswerEvaluation(
                question_index=question_index,
                score=score,
                summary_indicator=res.get("summary_indicator", "Solid response"),
                strengths=res.get("strengths", ["Clear explanation"]),
                weaknesses=res.get("weaknesses", ["Could add more metric-driven specifics"]),
                missing_points=res.get("missing_points", []),
                suggested_followup=res.get("suggested_followup"),
                difficulty_adjustment=adj
            )

    # Heuristic evaluation fallback for offline/deterministic scenarios
    if word_count < 15:
        return AnswerEvaluation(
            question_index=question_index,
            score=4.5,
            summary_indicator="Needs more technical depth",
            strengths=["Direct answer to the prompt"],
            weaknesses=["Response was very brief and lacked concrete technical specifics"],
            missing_points=["Specific architectural trade-offs and implementation examples"],
            suggested_followup=f"Could you walk me through a specific scenario where you implemented {topic} in production?",
            difficulty_adjustment="decrease"
        )
    elif word_count < 45:
        return AnswerEvaluation(
            question_index=question_index,
            score=6.8,
            summary_indicator="Good foundational answer",
            strengths=["Addressed the core requirement", "Demonstrated familiarity with principles"],
            weaknesses=["Could elaborate on performance metrics or failure edge cases"],
            missing_points=["Quantified impact and error handling strategy"],
            suggested_followup=None,
            difficulty_adjustment="maintain"
        )
    else:
        # Longer, detailed answer
        return AnswerEvaluation(
            question_index=question_index,
            score=8.4,
            summary_indicator="Strong technical depth",
            strengths=["Detailed technical justification", "Demonstrated clear hands-on experience"],
            weaknesses=["Could explicitly highlight system monitoring and observability aspects"],
            missing_points=["Production telemetry or rollback strategy"],
            suggested_followup=None,
            difficulty_adjustment="increase"
        )
