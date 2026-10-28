"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, Award, Calculator, CheckCircle2, Layers, Loader2, MessagesSquare, RotateCcw, Sigma, TrendingUp, XCircle } from "lucide-react";
import { MathRenderer } from "@/components/common/MathRenderer";
import { MarkdownMessage } from "@/components/tutor/MarkdownMessage";
import { MasteryGauge } from "@/components/quiz/MasteryGauge";
import { MisconceptionCallout } from "@/components/quiz/MisconceptionCallout";
import { RetentionForecast } from "@/components/quiz/RetentionForecast";
import { KnowledgeRadar } from "@/components/quiz/KnowledgeRadar";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { MagneticButton } from "@/components/ui/MagneticButton";
import { SegmentedControl } from "@/components/ui/SegmentedControl";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { celebrateMastery } from "@/utils/confetti";
import { cn } from "@/utils/cn";
import {
  quizService,
  type QuizMasteryResponse,
  type QuizSessionDetail,
  type QuizSubmitAnswerResponse,
  type TopicMasterySummary,
} from "@/services/quizService";

const PRESET_DOMAINS = [
  { title: "Calculus", description: "Definite integrals, derivatives, limits and series", icon: Calculator, accent: "from-indigo-500/30 to-indigo-500/0" },
  { title: "Linear Algebra", description: "Eigenvalues, rank, orthogonality and spans", icon: Sigma, accent: "from-cyan-500/30 to-cyan-500/0" },
  { title: "Probability & Statistics", description: "Bayes' theorem, expectation and distributions", icon: TrendingUp, accent: "from-emerald-500/25 to-emerald-500/0" },
  { title: "Algorithms", description: "Asymptotic analysis, graphs and recursion", icon: Layers, accent: "from-amber-500/30 to-amber-500/0" },
];

const DIFFICULTIES = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
] as const;

const COUNTS = [
  { value: "3", label: "3 questions" },
  { value: "5", label: "5 questions" },
  { value: "10", label: "10 questions" },
] as const;

type Difficulty = (typeof DIFFICULTIES)[number]["value"];
type Stage = "config" | "running" | "summary";

