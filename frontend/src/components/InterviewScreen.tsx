import React, { useState, useEffect, useRef } from 'react';
import { ArrowRight } from 'lucide-react';
import type { Question, AnswerEvaluation } from '../types';

interface InterviewScreenProps {
  currentQuestion: Question;
  questionNumber: number;
  totalQuestions: number;
  currentDifficulty: string;
  topicsCovered: string[];
  lastEvaluation?: AnswerEvaluation | null;
  isEvaluating: boolean;
  onSubmitAnswer: (answer: string) => void;
  onEndEarly: () => void;
}

export const InterviewScreen: React.FC<InterviewScreenProps> = ({
  currentQuestion,
  questionNumber,
  totalQuestions,
  currentDifficulty,
  topicsCovered,
  lastEvaluation,
  isEvaluating,
  onSubmitAnswer,
  onEndEarly,
}) => {
  const [answer, setAnswer] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setAnswer('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [currentQuestion.question_index]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!answer.trim() || isEvaluating) return;
    onSubmitAnswer(answer);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const progressPercent = Math.round((questionNumber / totalQuestions) * 100);

  return (
    <div className="relative z-10 max-w-3xl mx-auto px-6 pt-10 sm:pt-14 pb-20">
      {/* Progress */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-xs font-mono text-zinc-600 mb-2">
          <span>{questionNumber} / {totalQuestions}</span>
          <span className="capitalize">{currentDifficulty}</span>
        </div>
        <div className="w-full h-[2px] bg-zinc-800/60 rounded-full overflow-hidden">
          <div
            className="h-full bg-zinc-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Previous evaluation indicator */}
      {lastEvaluation && (
        <div className="flex items-center gap-2 py-2 text-xs text-zinc-500">
          <span
            className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
              lastEvaluation.score >= 7 ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
          />
          <span>Previous: {lastEvaluation.summary_indicator}</span>
        </div>
      )}

      {/* Question */}
      <div className="mt-12 sm:mt-16">
        <span className="text-xs text-zinc-600 mb-3 block">
          {currentQuestion.topic}
        </span>

        <h2 className="text-xl sm:text-2xl font-medium text-zinc-100 leading-relaxed">
          {currentQuestion.question}
        </h2>

        {currentQuestion.context_bullet && (
          <p className="mt-3 text-sm text-zinc-500 italic">
            {currentQuestion.context_bullet}
          </p>
        )}
      </div>

      {/* Answer */}
      <form onSubmit={handleSubmit} className="mt-8">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isEvaluating}
            placeholder="Type your answer..."
            rows={6}
            className="w-full p-4 rounded-lg bg-zinc-900/40 border border-zinc-800/40 focus:border-zinc-700 focus:outline-none text-sm text-zinc-300 placeholder-zinc-600 resize-none leading-relaxed transition-colors disabled:opacity-40"
          />
          <span className="absolute right-3 bottom-3 text-[11px] font-mono text-zinc-700 hidden sm:block">
            Cmd + Enter
          </span>
        </div>

        <div className="flex items-center justify-between mt-3">
          <button
            type="button"
            onClick={onEndEarly}
            className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors"
          >
            End interview
          </button>

          <button
            type="submit"
            disabled={!answer.trim() || isEvaluating}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-white hover:bg-zinc-200 text-zinc-900 font-medium text-sm tracking-tight transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {isEvaluating ? (
              <>
                <span className="w-3 h-3 rounded-full border-2 border-zinc-900 border-t-transparent animate-spin" />
                Evaluating...
              </>
            ) : (
              <>
                Submit
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Covered topics */}
      {topicsCovered.length > 0 && (
        <p className="mt-12 text-xs text-zinc-600">
          Covered: {topicsCovered.join(', ')}
        </p>
      )}
    </div>
  );
};
