import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { SetupScreen } from './components/SetupScreen';
import { AnalysisScreen } from './components/AnalysisScreen';
import { PreInterviewInsight } from './components/PreInterviewInsight';
import { InterviewScreen } from './components/InterviewScreen';
import { ReportScreen } from './components/ReportScreen';
import { apiClient } from './api/client';
import type {
  ScreenState,
  SessionResponse,
  Question,
  AnswerEvaluation,
  FinalReport,
  ParsedDocument
} from './types';

export function App() {
  const [screen, setScreen] = useState<ScreenState>('setup');
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [currentDifficulty, setCurrentDifficulty] = useState('medium');
  const [topicsCovered, setTopicsCovered] = useState<string[]>([]);
  const [lastEvaluation, setLastEvaluation] = useState<AnswerEvaluation | null>(null);
  const [finalReport, setFinalReport] = useState<FinalReport | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>('Ready');

  // ALL HANDLERS STAY EXACTLY THE SAME
  const handleStartSetup = async (params: {
    resume_text: string;
    job_description: string;
    interview_type: string;
    difficulty: string;
    num_questions: number;
    resume_meta?: ParsedDocument;
  }) => {
    setScreen('analyzing');
    setStatusMessage('Analyzing...');
    try {
      const sess = await apiClient.startInterview({
        resume_text: params.resume_text,
        job_description: params.job_description,
        interview_type: params.interview_type,
        difficulty: params.difficulty,
        num_questions: params.num_questions,
      });
      setSession(sess);
      setCurrentQuestion(sess.first_question);
      setCurrentDifficulty(sess.current_difficulty);
      setTopicsCovered(sess.topics_covered);
      setQuestionNumber(1);
      setLastEvaluation(null);
      setFinalReport(null);
    } catch (err: any) {
      alert(err.message || 'Failed to start interview.');
      setScreen('setup');
      setStatusMessage('Ready');
    }
  };

  const handleAnalysisComplete = () => {
    setScreen('pre_insight');
    setStatusMessage('Ready');
  };

  const handleBeginInterview = () => {
    setScreen('interview');
    setStatusMessage('In progress');
  };

  const handleSubmitAnswer = async (answer: string) => {
    if (!session || !currentQuestion) return;
    setIsEvaluating(true);
    setStatusMessage('Evaluating...');
    try {
      const res = await apiClient.submitAnswer({
        session_id: session.session_id,
        question_index: questionNumber,
        answer,
      });
      setLastEvaluation(res.last_evaluation);
      setCurrentDifficulty(res.progress.difficulty);
      setTopicsCovered(res.progress.topics_covered);
      if (res.is_completed && res.final_report) {
        setFinalReport(res.final_report);
        setScreen('report');
        setStatusMessage('Complete');
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
        setQuestionNumber((prev) => prev + 1);
        setStatusMessage('In progress');
      }
    } catch (err: any) {
      alert(err.message || 'Failed to evaluate. Please retry.');
      setStatusMessage('Retry');
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleEndEarly = async () => {
    if (!session) return;
    if (!window.confirm('End the interview and view your report?')) return;
    try {
      const report = await apiClient.endInterviewEarly(session.session_id);
      setFinalReport(report);
      setScreen('report');
      setStatusMessage('Complete');
    } catch (err: any) {
      alert(err.message || 'Unable to generate report.');
    }
  };

  const handleReset = () => {
    setScreen('setup');
    setSession(null);
    setCurrentQuestion(null);
    setQuestionNumber(1);
    setLastEvaluation(null);
    setFinalReport(null);
    setStatusMessage('Ready');
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100">
      <Navbar
        onReset={handleReset}
        statusText={statusMessage}
        hasActiveSession={screen !== 'setup'}
      />

      <main>
        {screen === 'setup' && (
          <SetupScreen onStart={handleStartSetup} isLoading={false} />
        )}
        {screen === 'analyzing' && (
          <AnalysisScreen onComplete={handleAnalysisComplete} />
        )}
        {screen === 'pre_insight' && session && (
          <PreInterviewInsight
            insight={session.insight}
            interviewType={session.interview_type}
            difficulty={session.current_difficulty}
            totalQuestions={session.total_questions}
            onBegin={handleBeginInterview}
          />
        )}
        {screen === 'interview' && currentQuestion && session && (
          <InterviewScreen
            currentQuestion={currentQuestion}
            questionNumber={questionNumber}
            totalQuestions={session.total_questions}
            currentDifficulty={currentDifficulty}
            topicsCovered={topicsCovered}
            lastEvaluation={lastEvaluation}
            isEvaluating={isEvaluating}
            onSubmitAnswer={handleSubmitAnswer}
            onEndEarly={handleEndEarly}
          />
        )}
        {screen === 'report' && finalReport && (
          <ReportScreen report={finalReport} onRetake={handleReset} />
        )}
      </main>
    </div>
  );
}

export default App;
