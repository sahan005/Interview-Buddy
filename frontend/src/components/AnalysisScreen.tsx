import React, { useEffect, useState } from 'react';

interface AnalysisScreenProps {
  onComplete: () => void;
}

const STEPS = [
  'Reading resume...',
  'Mapping role requirements...',
  'Matching experience to role...',
  'Building interview strategy...',
];

export const AnalysisScreen: React.FC<AnalysisScreenProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(onComplete, 400);
          return prev;
        }
      });
    }, 800);

    return () => clearInterval(interval);
  }, [onComplete]);

  const progress = ((currentStep + 1) / STEPS.length) * 100;

  return (
    <div className="relative z-10 flex flex-col items-center justify-center min-h-[70vh] px-6">
      <span className="text-[11px] text-zinc-600 tracking-[0.2em] uppercase mb-8">
        Analyzing
      </span>

      <div className="w-48 h-[2px] bg-zinc-800/60 rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-zinc-400 rounded-full transition-all duration-700 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p
        key={currentStep}
        className="text-sm text-zinc-500 animate-fade-in"
      >
        {STEPS[currentStep]}
      </p>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 300ms ease-out;
        }
      `}</style>
    </div>
  );
};
