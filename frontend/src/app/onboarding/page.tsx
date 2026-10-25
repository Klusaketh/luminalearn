"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useOnReconnect } from "@/hooks/useOnReconnect";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "../../components/auth/ProtectedRoute";
import { useAuthStore } from "../../stores/useAuthStore";
import {
  onboardingService,
  DiagnosticQuestion,
  QuestionAnswer,
  PersonalizedRoadmap
} from "../../services/onboardingService";
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  BrainCircuit,
  Compass,
  BookOpen,
  Target,
  Clock,
  TrendingUp,
  Award,
  Zap,
  ShieldAlert,
  GraduationCap,
  Code,
  Calculator,
  Cpu,
  Database,
  Globe,
  HelpCircle
} from "lucide-react";

export default function OnboardingPage() {
  const router = useRouter();
  const { user, accessToken } = useAuthStore();

  // Wizard Navigation State (Steps 1 to 7)
  const [currentStep, setCurrentStep] = useState<number>(1);

  // User Onboarding Selections
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([]);

  // Diagnostic Quiz State
  const [questions, setQuestions] = useState<DiagnosticQuestion[]>([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState<number>(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const [questionTimeLogs, setQuestionTimeLogs] = useState<Record<number, number>>({});

  // Loading & Error States
  const [isLoadingQuestions, setIsLoadingQuestions] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Result Profile & Roadmap State
  const [roadmapResult, setRoadmapResult] = useState<PersonalizedRoadmap | null>(null);

  const fetchQuestions = useCallback(async () => {
    setIsLoadingQuestions(true);
    setErrorMessage(null);
    try {
      const qData = await onboardingService.getDiagnosticQuestions();
      setQuestions(qData);
      setQuestionStartTime(Date.now());
    } catch {
      setErrorMessage("Failed to load diagnostic questions. Please try again.");
    } finally {
      setIsLoadingQuestions(false);
    }
  }, []);

  // Fetch Diagnostic Questions when entering Step 5
  useEffect(() => {
    if (currentStep === 5 && questions.length === 0) {
      fetchQuestions();
    }
  }, [currentStep, questions.length, fetchQuestions]);

  // After a server outage, reload by itself if this page is showing a load error.
  useOnReconnect(() => {
    if (errorMessage) void fetchQuestions();
  });

  // Option Toggles
  const toggleGoal = (goal: string) => {
    setSelectedGoals((prev) =>
      prev.includes(goal) ? prev.filter((g) => g !== goal) : [...prev, goal]
    );
  };

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest) ? prev.filter((i) => i !== interest) : [...prev, interest]
    );
  };

  const toggleSubject = (subject: string) => {
    setSelectedSubjects((prev) =>
      prev.includes(subject) ? prev.filter((s) => s !== subject) : [...prev, subject]
    );
  };

  const handleSelectOption = (questionId: number, optionIdx: number) => {
    const elapsed = Date.now() - questionStartTime;
    setAnswers((prev) => ({ ...prev, [questionId]: optionIdx }));
    setQuestionTimeLogs((prev) => ({ ...prev, [questionId]: elapsed }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIdx < questions.length - 1) {
      setCurrentQuestionIdx((prev) => prev + 1);
      setQuestionStartTime(Date.now());
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIdx > 0) {
      setCurrentQuestionIdx((prev) => prev - 1);
      setQuestionStartTime(Date.now());
    }
  };

  const handleSubmitOnboarding = async () => {
    setIsSubmitting(true);
    setErrorMessage(null);

    const formattedAnswers: QuestionAnswer[] = Object.entries(answers).map(
      ([qidStr, optionIdx]) => ({
        question_id: Number(qidStr),
        selected_option_index: optionIdx,
        time_taken_ms: questionTimeLogs[Number(qidStr)] || 5000,
      })
    );

    try {
      await onboardingService.submitOnboarding(
        {
          goals: selectedGoals.length ? selectedGoals : ["General Skill Development"],
          interests: selectedInterests.length ? selectedInterests : ["Programming"],
          selected_subjects: selectedSubjects.length ? selectedSubjects : ["Computer Science"],
          answers: formattedAnswers,
        },
        accessToken || undefined
      );

      const roadmap: PersonalizedRoadmap = await onboardingService.getPersonalizedRoadmap(
        accessToken || undefined
      );

      setRoadmapResult(roadmap);
      setCurrentStep(6); // Transition to Profile & Roadmap summary
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process diagnostic assessment.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Goal & Interest Catalog Data
  const goalsCatalog = [
    { id: "Semester Preparation", label: "Semester Preparation", desc: "Master your college syllabus & ace exams", icon: BookOpen },
    { id: "Placement Preparation", label: "Placement Preparation", desc: "Crack coding interviews & technical rounds", icon: Target },
    { id: "GATE Exam", label: "GATE Exam", desc: "Structured prep for Computer Science GATE", icon: GraduationCap },
    { id: "UPSC & Competitive", label: "UPSC & Competitive", desc: "Aptitude, logic & analytical fundamentals", icon: Award },
    { id: "School Exams", label: "School Exams", desc: "STEM foundation & board exam prep", icon: Compass },
    { id: "Skill Development", label: "Skill Development", desc: "Learn modern AI, ML & Web Engineering", icon: Zap },
  ];

  const interestsCatalog = [
    { id: "Programming", label: "Programming", icon: Code },
    { id: "Mathematics", label: "Mathematics", icon: Calculator },
    { id: "AI & ML", label: "AI & Data Science", icon: Cpu },
    { id: "Web Engineering", label: "Web Engineering", icon: Globe },
    { id: "Databases", label: "Databases & SQL", icon: Database },
    { id: "Aptitude & Logic", label: "Aptitude & Logic", icon: HelpCircle },
  ];

  const subjectsCatalog = [
    "Data Structures & Algorithms",
    "Python & AI Foundations",
    "Linear Algebra & Calculus",
    "Database Systems & SQL",
    "Full-Stack Web Engineering",
    "Machine Learning & Data Science",
  ];

  return (
    <ProtectedRoute allowedRoles={["student", "admin"]}>
      <div className="flex-1 text-slate-100 flex flex-col justify-between px-4 py-8 relative overflow-hidden font-sans">
        {/* Ambient Glow Effects */}

        {/* Top Wizard Navigation Header */}
        <header className="max-w-4xl w-full mx-auto flex items-center justify-between z-10 mb-6">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-lg bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                LuminaLearn AI
              </span>
              <span className="text-xs text-indigo-400 font-mono block">Personalization Engine</span>
            </div>
          </div>

          {currentStep <= 5 && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400 font-mono">
                Step {currentStep} of 5
              </span>
              <div className="w-36 h-2 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${(currentStep / 5) * 100}%` }}
                />
              </div>
            </div>
          )}
        </header>

        {/* Main Content Card Container */}
        <main className="max-w-3xl w-full mx-auto bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-6 sm:p-10 shadow-2xl z-10 my-auto">
          {/* Error Alert */}
          {errorMessage && (
            <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 1: WELCOME SCREEN */}
          {/* ============================================================================== */}
          {currentStep === 1 && (
            <div className="text-center py-4 space-y-6">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-2">
                <Sparkles className="w-3.5 h-3.5" />
                Adaptive Cognitive Personalization
              </div>

              <h1 className="font-display leading-tight text-white text-4xl sm:text-5xl">
                Welcome to Your Personal AI Learning Journey, {user?.full_name || "Learner"}!
              </h1>

              <p className="text-slate-400 text-sm max-w-xl mx-auto leading-relaxed">
                LuminaLearn AI does not force you through standardized chapters. We continuously diagnose your unique cognitive pace, VARK modality preference, and knowledge gaps to build a 100% custom study trajectory.
              </p>

              {/* Value Proposition Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4 text-left">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <BrainCircuit className="w-6 h-6 text-indigo-400 mb-2" />
                  <h4 className="font-semibold text-sm text-slate-200">Diagnostic Assessment</h4>
                  <p className="text-xs text-slate-400 mt-1">Identify exact strong vs. weak micro-concepts in minutes.</p>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <TrendingUp className="w-6 h-6 text-purple-400 mb-2" />
                  <h4 className="font-semibold text-sm text-slate-200">Dynamic Study Pace</h4>
                  <p className="text-xs text-slate-400 mt-1">Recalibrates weekly targets based on your real performance.</p>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <Target className="w-6 h-6 text-emerald-400 mb-2" />
                  <h4 className="font-semibold text-sm text-slate-200">Tailored Roadmap</h4>
                  <p className="text-xs text-slate-400 mt-1">Custom daily targets focused strictly on your goals.</p>
                </div>
              </div>

              <div className="pt-6">
                <button
                  onClick={() => setCurrentStep(2)}
                  className="px-8 py-3.5 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition-all inline-flex items-center gap-2 group text-sm"
                >
                  Let&apos;s Get Started
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 2: LEARNING GOAL SELECTION */}
          {/* ============================================================================== */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <span className="text-xs text-indigo-400 font-mono font-semibold block mb-1">Step 2 of 5</span>
                <h2 className="text-2xl font-bold text-white">What is your primary learning goal?</h2>
                <p className="text-slate-400 text-xs mt-1">Select one or more goals to tailor your roadmap velocity.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {goalsCatalog.map((item) => {
                  const Icon = item.icon;
                  const isSelected = selectedGoals.includes(item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggleGoal(item.id)}
                      className={`p-4 rounded-xl border text-left transition-all flex items-start gap-3 ${
                        isSelected
                          ? "bg-indigo-600/20 border-indigo-500 text-white ring-1 ring-indigo-500"
                          : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                      }`}
                    >
                      <div className={`p-2 rounded-lg ${isSelected ? "bg-indigo-600 text-white" : "bg-slate-900 text-slate-400"}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-slate-200">{item.label}</h4>
                        <p className="text-xs text-slate-500 mt-0.5">{item.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-800/80">
                <button
                  onClick={() => setCurrentStep(1)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors inline-flex items-center gap-1.5"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>

                <button
                  onClick={() => setCurrentStep(3)}
                  disabled={selectedGoals.length === 0}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition-all inline-flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                >
                  Next Step <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 3: INTEREST SELECTION */}
          {/* ============================================================================== */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div>
                <span className="text-xs text-indigo-400 font-mono font-semibold block mb-1">Step 3 of 5</span>
                <h2 className="text-2xl font-bold text-white">What domains excite you most?</h2>
                <p className="text-slate-400 text-xs mt-1">Select domains to prioritize interactive practice problems.</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {interestsCatalog.map((item) => {
                  const Icon = item.icon;
                  const isSelected = selectedInterests.includes(item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggleInterest(item.id)}
                      className={`p-4 rounded-xl border text-center transition-all flex flex-col items-center justify-center gap-2 ${
                        isSelected
                          ? "bg-purple-600/20 border-purple-500 text-white ring-1 ring-purple-500"
                          : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                      }`}
                    >
                      <Icon className={`w-6 h-6 ${isSelected ? "text-purple-400" : "text-slate-500"}`} />
                      <span className="text-xs font-semibold text-slate-200">{item.label}</span>
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-800/80">
                <button
                  onClick={() => setCurrentStep(2)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors inline-flex items-center gap-1.5"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>

                <button
                  onClick={() => setCurrentStep(4)}
                  disabled={selectedInterests.length === 0}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition-all inline-flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                >
                  Next Step <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 4: SUBJECT SELECTION */}
          {/* ============================================================================== */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <div>
                <span className="text-xs text-indigo-400 font-mono font-semibold block mb-1">Step 4 of 5</span>
                <h2 className="text-2xl font-bold text-white">Choose subjects to learn first</h2>
                <p className="text-slate-400 text-xs mt-1">Select subjects you want featured in your first roadmap module.</p>
              </div>

              <div className="space-y-2">
                {subjectsCatalog.map((subj) => {
                  const isSelected = selectedSubjects.includes(subj);
                  return (
                    <button
                      key={subj}
                      type="button"
                      onClick={() => toggleSubject(subj)}
                      className={`w-full p-3.5 rounded-xl border text-left transition-all flex items-center justify-between ${
                        isSelected
                          ? "bg-indigo-600/20 border-indigo-500 text-white ring-1 ring-indigo-500"
                          : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                      }`}
                    >
                      <span className="text-sm font-semibold text-slate-200">{subj}</span>
                      <CheckCircle2 className={`w-4 h-4 ${isSelected ? "text-indigo-400" : "text-slate-700"}`} />
                    </button>
                  );
                })}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-800/80">
                <button
                  onClick={() => setCurrentStep(3)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors inline-flex items-center gap-1.5"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>

                <button
                  onClick={() => setCurrentStep(5)}
                  disabled={selectedSubjects.length === 0}
                  className="px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition-all inline-flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                >
                  Start Diagnostic Assessment <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 5: DIAGNOSTIC ASSESSMENT QUIZ */}
          {/* ============================================================================== */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-indigo-400 font-mono font-semibold">
                    Diagnostic Quiz • Question {currentQuestionIdx + 1} of {questions.length || 10}
                  </span>
                  {questions[currentQuestionIdx] && (
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      questions[currentQuestionIdx].difficulty === "Easy"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : questions[currentQuestionIdx].difficulty === "Medium"
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                    }`}>
                      {questions[currentQuestionIdx].difficulty}
                    </span>
                  )}
                </div>

                {/* Progress bar */}
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-2">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300"
                    style={{ width: `${((currentQuestionIdx + 1) / (questions.length || 10)) * 100}%` }}
                  />
                </div>
              </div>

              {isLoadingQuestions ? (
                <div className="py-12 text-center space-y-3">
                  <div className="w-8 h-8 border-3 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
                  <p className="text-xs text-slate-400 font-mono">Loading Diagnostic Assessment Items...</p>
                </div>
              ) : questions[currentQuestionIdx] ? (
                <div className="space-y-6">
                  {/* Topic Metadata Pill */}
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md font-mono">
                      {questions[currentQuestionIdx].subject}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-[11px] text-slate-400">
                      {questions[currentQuestionIdx].topic}
                    </span>
                  </div>

                  {/* Question Stem */}
                  <h3 className="text-lg font-semibold text-slate-100 leading-snug">
                    {questions[currentQuestionIdx].question}
                  </h3>

                  {/* Options */}
                  <div className="space-y-2.5">
                    {questions[currentQuestionIdx].options.map((optText, optIdx) => {
                      const qId = questions[currentQuestionIdx].id;
                      const isSelected = answers[qId] === optIdx;
                      return (
                        <button
                          key={optIdx}
                          type="button"
                          onClick={() => handleSelectOption(qId, optIdx)}
                          className={`w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between ${
                            isSelected
                              ? "bg-indigo-600/25 border-indigo-500 text-white ring-1 ring-indigo-500 shadow-md"
                              : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700"
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <span className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-mono font-bold ${
                              isSelected ? "bg-indigo-500 text-white" : "bg-slate-800 text-slate-400"
                            }`}>
                              {String.fromCharCode(65 + optIdx)}
                            </span>
                            <span className="text-sm">{optText}</span>
                          </div>
                          {isSelected && <CheckCircle2 className="w-4 h-4 text-indigo-400 shrink-0" />}
                        </button>
                      );
                    })}
                  </div>

                  {/* Inline Error Alert if submission fails */}
                  {errorMessage && (
                    <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 shrink-0" />
                        <span>
                          {errorMessage === "EMAIL_VERIFICATION_REQUIRED"
                            ? "Your account email is not yet verified. Please verify your email via the OTP sent to your inbox to submit this assessment."
                            : errorMessage}
                        </span>
                      </div>
                      {errorMessage === "EMAIL_VERIFICATION_REQUIRED" && (
                        <a
                          href="/verify-email"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1 rounded bg-rose-500/20 hover:bg-rose-500/30 text-white font-semibold shrink-0 transition-colors"
                        >
                          Verify Email
                        </a>
                      )}
                    </div>
                  )}

                  {/* Question Controls */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-800/80">
                    <button
                      onClick={handlePrevQuestion}
                      disabled={currentQuestionIdx === 0}
                      className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 disabled:opacity-30 transition-colors inline-flex items-center gap-1.5"
                    >
                      <ArrowLeft className="w-3.5 h-3.5" /> Previous Question
                    </button>

                    {currentQuestionIdx < questions.length - 1 ? (
                      <button
                        onClick={handleNextQuestion}
                        disabled={answers[questions[currentQuestionIdx].id] === undefined}
                        className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition-all inline-flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
                      >
                        Next Question <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button
                        onClick={handleSubmitOnboarding}
                        disabled={isSubmitting || Object.keys(answers).length < questions.length}
                        className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition-all inline-flex items-center gap-2 shadow-lg shadow-emerald-600/20"
                      >
                        {isSubmitting ? (
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                          <>
                            Submit Assessment <CheckCircle2 className="w-4 h-4" />
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          )}

          {/* ============================================================================== */}
          {/* STEP 6 & 7: LEARNER PROFILE & PERSONALIZED ROADMAP SUMMARY */}
          {/* ============================================================================== */}
          {currentStep === 6 && roadmapResult && (
            <div className="space-y-6 py-2">
              {/* Header Badge */}
              <div className="text-center space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Onboarding & Assessment Complete
                </div>
                <h2 className="text-3xl font-extrabold text-white">Your Personalized Learning Profile</h2>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Rule-based cognitive profile generated based on your 10-question diagnostic evaluation.
                </p>
              </div>

              {/* Top Profile Summary Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {/* Diagnostic Score Gauge */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center flex flex-col items-center justify-center">
                  <span className="text-[11px] text-slate-400 font-mono mb-1">Diagnostic Score</span>
                  <div className="text-3xl font-black text-indigo-400 font-mono">
                    {roadmapResult.profile.assessment_score}%
                  </div>
                  <span className="text-[11px] text-slate-500 mt-1">Accuracy Index</span>
                </div>

                {/* Recommended Study Pace */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center flex flex-col items-center justify-center">
                  <span className="text-[11px] text-slate-400 font-mono mb-1">Target Study Pace</span>
                  <div className="text-3xl font-black text-purple-400 font-mono flex items-baseline gap-1">
                    {roadmapResult.weekly_goal_hours} <span className="text-xs text-slate-400 font-sans font-normal">hrs/wk</span>
                  </div>
                  <span className="text-[11px] text-slate-500 mt-1">~{roadmapResult.daily_target_minutes} mins / day</span>
                </div>

                {/* Starting Course Focus */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center flex flex-col items-center justify-center">
                  <span className="text-[11px] text-slate-400 font-mono mb-1">Suggested Starting Focus</span>
                  <div className="text-xs font-bold text-emerald-400 line-clamp-2 px-1">
                    {roadmapResult.starting_module}
                  </div>
                  <span className="text-[11px] text-slate-500 mt-1">Initial Module</span>
                </div>
              </div>

              {/* Strengths & Weak Areas Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-emerald-500/20">
                  <h4 className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 mb-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Strengths Identified
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {roadmapResult.profile.strengths.map((str, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-xs font-medium">
                        {str}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/60 border border-amber-500/20">
                  <h4 className="text-xs font-bold text-amber-400 flex items-center gap-1.5 mb-2">
                    <Target className="w-3.5 h-3.5" /> Priority Remediation Focus
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {roadmapResult.profile.weak_areas.map((weak, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/20 text-xs font-medium">
                        {weak}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Roadmap Timeline Modules */}
              <div className="pt-2">
                <h3 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-indigo-400" />
                  Your Custom Roadmap: {roadmapResult.recommended_course}
                </h3>

                <div className="space-y-3">
                  {roadmapResult.roadmap_modules.map((mod) => (
                    <div
                      key={mod.id}
                      className={`p-4 rounded-xl border flex items-start justify-between ${
                        mod.is_key_focus
                          ? "bg-indigo-600/15 border-indigo-500/60"
                          : "bg-slate-950/60 border-slate-800"
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-white">{mod.title}</h4>
                          {mod.is_key_focus && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500 text-white">
                              Starting Focus
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-400 mt-1">{mod.description}</p>
                      </div>

                      <span className="text-xs text-slate-400 font-mono shrink-0 ml-3">
                        {mod.estimated_hours} hrs
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Finish CTA */}
              <div className="pt-4 text-center">
                <button
                  onClick={() => router.push("/dashboard")}
                  className="px-8 py-3.5 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/30 transition-all inline-flex items-center gap-2 text-sm group"
                >
                  Go to Student Dashboard
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          )}
        </main>

        {/* Footer info */}
        <footer className="max-w-4xl w-full mx-auto text-center z-10 text-xs text-slate-500 py-4">
          LuminaLearn AI • Enterprise Monorepo Personalization Foundation
        </footer>
      </div>
    </ProtectedRoute>
  );
}
