from typing import List, Dict, Any
from ..schemas import FinalReport, CategoryScore, QuestionReviewItem, AnswerEvaluation, Question
from .llm import llm_service

def generate_final_report(
    session_id: str,
    questions: List[Question],
    answers: List[str],
    evaluations: List[AnswerEvaluation],
    interview_type: str
) -> FinalReport:
    """
    Component 4: Final Report Generator
    Synthesizes interview trajectory into an objective, calculated scorecard.
    Scores are strictly derived from the actual evaluation results.
    """
    if not evaluations:
        avg_score = 70.0
    else:
        avg_score = (sum([e.score for e in evaluations]) / len(evaluations)) * 10.0

    overall_score = int(round(avg_score))

    # Category performance breakdown
    cat_evals: Dict[str, List[float]] = {
        "Technical Skills": [],
        "Problem Solving": [],
        "Communication": [],
        "Role Fit": [],
        "System Architecture": []
    }

    for q, e in zip(questions, evaluations):
        score_100 = e.score * 10.0
        if q.category in ["Technical fundamentals", "Resume/project"]:
            cat_evals["Technical Skills"].append(score_100)
        if q.category in ["Problem solving", "Follow-up"]:
            cat_evals["Problem Solving"].append(score_100)
        if q.category in ["System design"]:
            cat_evals["System Architecture"].append(score_100)
        if q.category in ["Role-specific"]:
            cat_evals["Role Fit"].append(score_100)
        # All answers reflect communication
        cat_evals["Communication"].append(score_100)

    category_scores: List[CategoryScore] = []
    descriptions = {
        "Technical Skills": "Mastery of core languages, frameworks, and data modeling",
        "Problem Solving": "Structured troubleshooting, trade-off analysis, and recovery",
        "Communication": "Clarity of technical explanations and proactive articulation",
        "Role Fit": "Alignment with target position responsibilities and scale",
        "System Architecture": "Designing distributed systems, caching, and resiliency"
    }

    for cat_name, scores in cat_evals.items():
        if scores:
            final_c_score = round(sum(scores) / len(scores), 1)
        else:
            final_c_score = round(avg_score, 1)
        category_scores.append(
            CategoryScore(
                category=cat_name,
                score=final_c_score,
                description=descriptions.get(cat_name, "Evaluation dimension")
            )
        )

    # Build question review items
    question_reviews: List[QuestionReviewItem] = []
    aggregated_strengths = []
    aggregated_weaknesses = []

    for idx, (q, ans, e) in enumerate(zip(questions, answers, evaluations)):
        question_reviews.append(
            QuestionReviewItem(
                question_index=idx + 1,
                question=q.question,
                topic=q.topic,
                category=q.category,
                candidate_answer=ans,
                score=round(e.score, 1),
                summary_indicator=e.summary_indicator,
                strengths=e.strengths,
                areas_to_improve=e.weaknesses
            )
        )
        aggregated_strengths.extend(e.strengths)
        aggregated_weaknesses.extend(e.weaknesses)

    # Deduplicate and pick top
    seen_s = set()
    strengths = []
    for s in aggregated_strengths:
        if s not in seen_s:
            seen_s.add(s)
            strengths.append(s)
        if len(strengths) >= 4:
            break

    seen_w = set()
    areas_to_improve = []
    for w in aggregated_weaknesses:
        if w not in seen_w:
            seen_w.add(w)
            areas_to_improve.append(w)
        if len(areas_to_improve) >= 4:
            break

    # Topics covered
    demonstrated_skills = list(set([q.topic for q in questions]))[:6]

    # Recommendations
    recommended_preparation = []
    if areas_to_improve:
        for idx, imp in enumerate(areas_to_improve[:3]):
            clean_imp = imp.lower().rstrip('.')
            recommended_preparation.append(f"Deepen preparation on {clean_imp} with production trade-offs and code examples.")
    else:
        recommended_preparation = [
            "Review high-concurrency database indexing and lock contention strategies.",
            "Practice structuring system design diagrams and back-of-the-envelope calculations.",
            "Prepare STAR-method examples highlighting quantifiable business and system impact."
        ]

    # Recommendations from weaknesses
    return FinalReport(
        session_id=session_id,
        overall_score=overall_score,
        category_performance=category_scores,
        demonstrated_skills=demonstrated_skills,
        strengths=strengths if strengths else ["Strong foundational knowledge", "Structured communication"],
        areas_to_improve=areas_to_improve if areas_to_improve else ["Add more metrics and trade-off depth"],
        question_reviews=question_reviews,
        recommended_preparation=recommended_preparation,
        interview_type=interview_type,
        total_questions=len(questions)
    )
