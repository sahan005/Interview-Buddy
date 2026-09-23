import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_flow():
    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    print("Health check:", data)
    assert data["status"] == "healthy"

    # 2. Fetch demo data
    res = client.get("/api/demo-data")
    assert res.status_code == 200
    demo = res.json()
    assert len(demo["sample_resume"]) > 50
    assert len(demo["sample_job_description"]) > 50
    print("Fetched demo data successfully for:", demo["candidate_name"])

    # 3. Start interview with 3 questions
    start_payload = {
        "resume_text": demo["sample_resume"],
        "job_description": demo["sample_job_description"],
        "interview_type": "Mixed",
        "difficulty": "Adaptive",
        "num_questions": 3
    }
    res = client.post("/api/interview/start", json=start_payload)
    assert res.status_code == 200
    session_data = res.json()
    session_id = session_data["session_id"]
    print("Session created:", session_id)
    print("Candidate Profile:", session_data["insight"]["candidate_profile"])
    print("Strong Areas:", session_data["insight"]["strong_areas"])
    print("Q1:", session_data["first_question"]["question"])
    assert session_data["first_question"]["question_index"] == 1

    # 4. Answer Q1 (strong technical answer)
    ans1_payload = {
        "session_id": session_id,
        "question_index": 1,
        "answer": "At DataFlow Systems, I engineered an event ingestion pipeline using FastAPI, Redis Pub/Sub, and PostgreSQL. We handled 12 million events per day. To prevent table bloat and query contention, we added composite indexes on (tenant_id, created_at) and implemented partitioned tables, cutting query response times by 42%."
    }
    res = client.post("/api/interview/answer", json=ans1_payload)
    assert res.status_code == 200
    ans1_resp = res.json()
    print("Q1 Evaluation Score:", ans1_resp["last_evaluation"]["score"])
    print("Q1 Evaluation Badge:", ans1_resp["evaluation_summary"])
    assert ans1_resp["is_completed"] is False
    assert ans1_resp["next_question"] is not None
    print("Q2:", ans1_resp["next_question"]["question"])

    # 5. Answer Q2 (concise answer)
    ans2_payload = {
        "session_id": session_id,
        "question_index": 2,
        "answer": "We monitored latency using Prometheus and set up alerting thresholds in Grafana for 5xx errors and CPU saturation."
    }
    res = client.post("/api/interview/answer", json=ans2_payload)
    assert res.status_code == 200
    ans2_resp = res.json()
    print("Q2 Evaluation Score:", ans2_resp["last_evaluation"]["score"])
    assert ans2_resp["is_completed"] is False
    assert ans2_resp["next_question"] is not None
    print("Q3:", ans2_resp["next_question"]["question"])

    # 6. Answer Q3 (final question)
    ans3_payload = {
        "session_id": session_id,
        "question_index": 3,
        "answer": "In our team we established clear RFC technical review guidelines to debate architectural decisions objectively, prioritizing simplicity and customer latency over premature optimizations."
    }
    res = client.post("/api/interview/answer", json=ans3_payload)
    assert res.status_code == 200
    ans3_resp = res.json()
    assert ans3_resp["is_completed"] is True
    assert ans3_resp["final_report"] is not None
    report = ans3_resp["final_report"]
    print("\n--- Final Assessment Report ---")
    print(f"Overall Calculated Score: {report['overall_score']}/100")
    for cat in report["category_performance"]:
        print(f" - {cat['category']}: {cat['score']}/100")
    print("Demonstrated Skills:", report["demonstrated_skills"])
    print("Strengths:", report["strengths"])
    print("Recommendations:", report["recommended_preparation"])

    print("\nEnd-to-End API Test completed successfully!")

if __name__ == "__main__":
    test_full_flow()