function QuizStudio() {
  const router = useRouter();
  const params = useSearchParams();

  const [stage, setStage] = useState<Stage>("config");
  const [selectedTopic, setSelectedTopic] = useState("Calculus");
  const [customTopic, setCustomTopic] = useState("");
  const [difficulty, setDifficulty] = useState<Difficulty>("intermediate");
  const [questionCount, setQuestionCount] = useState<"3" | "5" | "10">("5");

  const [session, setSession] = useState<QuizSessionDetail | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [startTime, setStartTime] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Record<number, QuizSubmitAnswerResponse>>({});
  const [lastResult, setLastResult] = useState<QuizSubmitAnswerResponse | null>(null);
  const [masteryData, setMasteryData] = useState<QuizMasteryResponse | null>(null);
  const [masteries, setMasteries] = useState<TopicMasterySummary[]>([]);
  const explanationRef = useRef<HTMLDivElement>(null);

  const activeTopic = customTopic.trim() || selectedTopic;
  const currentQuestion = session?.questions[currentIndex];
  const currentResult = session ? results[currentIndex] ?? null : null;
  const isLastQuestion = session ? currentIndex >= session.questions.length - 1 : false;

  // Arriving from the tutor's "recalibrate" link: /quiz?topic=...
  useEffect(() => {
    const topic = params.get("topic");
    if (!topic) return;
    const preset = PRESET_DOMAINS.find((d) => d.title.toLowerCase() === topic.toLowerCase());
    if (preset) setSelectedTopic(preset.title);
    else setCustomTopic(topic.slice(0, 150));
  }, [params]);

  useEffect(() => {
    if (stage !== "config") return;
    let cancelled = false;
    quizService
      .getMasteries()
      .then((items) => !cancelled && setMasteries(items))
      .catch(() => !cancelled && setMasteries([]));
    return () => {
      cancelled = true;
    };
  }, [stage]);

  useEffect(() => {
    if (stage === "running") setStartTime(Date.now());
  }, [currentIndex, stage]);

  const handleStartQuiz = async () => {
    setError(null);
    setIsGenerating(true);
    try {
      const newSession = await quizService.generateQuiz({ topic: activeTopic, difficulty, question_count: Number(questionCount) });
      setSession(newSession);
      setCurrentIndex(0);
      setSelectedOption(null);
      setResults({});
      setLastResult(null);
      setMasteryData(null);
      setStage("running");
    } catch (err) {
      const message = err instanceof Error ? err.message : "";
      if (message === "AUTHENTICATION_REQUIRED") return router.push("/login?redirect=/quiz");
      if (message === "EMAIL_VERIFICATION_REQUIRED") return router.push("/verify-email");
      setError(message || "The quiz couldn't be generated. Check that the backend is running, then try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmitAnswer = useCallback(async () => {
    if (!session || !currentQuestion || !selectedOption || isSubmitting || currentResult) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await quizService.submitAnswer({
        session_id: session.id,
        question_id: currentQuestion.id,
        selected_answer: selectedOption,
        latency_ms: Math.max(100, Date.now() - startTime),
      });
      setResults((prev) => ({ ...prev, [currentIndex]: response }));
      setLastResult(response);
      if (response.level_up) void celebrateMastery();
      if (response.session_completed || currentIndex === session.questions.length - 1) {
        quizService.getMastery(session.topic_title).then(setMasteryData).catch(() => setMasteryData(null));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Your answer couldn't be submitted. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  }, [currentIndex, currentQuestion, currentResult, isSubmitting, selectedOption, session, startTime]);

  const handleNext = useCallback(() => {
    if (!session) return;
    if (currentIndex < session.questions.length - 1) {
      setCurrentIndex((i) => i + 1);
      setSelectedOption(null);
    } else {
      setStage("summary");
    }
  }, [currentIndex, session]);

  // Keyboard: 1-4 or A-D pick an option, Enter submits or advances.
  useEffect(() => {
    if (stage !== "running" || !currentQuestion) return;
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
      if (event.key === "Enter") {
        event.preventDefault();
        if (currentResult) handleNext();
        else void handleSubmitAnswer();
        return;
      }
      if (currentResult) return;
      const key = event.key.toLowerCase();
      const index = /^[1-9]$/.test(key) ? Number(key) - 1 : /^[a-i]$/.test(key) ? key.charCodeAt(0) - 97 : -1;
      if (index >= 0 && index < currentQuestion.options.length) setSelectedOption(currentQuestion.options[index]);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [stage, currentQuestion, currentResult, handleNext, handleSubmitAnswer]);

  const reviewExplanation = () => {
    explanationRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    explanationRef.current?.focus({ preventScroll: true });
  };

  const finalScore = lastResult?.session_score ?? session?.score ?? 0;
  const finalMastery = lastResult?.session_final_mastery ?? session?.final_mastery ?? lastResult?.next_opportunity_mastery ?? null;
  const answered = Object.values(results);

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-indigo-300">Adaptive quiz</p>
          <h1 className="font-display text-4xl leading-tight text-white sm:text-5xl">
            {stage === "summary" && session ? `${session.topic_title}, assessed` : "Measure what you know"}
          </h1>
        </div>
        {session && stage === "running" && (
          <div className="flex items-center gap-3" aria-label={`Question ${currentIndex + 1} of ${session.total_questions}`}>
            <div className="flex gap-1.5">
              {session.questions.map((q, i) => {
                const result = results[i];
                return (
                  <span
                    key={q.id}
                    className={cn(
                      "h-2 w-6 rounded-full transition-colors duration-300",
                      result ? (result.is_correct ? "bg-emerald-400" : "bg-rose-400") : i === currentIndex ? "bg-indigo-400" : "bg-white/10"
                    )}
                  />
                );
              })}
            </div>
            <span className="tabular text-sm text-slate-300">
              {currentIndex + 1} / {session.total_questions}
            </span>
          </div>
        )}
      </header>

      <AnimatePresence>
        {error && (
          <motion.p
            role="alert"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-6 rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-200 ring-1 ring-rose-400/25"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {stage === "config" && (
          <motion.div key="config" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
            <div className="space-y-6">
              <p className="max-w-2xl text-[15px] leading-relaxed text-slate-300">
                Every answer updates a Bayesian estimate of your mastery. Wrong answers are diagnosed, not just marked, so you see the misconception behind them.
              </p>
              <fieldset>
                <legend className="mb-3 text-sm font-semibold text-slate-200">Pick a domain</legend>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {PRESET_DOMAINS.map((domain) => {
                    const Icon = domain.icon;
                    const selected = selectedTopic === domain.title && !customTopic.trim();
                    return (
                      <motion.button
                        key={domain.title}
                        type="button"
                        aria-pressed={selected}
                        whileHover={{ y: -3 }}
                        transition={{ type: "spring", stiffness: 400, damping: 26 }}
                        onClick={() => {
                          setSelectedTopic(domain.title);
                          setCustomTopic("");
                        }}
                        className={cn(
                          "glass relative overflow-hidden rounded-3xl p-5 text-left outline-none focus-visible:ring-2 focus-visible:ring-indigo-300",
                          selected && "shadow-glow ring-1 ring-indigo-300/50"
                        )}
                      >
                        <span aria-hidden="true" className={cn("absolute inset-0 bg-gradient-to-br opacity-70", domain.accent)} />
                        <span className="relative flex items-start gap-3">
                          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/[0.08]">
                            <Icon className="h-5 w-5 text-white" aria-hidden="true" />
                          </span>
                          <span>
                            <span className="block text-base font-semibold text-white">{domain.title}</span>
                            <span className="mt-0.5 block text-sm text-slate-300">{domain.description}</span>
                          </span>
                        </span>
                      </motion.button>
                    );
                  })}
                </div>
              </fieldset>
              <div>
                <label htmlFor="custom-topic" className="text-sm font-semibold text-slate-200">
                  Or any STEM topic
                </label>
                <input
                  id="custom-topic"
                  value={customTopic}
                  maxLength={150}
                  onChange={(event) => setCustomTopic(event.target.value)}
                  placeholder="e.g. Eigenvalues, dynamic programming, neural networks"
                  className="mt-2 w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-[15px] text-white outline-none placeholder:text-slate-500 focus:border-indigo-400/60 focus:ring-2 focus:ring-indigo-400/20"
                />
              </div>
              <div className="flex flex-wrap items-center gap-4">
                <SegmentedControl label="Difficulty" options={DIFFICULTIES} value={difficulty} onChange={setDifficulty} />
                <SegmentedControl label="Number of questions" options={COUNTS} value={questionCount} onChange={setQuestionCount} />
              </div>
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <MagneticButton size="lg" onClick={handleStartQuiz} disabled={isGenerating}>
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> Calibrating questions
                    </>
                  ) : (
                    <>
                      Start the {activeTopic} quiz <ArrowRight className="h-5 w-5" aria-hidden="true" />
                    </>
                  )}
                </MagneticButton>
              </div>
            </div>

            <GlassPanel as="aside" aria-label="Your knowledge radar" className="h-fit p-5">
              <h2 className="text-sm font-semibold text-white">Your knowledge radar</h2>
              <p className="mt-1 text-xs leading-relaxed text-slate-400">Bayesian mastery across every topic you've been assessed on.</p>
              <div className="mt-4">
                {masteries.length > 0 ? (
                  <KnowledgeRadar items={masteries} />
                ) : (
                  <p className="rounded-2xl bg-white/[0.02] px-4 py-6 text-center text-sm text-slate-400">
                    Finish a quiz to start your radar.
                  </p>
                )}
              </div>
            </GlassPanel>
          </motion.div>
        )}

        {stage === "running" && session && currentQuestion && (
          <motion.div key={`q-${currentIndex}`} initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -24 }} transition={{ type: "spring", stiffness: 260, damping: 30 }} className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_19rem]">
            <div className="space-y-5">
              <GlassPanel strong className="p-5 sm:p-7">
                <div className="mb-4 flex flex-wrap gap-2 text-[11px]">
                  <span className="rounded-full bg-indigo-500/15 px-2.5 py-1 font-medium capitalize text-indigo-200">{currentQuestion.blooms_level}</span>
                  <span className="tabular rounded-full bg-white/[0.05] px-2.5 py-1 text-slate-300">IRT difficulty {currentQuestion.irt_difficulty.toFixed(2)}</span>
                </div>
                <div className="text-lg leading-relaxed text-white sm:text-xl">
                  <MathRenderer content={currentQuestion.prompt} />
                </div>
                <div className="mt-6 space-y-2.5" role="radiogroup" aria-label="Answer options">
                  {currentQuestion.options.map((option, idx) => {
                    const submitted = currentResult !== null;
                    const chosen = submitted ? option === currentResult.selected_answer : option === selectedOption;
                    const isCorrect = submitted && option === currentResult.correct_answer;
                    const isWrong = submitted && chosen && !currentResult.is_correct;
                    return (
                      <motion.button
                        key={`${currentQuestion.id}-${idx}`}
                        type="button"
                        role="radio"
                        aria-checked={chosen}
                        disabled={submitted}
                        onClick={() => setSelectedOption(option)}
                        animate={isCorrect ? { scale: [1, 1.015, 1] } : undefined}
                        transition={{ duration: 0.45 }}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-left outline-none ring-1 transition-colors focus-visible:ring-2 focus-visible:ring-indigo-300",
                          isCorrect
                            ? "bg-emerald-500/[0.12] text-emerald-50 ring-emerald-400/60"
                            : isWrong
                              ? "bg-rose-500/[0.12] text-rose-50 ring-rose-400/60"
                              : chosen
                                ? "bg-indigo-500/15 text-white shadow-glow ring-indigo-300/60"
                                : "bg-white/[0.02] text-slate-100 ring-white/10 hover:bg-white/[0.05] hover:ring-white/20"
                        )}
                      >
                        <span className={cn("tabular flex h-7 w-7 shrink-0 items-center justify-center rounded-xl text-xs font-semibold", chosen || isCorrect ? "bg-white/15 text-white" : "bg-white/[0.06] text-slate-300")}>
                          {String.fromCharCode(65 + idx)}
                        </span>
                        <span className="flex-1 text-[15px]">
                          <MathRenderer content={option} />
                        </span>
                        {isCorrect && <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-300" aria-label="Correct answer" />}
                        {isWrong && <XCircle className="h-5 w-5 shrink-0 text-rose-300" aria-label="Your answer" />}
                      </motion.button>
                    );
                  })}
                </div>
                <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.06] pt-5">
                  <p className="text-xs text-slate-400">Keys: 1 to 4 to choose, Enter to {currentResult ? "continue" : "submit"}.</p>
                  {currentResult ? (
                    <MagneticButton onClick={handleNext}>
                      {isLastQuestion ? (
                        <>
                          See your results <Award className="h-4 w-4" aria-hidden="true" />
                        </>
                      ) : (
                        <>
                          Next question <ArrowRight className="h-4 w-4" aria-hidden="true" />
                        </>
                      )}
                    </MagneticButton>
                  ) : (
                    <MagneticButton onClick={() => void handleSubmitAnswer()} disabled={!selectedOption || isSubmitting}>
                      {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
                      {isSubmitting ? "Checking" : "Submit answer"}
                    </MagneticButton>
                  )}
                </div>
              </GlassPanel>

              <AnimatePresence>
                {currentResult && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                    <p role="status" className={cn("flex items-start gap-2.5 rounded-2xl px-4 py-3 text-sm ring-1", currentResult.is_correct ? "bg-emerald-500/10 text-emerald-100 ring-emerald-400/25" : "bg-rose-500/10 text-rose-100 ring-rose-400/25")}>
                      {currentResult.is_correct ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" /> : <XCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />}
                      <span>
                        <strong className="font-semibold">{currentResult.is_correct ? "Correct." : "Not quite."}</strong>{" "}
                        {currentResult.level_up && currentResult.retention_level ? `You're now ${currentResult.retention_level} in ${session.topic_title}.` : ""}
                      </span>
                    </p>
                    {!currentResult.is_correct && currentResult.detected_misconception && (
                      <MisconceptionCallout
                        misconception={currentResult.detected_misconception}
                        topic={session.topic_title}
                        question={currentQuestion.prompt}
                        chosenAnswer={currentResult.selected_answer}
                        onReviewExplanation={reviewExplanation}
                      />
                    )}
                    <div ref={explanationRef} tabIndex={-1} className="glass rounded-3xl p-5 outline-none">
                      <h3 className="mb-2 text-sm font-semibold text-indigo-200">Derivation</h3>
                      <MarkdownMessage text={currentResult.explanation} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <GlassPanel as="aside" aria-label="Mastery" className="flex h-fit flex-col items-center gap-4 p-5 lg:sticky lg:top-24">
              <MasteryGauge
                value={currentResult ? currentResult.next_opportunity_mastery : lastResult?.next_opportunity_mastery ?? session.initial_mastery}
                from={currentResult ? currentResult.prior_mastery : undefined}
                label={`Mastery of ${session.topic_title}`}
              />
              <dl className="grid w-full grid-cols-2 gap-2 text-center">
                <div className="rounded-2xl bg-white/[0.03] p-3">
                  <dt className="text-[11px] text-slate-400">Predicted accuracy</dt>
                  <dd className="tabular mt-1 text-lg font-semibold text-white">
                    <AnimatedNumber value={(currentResult?.predicted_accuracy ?? lastResult?.predicted_accuracy ?? 0.28) * 100} format={(v) => `${Math.round(v)}%`} />
                  </dd>
                </div>
                <div className="rounded-2xl bg-white/[0.03] p-3">
                  <dt className="text-[11px] text-slate-400">Session score</dt>
                  <dd className="tabular mt-1 text-lg font-semibold text-white">
                    <AnimatedNumber value={lastResult?.session_score ?? 0} format={(v) => `${Math.round(v)}%`} />
                  </dd>
                </div>
              </dl>
              <p className="text-center text-xs leading-relaxed text-slate-400">
                Bayesian Knowledge Tracing updates after every answer, accounting for lucky guesses and slips.
              </p>
            </GlassPanel>
          </motion.div>
        )}

        {stage === "summary" && session && (
          <motion.div key="summary" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <GlassPanel flow className="grid gap-6 p-6 sm:p-8 md:grid-cols-[auto_1fr] md:items-center">
              <MasteryGauge value={finalMastery ?? session.initial_mastery} from={session.initial_mastery} size={200} label="Final mastery" />
              <div>
                <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {[
                    { label: "Accuracy", value: finalScore, suffix: "%" },
                    { label: "Starting P(L)", value: session.initial_mastery * 100, suffix: "%" },
                    { label: "Final P(L)", value: (finalMastery ?? session.initial_mastery) * 100, suffix: "%" },
                    { label: "Answered", value: answered.length, suffix: `/${session.total_questions}` },
                  ].map((stat) => (
                    <div key={stat.label} className="rounded-2xl bg-white/[0.03] p-4">
                      <dt className="text-xs text-slate-400">{stat.label}</dt>
                      <dd className="mt-1 font-display text-3xl text-white">
                        <AnimatedNumber value={stat.value} format={(v) => `${Math.round(v)}${stat.suffix}`} />
                      </dd>
                    </div>
                  ))}
                </dl>
                <p className="mt-4 text-sm text-slate-300">
                  Retention level:{" "}
                  <strong className="font-semibold text-white">{masteryData?.retention_level ?? lastResult?.retention_level ?? "Developing"}</strong>. Predicted accuracy on your next question is{" "}
                  <strong className="tabular font-semibold text-white">{Math.round((masteryData?.predicted_accuracy ?? lastResult?.predicted_accuracy ?? 0) * 100)}%</strong>.
                </p>
              </div>
            </GlassPanel>

            <RetentionForecast mastery={finalMastery ?? session.initial_mastery} topic={session.topic_title} />

            {masteryData && masteryData.history.length > 0 && (
              <GlassPanel className="p-5 sm:p-6">
                <h2 className="text-base font-semibold text-white">Answer history</h2>
                <ol className="mt-3 space-y-2">
                  {masteryData.history.slice(-8).map((item, idx, shown) => (
                    <li key={item.attempt_id} className="flex items-center justify-between gap-3 rounded-2xl bg-white/[0.02] px-4 py-2.5 text-sm">
                      <span className="flex items-center gap-2 text-slate-200">
                        {item.is_correct ? <CheckCircle2 className="h-4 w-4 text-emerald-300" aria-label="Correct" /> : <XCircle className="h-4 w-4 text-rose-300" aria-label="Incorrect" />}
                        Attempt {masteryData.history.length - shown.length + idx + 1}
                        <span className="tabular text-xs text-slate-400">{(item.latency_ms / 1000).toFixed(1)}s</span>
                      </span>
                      <span className="tabular text-slate-300">P(L) {(item.posterior_mastery * 100).toFixed(1)}%</span>
                    </li>
                  ))}
                </ol>
              </GlassPanel>
            )}

            <div className="flex flex-wrap gap-3">
              <MagneticButton href={`/tutor?topic=${encodeURIComponent(session.topic_title)}`}>
                <MessagesSquare className="h-4 w-4" aria-hidden="true" /> Practice with the tutor
              </MagneticButton>
              <MagneticButton
                variant="glass"
                onClick={() => {
                  setStage("config");
                  setSession(null);
                  setResults({});
                  setLastResult(null);
                }}
              >
                <RotateCcw className="h-4 w-4" aria-hidden="true" /> Assess another topic
              </MagneticButton>
              <Link href="/dashboard" className="inline-flex h-11 items-center rounded-2xl px-4 text-sm font-medium text-slate-300 hover:text-white">
                Back to dashboard
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}

export default function QuizStudioPage() {
  return (
    <Suspense fallback={<div className="min-h-[60vh]" aria-busy="true" />}>
      <QuizStudio />
    </Suspense>
  );
}
