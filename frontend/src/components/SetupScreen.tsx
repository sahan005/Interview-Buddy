import React, { useState, useRef } from 'react';
import { Upload, FileText, X, ArrowRight, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { apiClient } from '../api/client';
import type { ParsedDocument } from '../types';

interface SetupScreenProps {
  onStart: (params: {
    resume_text: string;
    job_description: string;
    interview_type: string;
    difficulty: string;
    num_questions: number;
    resume_meta?: ParsedDocument;
  }) => void;
  isLoading: boolean;
}

export const SetupScreen: React.FC<SetupScreenProps> = ({ onStart, isLoading }) => {
  const [resumeText, setResumeText] = useState('');
  const [resumeMeta, setResumeMeta] = useState<ParsedDocument | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [interviewType, setInterviewType] = useState('Mixed');
  const [difficulty, setDifficulty] = useState('Adaptive');
  const [numQuestions, setNumQuestions] = useState(8);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setErrorMessage(null);
    setIsUploading(true);
    try {
      const parsed = await apiClient.uploadResume(file);
      setResumeText(parsed.text);
      setResumeMeta(parsed);
    } catch (err: any) {
      setErrorMessage(err.message || 'Unable to read this file. Try another PDF or DOCX.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleLoadDemoData = async () => {
    setErrorMessage(null);
    try {
      const data = await apiClient.getDemoData();
      setResumeText(data.sample_resume);
      setResumeMeta({
        text: data.sample_resume,
        num_pages: 1,
        sections: ['Experience', 'Skills', 'Education'],
        file_type: 'txt',
        filename: 'alex_rivera_backend_resume.pdf'
      });
      setJobDescription(data.sample_job_description);
    } catch (err: any) {
      setErrorMessage('Failed to load sample data.');
    }
  };

  const handleRemoveResume = () => {
    setResumeText('');
    setResumeMeta(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    if (!resumeText.trim()) {
      setErrorMessage('Upload a resume to continue.');
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage('Add the job description before starting.');
      return;
    }
    onStart({
      resume_text: resumeText,
      job_description: jobDescription,
      interview_type: interviewType,
      difficulty: difficulty,
      num_questions: numQuestions,
      resume_meta: resumeMeta || undefined
    });
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
      {/* Hero Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-zinc-100">
          Practice interviews built around your experience
        </h1>
        <p className="mt-3 text-sm sm:text-base text-zinc-400 leading-relaxed">
          Ground questions in verified resume accomplishments and target role specifications.
          Zero generic prompts. Completely adaptive.
        </p>
        <div className="mt-4 flex justify-center">
          <button
            type="button"
            onClick={handleLoadDemoData}
            className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded bg-zinc-800/80 hover:bg-zinc-800 text-zinc-300 hover:text-zinc-100 border border-zinc-700/60 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5 text-zinc-400" />
            <span>Load Sample Data (Backend Role)</span>
          </button>
        </div>
      </div>

      {/* Error alert */}
      {errorMessage && (
        <div className="max-w-4xl mx-auto mb-6 p-3 rounded bg-red-950/40 border border-red-800/50 flex items-center gap-2.5 text-xs text-red-300">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Form Container */}
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Column: Resume Upload */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-zinc-400">
                Resume (PDF, DOCX)
              </label>
              {resumeMeta && (
                <span className="text-[11px] font-mono text-zinc-500">
                  {resumeMeta.text.length} chars
                </span>
              )}
            </div>

            {!resumeText ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="min-h-[220px] flex-1 border border-dashed border-zinc-800 hover:border-zinc-700 bg-zinc-900/30 hover:bg-zinc-900/60 rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-colors text-center"
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                />
                <div className="w-9 h-9 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-400 mb-3">
                  <Upload className="w-4 h-4" />
                </div>
                <span className="text-xs font-medium text-zinc-200">
                  {isUploading ? 'Extracting document text...' : 'Click to select or drag and drop resume'}
                </span>
                <span className="text-[11px] text-zinc-500 mt-1">PDF or DOCX supported up to 10MB</span>
              </div>
            ) : (
              <div className="min-h-[220px] flex-1 border border-zinc-800 bg-zinc-900/50 rounded-lg p-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-300">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-xs font-medium text-zinc-200 truncate max-w-[200px]">
                          {resumeMeta?.filename || 'Uploaded Resume'}
                        </p>
                        <p className="text-[11px] text-zinc-500">
                          {resumeMeta?.file_type?.toUpperCase()} document parsed
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={handleRemoveResume}
                      className="text-zinc-500 hover:text-zinc-300 p-1 rounded hover:bg-zinc-800 transition-colors"
                      title="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="mt-3 py-2 px-2.5 rounded bg-zinc-950/70 border border-zinc-800 text-[11px] text-zinc-400 max-h-24 overflow-y-auto leading-relaxed">
                    {resumeText.slice(0, 320)}...
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-zinc-800/60 flex items-center gap-1.5 text-[11px] text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Document parsed and ready for interview generation</span>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Job Description */}
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-medium text-zinc-400">
                Job Description
              </label>
              <span className="text-[11px] font-mono text-zinc-500">
                {jobDescription.length} chars
              </span>
            </div>

            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the target role description, responsibilities, and required qualifications here..."
              rows={8}
              className="flex-1 w-full min-h-[220px] p-3.5 rounded-lg bg-zinc-900/30 border border-zinc-800 hover:border-zinc-700 focus:border-zinc-500 focus:outline-none text-xs text-zinc-200 placeholder-zinc-600 resize-none font-sans leading-relaxed transition-colors"
            />
          </div>
        </div>

        {/* Configuration Row */}
        <div className="pt-5 border-t border-zinc-800/80">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div>
              <span className="block text-xs font-medium text-zinc-400 mb-1.5">Interview Format</span>
              <div className="grid grid-cols-3 gap-1 p-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs">
                {['Technical', 'Mixed', 'Behavioral'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setInterviewType(type)}
                    className={`py-1 rounded text-center transition-colors ${
                      interviewType === type
                        ? 'bg-zinc-800 text-zinc-100 font-medium'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <span className="block text-xs font-medium text-zinc-400 mb-1.5">Difficulty</span>
              <div className="grid grid-cols-4 gap-1 p-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs">
                {['Adaptive', 'Easy', 'Medium', 'Hard'].map((diff) => (
                  <button
                    key={diff}
                    type="button"
                    onClick={() => setDifficulty(diff)}
                    className={`py-1 rounded text-center transition-colors ${
                      difficulty === diff
                        ? 'bg-zinc-800 text-zinc-100 font-medium'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <span className="block text-xs font-medium text-zinc-400 mb-1.5">Question Count</span>
              <div className="grid grid-cols-3 gap-1 p-1 rounded-md bg-zinc-900 border border-zinc-800 text-xs">
                {[5, 8, 10].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setNumQuestions(num)}
                    className={`py-1 rounded text-center transition-colors ${
                      numQuestions === num
                        ? 'bg-zinc-800 text-zinc-100 font-medium'
                        : 'text-zinc-400 hover:text-zinc-200'
                    }`}
                  >
                    {num} Qs
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-2 flex justify-center">
          <button
            type="submit"
            disabled={isLoading || isUploading}
            className="inline-flex items-center gap-2 px-7 py-3 rounded-md bg-zinc-100 hover:bg-white text-zinc-900 font-medium text-xs tracking-tight transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
          >
            <span>Start Interview</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
};
