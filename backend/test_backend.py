import sys
import os
from app.services.parser import parse_document
from app.services.rag import VectorRAGIndex
from app.services.planner import generate_plan
from app.services.interviewer import InterviewerAgent
from app.services.evaluator import evaluate_answer
from app.services.report import generate_final_report
from app.services.demo_data import SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION

def run_tests():
    print("=== Testing Document Parsing ===")
    parsed = parse_document(SAMPLE_RESUME.encode('utf-8'), "resume.txt")
    assert len(parsed.text) > 100
    print(f"Parsed text length: {len(parsed.text)} chars")

    print("\n=== Testing RAG Index & Retrieval ===")
    rag = VectorRAGIndex()
    rag.build_index(SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION)
    assert len(rag.chunks) > 0
    print(f"Indexed {len(rag.chunks)} chunks across resume and JD")
    
    skills = rag.extract_key_skills()
    print(f"Matched skills: {skills['matched']}")
    print(f"Gaps identified: {skills['gaps']}")
    assert len(skills["matched"]) > 0

    retrieved = rag.query("PostgreSQL indexing performance", source_filter="resume", top_k=2)
    assert len(retrieved) > 0
    print(f"Top chunk snippet: {retrieved[0].text[:80]}... (Score: {retrieved[0].score:.3f})")

    print("\n=== Testing Planner Agent ===")
    insight = generate_plan(rag, SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION, "Mixed")
    print(f"Profile: {insight.candidate_profile}")
    print(f"Strong areas: {insight.strong_areas}")
    print(f"Areas to probe: {insight.areas_to_probe}")

    print("\n=== Testing Interviewer Agent & State ===")
    interviewer = InterviewerAgent(rag, total_questions=3, interview_type="Mixed", base_difficulty="Adaptive")
    q1 = interviewer.generate_next_question()
    print(f"Q1 ({q1.category}, {q1.difficulty}): {q1.question}")
    assert q1.question_index == 1

    print("\n=== Testing Evaluator & Dynamic Difficulty ===")
    eval1 = evaluate_answer(
        question_text=q1.question,
        topic=q1.topic,
        category=q1.category,
        candidate_answer="At DataFlow Systems, I analyzed slow analytical queries and noticed full table scans on multi-tenant audit logs. I introduced composite B-tree indexes on (tenant_id, created_at) and tuned PostgreSQL work_mem, reducing query execution times by 42% and eliminating lock contention during peak business hours.",
        question_index=1
    )
    print(f"Eval 1 Score: {eval1.score}/10 | Badge: {eval1.summary_indicator} | Adj: {eval1.difficulty_adjustment}")
    assert eval1.difficulty_adjustment in ["increase", "maintain"]

    q2 = interviewer.generate_next_question(last_eval=eval1)
    print(f"Q2 ({q2.category}, {q2.difficulty}): {q2.question}")
    assert q2.question_index == 2

    # Test weak response
    eval2 = evaluate_answer(
        question_text=q2.question,
        topic=q2.topic,
        category=q2.category,
        candidate_answer="I used it once.",
        question_index=2
    )
    print(f"Eval 2 Score: {eval2.score}/10 | Badge: {eval2.summary_indicator} | Adj: {eval2.difficulty_adjustment}")
    assert eval2.score < 6.0
    assert eval2.difficulty_adjustment == "decrease"

    print("\n=== Testing Final Report Generation ===")
    report = generate_final_report(
        session_id="test-session-123",
        questions=[q1, q2],
        answers=["Answer 1 with technical detail", "I used it once."],
        evaluations=[eval1, eval2],
        interview_type="Mixed"
    )
    print(f"Overall Score: {report.overall_score}/100")
    print(f"Categories: {[(c.category, c.score) for c in report.category_performance]}")
    print(f"Top recommendations: {report.recommended_preparation[:2]}")
    assert report.overall_score > 0
    print("\nAll Backend Agent & RAG tests passed successfully!")

if __name__ == "__main__":
    run_tests()
