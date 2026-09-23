import React, { useState } from 'react';
import { ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';
import type { FinalReport } from '../types';

interface ReportScreenProps {
  report: FinalReport;
  onRetake: () => void;
}

export const ReportScreen: React.FC<ReportScreenProps> = ({ report, onRetake }) => {
  const [expandedQuestions, setExpandedQuestions] = useState<Record<number, boolean>>({ 1: true });

  const toggleQuestion = (idx: number) => {
    setExpandedQuestions((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="relative z-10 max-w-3xl mx-auto px-6 pt-16 sm:pt-24 pb-24 space-y-16">
      {/* Header & Score */}
      <div className="text-center">
        <span className="text-[11px] text-zinc-600 tracking-[0.2em] uppercase">
          Interview complete
        </span>

        <div className="mt-8">
          <span className="text-6xl sm:text-7xl font-bold font-mono text-zinc-100 tracking-tight">
            {report.overall_score}
          </span>
          <p className="text-sm text-zinc-600 mt-2">out of 100</p>
        </div>

        <p className="mt-4 text-xs text-zinc-500 max-w-md mx-auto">
          Evaluated across {report.total_questions} adaptive questions.
          Scores reflect technical depth, specificity, and role alignment.
        </p>
      </div>

      {/* Category Performance */}
      <div className="space-y-5">
        <h2 className="text-xs text-zinc-600 tracking-wider uppercase">
          Category breakdown
        </h2>

        <div className="space-y-4">
          {report.category_performance.map((cat, idx) => (
            <div key={idx}>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-zinc-400">{cat.category}</span>
                <span className="font-mono text-zinc-300">{cat.score.toFixed(0)}</span>
              </div>
              <div className="w-full h-[3px] bg-zinc-800/50 rounded-full overflow-hidden">
                <div
                  className="h-full bg-zinc-400 rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Math.max(0, cat.score))}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Areas to improve */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        <div>
          <h3 className="text-sm font-medium text-zinc-300 mb-4">Strengths</h3>
          <ul className="space-y-2.5">
            {report.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm text-zinc-400 leading-relaxed">
                <span className="w-1 h-1 rounded-full bg-emerald-500 mt-2 flex-shrink-0" />
                {str}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-medium text-zinc-300 mb-4">Areas to improve</h3>
          <ul className="space-y-2.5">
            {report.areas_to_improve.map((imp, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-sm text-zinc-400 leading-relaxed">
                <span className="w-1 h-1 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                {imp}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Question Review */}
      <div className="space-y-3">
        <h2 className="text-xs text-zinc-600 tracking-wider uppercase mb-4">
          Question review
        </h2>

        {report.question_reviews.map((rev) => {
          const isExpanded = !!expandedQuestions[rev.question_index];

          return (
            <div key={rev.question_index}>
              <button
                type="button"
                onClick={() => toggleQuestion(rev.question_index)}
                className="w-full flex items-center justify-between py-3 text-left group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs font-mono text-zinc-600 flex-shrink-0 w-6">
                    {rev.question_index}.
                  </span>
                  <span className="text-sm text-zinc-400 truncate group-hover:text-zinc-300 transition-colors">
                    {rev.question}
                  </span>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                  <span className="text-xs font-mono text-zinc-500">
                    {rev.score.toFixed(1)}
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-3.5 h-3.5 text-zinc-600" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-zinc-600" />
                  )}
                </div>
              </button>

              {isExpanded && (
                <div className="pl-9 pb-5 space-y-4 text-sm">
                  <p className="text-zinc-500 italic leading-relaxed">
                    &ldquo;{rev.candidate_answer}&rdquo;
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    {rev.strengths.length > 0 && (
                      <div>
                        <span className="text-zinc-500 block mb-1.5">Strengths</span>
                        <ul className="space-y-1 text-zinc-400">
                          {rev.strengths.map((s, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="w-1 h-1 rounded-full bg-emerald-500/70 mt-1.5 flex-shrink-0" />
                              {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {rev.areas_to_improve.length > 0 && (
                      <div>
                        <span className="text-zinc-500 block mb-1.5">To deepen</span>
                        <ul className="space-y-1 text-zinc-400">
                          {rev.areas_to_improve.map((w, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="w-1 h-1 rounded-full bg-amber-500/70 mt-1.5 flex-shrink-0" />
                              {w}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="border-b border-zinc-800/30" />
            </div>
          );
        })}
      </div>

      {/* Recommendations */}
      <div>
        <h2 className="text-xs text-zinc-600 tracking-wider uppercase mb-4">
          Recommended preparation
        </h2>
        <ol className="space-y-2.5">
          {report.recommended_preparation.map((rec, idx) => (
            <li key={idx} className="flex items-start gap-3 text-sm text-zinc-400 leading-relaxed">
              <span className="text-xs font-mono text-zinc-600 mt-0.5 flex-shrink-0">
                {idx + 1}.
              </span>
              {rec}
            </li>
          ))}
        </ol>
      </div>

      {/* Retake */}
      <div className="flex justify-center pt-4">
        <button
          type="button"
          onClick={onRetake}
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg border border-zinc-700 text-zinc-300 hover:bg-zinc-800/50 text-sm transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Retake interview
        </button>
      </div>
    </div>
  );
};
