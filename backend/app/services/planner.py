from typing import Dict, Any, List
from ..schemas import PreInterviewInsight
from .rag import VectorRAGIndex
from .llm import llm_service

def generate_plan(
    rag: VectorRAGIndex,
    resume_text: str,
    jd_text: str,
    interview_type: str = "Mixed"
) -> PreInterviewInsight:
    """
    Component 1: Interview Planner
    Uses Gemini LLM directly with RAG context to understand the candidate's actual resume
    and target role—handling any role (Data Analyst, Product Manager, AI Engineer, Nurse, etc.)
    without hardcoded if/else rules.
    """
    # 1. Top chunks retrieved from ChromaDB vector index
    resume_chunks = rag.query("experience projects background skills education", source_filter="resume", top_k=8)
    jd_chunks = rag.query("role job description responsibilities requirements qualifications", source_filter="job_description", top_k=4)

    resume_context = "\n---\n".join([c.text for c in resume_chunks]) if resume_chunks else resume_text[:3000]
    jd_context = "\n---\n".join([c.text for c in jd_chunks]) if jd_chunks else jd_text[:3000]

    # 2. Pure AI Analysis using Gemini
    if llm_service.is_available():
        prompt = f"""
You are an expert hiring director. Analyze this candidate's resume against the target Job Description.
Read both carefully. Do NOT assume any specific role beforehand. Do NOT hallucinate.

Candidate Resume Context:
{resume_context[:1500]}

Target Job Description Context:
{jd_context[:1500]}

Generate a concise, professional assessment tailored specifically to whatever this role and candidate are.

Return ONLY a JSON object with this exact schema:
{{
  "candidate_profile": "Concise 1-sentence synthesis of candidate background and alignment with target role (e.g. 'Data Analyst with 3+ years experience in SQL and dashboard reporting targeting Data Analyst position')",
  "strong_areas": ["3 to 4 confirmed skills or domains directly present in the resume"],
  "areas_to_probe": ["3 to 4 target job requirements or potential gap areas to assess"],
  "role_focus": ["3 primary themes emphasized by the target Job Description"]
}}
"""
        res = llm_service.generate_json(
            prompt,
            system_instruction="You are an expert interviewer. Analyze resumes and job descriptions objectively using provided text."
        )
        if res and res.get("candidate_profile"):
            return PreInterviewInsight(
                candidate_profile=res.get("candidate_profile"),
                strong_areas=res.get("strong_areas", []),
                areas_to_probe=res.get("areas_to_probe", []),
                role_focus=res.get("role_focus", []),
                raw_resume_snippet=resume_context[:400],
                raw_jd_snippet=jd_context[:400]
            )

    # 3. Dynamic textual extraction only if LLM is completely offline
    first_res_line = [l.strip() for l in resume_text.split('\n') if l.strip()][:2]
    first_jd_line = [l.strip() for l in jd_text.split('\n') if l.strip()][:2]
    
    return PreInterviewInsight(
        candidate_profile=f"Candidate with background in {' / '.join(first_res_line)} targeting {' / '.join(first_jd_line)}",
        strong_areas=["Experience directly highlighted in resume", "Core domain expertise"],
        areas_to_probe=["Role requirements", "Methodology & tools"],
        role_focus=["Core responsibilities", "Key deliverables"],
        raw_resume_snippet=resume_context[:400],
        raw_jd_snippet=jd_context[:400]
    )
