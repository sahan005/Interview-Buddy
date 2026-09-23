import React from 'react';
import { ArrowRight } from 'lucide-react';
import type { PreInterviewInsight as PreInsightType } from '../types';

interface PreInterviewInsightProps {
  insight: PreInsightType;
  interviewType: string;
  difficulty: string;
  totalQuestions: number;
  onBegin: () => void;
}

export const PreInterviewInsight: React.FC<PreInterviewInsightProps> = ({
  insight,
  interviewType,
  difficulty,
  totalQuestions,
  onBegin,
}) => {
  return (
    <div className="relative z-10 max-w-3xl mx-auto px-6 pt-16 sm:pt-24 pb-20">
      <div className="text-center mb-12">
        <span className="text-[11px] text-zinc-600 tracking-[0.2em] uppercase">
          Interview briefing
        </span>
        <p className="mt-6 text-xl sm:text-2xl font-medium text-zinc-200 leading-relaxed max-w-2xl mx-auto">
          &ldquo;{insight.candidate_profile}&rdquo;
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-14">
        {/* Strong areas */}
        <div>
          <h3 className="text-xs text-zinc-500 tracking-wider uppercase mb-4">
            Strong areas
          </h3>
          <ul className="space-y-2.5">
            {insight.strong_areas.map((area, idx) => (
              <li key={idx} className="flex items-center gap-2.5 text-sm text-zinc-400">
                <span className="w-1 h-1 rounded-full bg-emerald-500 flex-shrink-0" />
                {area}
              </li>
            ))}
          </ul>
        </div>

        {/* Areas to probe */}
        <div>
          <h3 className="text-xs text-zinc-500 tracking-wider uppercase mb-4">
            Areas to probe
          </h3>
          <ul className="space-y-2.5">
            {insight.areas_to_probe.map((area, idx) => (
              <li key={idx} className="flex items-center gap-2.5 text-sm text-zinc-400">
                <span className="w-1 h-1 rounded-full bg-amber-500 flex-shrink-0" />
                {area}
              </li>
            ))}
          </ul>
        </div>

        {/* Role focus */}
        <div>
          <h3 className="text-xs text-zinc-500 tracking-wider uppercase mb-4">
            Role focus
          </h3>
          <ul className="space-y-2.5">
            {insight.role_focus.map((focus, idx) => (
              <li key={idx} className="flex items-center gap-2.5 text-sm text-zinc-400">
                <span className="w-1 h-1 rounded-full bg-zinc-500 flex-shrink-0" />
                {focus}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="text-center">
        <p className="text-xs text-zinc-600 mb-6">
          {interviewType} / {difficulty} / {totalQuestions} questions
        </p>

        <button
          type="button"
          onClick={onBegin}
          className="inline-flex items-center gap-2.5 px-8 py-3 rounded-lg bg-white hover:bg-zinc-200 text-zinc-900 font-medium text-sm tracking-tight transition-all"
        >
          Begin Interview
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
