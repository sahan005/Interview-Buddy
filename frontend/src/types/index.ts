export interface ParsedDocument {
  text: string;
  num_pages: number;
  sections: string[];
  file_type: string;
  filename: string;
}

export interface PreInterviewInsight {
  candidate_profile: string;
  strong_areas: string[];
  areas_to_probe: string[];
  role_focus: string[];
  raw_resume_snippet?: string;
  raw_jd_snippet?: string;
}

export interface RAGChunk {
  id: string;
  source: "resume" | "job_description";
  section?: string;
  page?: number;
  text: string;
  score: number;
}

export interface Question {
  question_index: number;
  question: string;
  category:
    | "Resume/project"
    | "Technical fundamentals"
    | "System design"
    | "Problem solving"
    | "Behavioral"
    | "Role-specific"
    | "Follow-up";
  topic: string;
  difficulty: "easy" | "medium" | "hard";
  reason: string;
  requires_resume_context: boolean;
  context_bullet?: string;
  retrieved_chunks: RAGChunk[];
}

export interface AnswerEvaluation {
  question_index: number;
  score: number;
  summary_indicator: string;
  strengths: string[];
  weaknesses: string[];
  missing_points: string[];
  suggested_followup?: string;
  difficulty_adjustment: "increase" | "maintain" | "decrease";
}

export interface CategoryScore {
  category: string;
  score: number;
  description: string;
}

export interface QuestionReviewItem {
  question_index: number;
  question: string;
  topic: string;
  category: string;
  candidate_answer: string;
  score: number;
  summary_indicator: string;
  strengths: string[];
  areas_to_improve: string[];
}

export interface FinalReport {
  session_id: string;
  overall_score: number;
  category_performance: CategoryScore[];
  demonstrated_skills: string[];
  strengths: string[];
  areas_to_improve: string[];
  question_reviews: QuestionReviewItem[];
  recommended_preparation: string[];
  interview_type: string;
  total_questions: number;
}

export interface SessionResponse {
  session_id: string;
  insight: PreInterviewInsight;
  first_question: Question;
  total_questions: number;
  current_difficulty: string;
  interview_type: string;
  topics_covered: string[];
  remaining_topics: string[];
}

export interface AnswerResponse {
  session_id: string;
  is_completed: boolean;
  evaluation_summary: string;
  last_evaluation: AnswerEvaluation;
  next_question?: Question;
  progress: {
    current_index: number;
    total: number;
    difficulty: string;
    topics_covered: string[];
  };
  final_report?: FinalReport;
}

export type ScreenState = 
  | "setup" 
  | "analyzing" 
  | "pre_insight" 
  | "interview" 
  | "evaluating_transition" 
  | "report";
