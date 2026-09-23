import React from 'react';
import { RotateCcw } from 'lucide-react';

interface NavbarProps {
  onReset: () => void;
  statusText?: string;
  hasActiveSession?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onReset, hasActiveSession }) => {
  return (
    <header className="border-b border-zinc-800/80 bg-[#09090b]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 h-13 flex items-center justify-between">
        <button
          onClick={onReset}
          className="text-sm font-semibold tracking-tight text-zinc-100 hover:text-white transition-colors"
        >
          Interview Agent
        </button>

        {hasActiveSession && (
          <button
            onClick={onReset}
            className="inline-flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition-colors px-2.5 py-1 rounded hover:bg-zinc-800"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>New interview</span>
          </button>
        )}
      </div>
    </header>
  );
};
