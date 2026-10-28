"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Bug, Compass, Ear, Hand, Lightbulb, Mic, Shapes, Sparkles } from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { homePathFor } from "@/utils/routes";
import { VoiceOrb, type OrbMode } from "@/components/tutor/VoiceOrb";
import { MagneticButton } from "@/components/ui/MagneticButton";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { MasteryGauge } from "@/components/quiz/MasteryGauge";
import { SmoothScroll } from "@/components/motion/SmoothScroll";
import { CustomCursor } from "@/components/motion/CustomCursor";
import { TagLabel } from "@/components/motion/TagLabel";
import { LandingNav } from "@/components/landing/LandingNav";
import { Hero } from "@/components/landing/Hero";

const DEMO: Array<{ mode: OrbMode; caption: string }> = [
  { mode: "idle", caption: "Ready when you are" },
  { mode: "listening", caption: "Listening" },
  { mode: "thinking", caption: "Routing to the Socratic Tutor" },
  { mode: "speaking", caption: "Answering with a question" },
];

const STUDENT_LINE = "Why does my recursive function never stop?";
const TUTOR_LINE = "Let's look at the smallest input first. What should your function return when n is 0, and does a call ever reach that case?";

const FACULTY = [
  {
    icon: Compass,
    name: "Socratic Tutor",
    tone: "text-indigo-200",
    body: "Never hands over the answer. Nudges, then scaffolds, then works a parallel example, one rung of the hint ladder at a time.",
  },
  {
    icon: Shapes,
    name: "Concept Explainer",
    tone: "text-cyan-200",
    body: "Teaches the idea in your style: a live diagram, a spoken walkthrough, structured notes, or a hands-on lab.",
  },
  {
    icon: Lightbulb,
    name: "Analogy Specialist",
    tone: "text-amber-200",
    body: "Turns Dijkstra into water in pipes and a mutex into a café restroom key, and tells you where each analogy breaks.",
  },
  {
    icon: Bug,
    name: "Code Diagnostic",
    tone: "text-rose-200",
    body: "Parses your code to pinpoint the line, the bug and the Big-O, then asks the question that leads you to the fix.",
  },
];

function HeroDemo() {
  const reduceMotion = useReducedMotion();
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (reduceMotion) return;
    const timer = window.setInterval(() => setStep((s) => (s + 1) % DEMO.length), 3200);
    return () => window.clearInterval(timer);
  }, [reduceMotion]);
  const current = DEMO[step];
  const showStudent = step >= 1;
  const showTutor = step >= 3;

  return (
    <div className="relative mx-auto w-full max-w-[34rem]">
      <div className="relative aspect-square w-full">
        <VoiceOrb mode={current.mode} className="h-full w-full" label={`Voice tutor demo: ${current.caption}`} />
      </div>
      <p className="absolute left-1/2 top-[8%] -translate-x-1/2 whitespace-nowrap rounded-full bg-white/[0.05] px-3 py-1 text-xs text-slate-300 ring-1 ring-white/10" aria-hidden="true">
        {current.caption}
      </p>
      <div className="absolute inset-x-0 bottom-0 space-y-2.5 px-2 sm:px-6" aria-hidden="true">
        <AnimatePresence>
          {showStudent && (
            <motion.div
              key="student"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-tr-md bg-[linear-gradient(135deg,rgba(124,58,237,0.5),rgba(8,145,178,0.35))] px-3.5 py-2 text-sm text-white"
            >
              <span className="mb-0.5 flex items-center gap-1 text-[11px] text-indigo-100/80">
                <Mic className="h-3 w-3" /> Spoken
              </span>
              {STUDENT_LINE}
            </motion.div>
          )}
          {showTutor && (
            <motion.div key="tutor" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="glass-strong w-fit max-w-[92%] rounded-2xl rounded-tl-md px-3.5 py-2.5 text-sm leading-relaxed text-slate-100">
              <span className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold text-indigo-200">
                <Compass className="h-3 w-3" /> Socratic Tutor
              </span>
              {TUTOR_LINE}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function Home() {
  const { isAuthenticated, user } = useAuthStore();
  const signedIn = isAuthenticated && user !== null;
  const dashboard = user ? homePathFor(user.role) : "/dashboard";

  return (
    <SmoothScroll>
      <CustomCursor />
      <LandingNav />
      <main className="flex w-full flex-1 flex-col">
      <Hero />

      <section id="see-it-think" aria-labelledby="see-it-think-heading" className="mx-auto grid w-full max-w-7xl scroll-mt-24 items-center gap-10 px-4 py-20 sm:px-6 lg:grid-cols-[1.05fr_1fr] lg:px-8">
        <div>
          <TagLabel>Live product</TagLabel>
          <h2 id="see-it-think-heading" className="mt-4 font-display text-4xl leading-tight text-white sm:text-6xl">
            See it <em>think</em>
          </h2>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-slate-300">
            A faculty of four AI specialists diagnoses what you already know, adapts to how you learn, and guides you to the answer out loud or in writing. It never just hands the answer over.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            {signedIn ? (
              <>
                <MagneticButton href="/tutor" size="lg" cursorLabel="Open">
                  <Mic className="h-5 w-5" aria-hidden="true" /> Talk to the tutor
                </MagneticButton>
                <MagneticButton href={dashboard} size="lg" variant="glass">
                  Your dashboard <ArrowRight className="h-5 w-5" aria-hidden="true" />
                </MagneticButton>
              </>
            ) : (
              <>
                <MagneticButton href="/register/student" size="lg" cursorLabel="Start">
                  <Sparkles className="h-5 w-5" aria-hidden="true" /> Start learning free
                </MagneticButton>
                <MagneticButton href="/login" size="lg" variant="glass">
                  Sign in <ArrowRight className="h-5 w-5" aria-hidden="true" />
                </MagneticButton>
              </>
            )}
          </div>
          <p className="mt-5 text-sm text-slate-400">
            {signedIn
              ? "Your mastery and learning style carry over to every session."
              : "Your workspace is private. Create a free account to talk with the tutor, take quizzes and track your mastery."}
          </p>
        </div>
        <HeroDemo />
      </section>

      <section id="features" aria-labelledby="faculty-heading" className="mx-auto w-full max-w-7xl scroll-mt-24 px-4 py-16 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          <h2 id="faculty-heading" className="font-display text-4xl text-white sm:text-5xl">
            One question, the right specialist.
          </h2>
          <p className="mt-4 text-[17px] leading-relaxed text-slate-300">
            A supervisor reads your message, your mastery of the topic and your learning style, then routes it, and tells you why. Every reply is grounded in your curriculum, with sources you can open.
          </p>
        </div>
        <div className="mt-10 grid gap-px overflow-hidden rounded-3xl bg-white/[0.06] sm:grid-cols-2">
          {FACULTY.map((agent) => {
            const Icon = agent.icon;
            return (
              <div key={agent.name} className="bg-space-950/80 p-6 backdrop-blur-xl sm:p-8">
                <Icon className={`h-6 w-6 ${agent.tone}`} aria-hidden="true" />
                <h3 className="mt-4 text-lg font-semibold text-white">{agent.name}</h3>
                <p className="mt-2 max-w-md text-[15px] leading-relaxed text-slate-300">{agent.body}</p>
              </div>
            );
          })}
        </div>
      </section>

      <section id="how-it-works" aria-labelledby="mastery-heading" className="mx-auto grid w-full max-w-7xl scroll-mt-24 items-center gap-10 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:px-8">
        <GlassPanel flow className="order-last flex flex-col items-center gap-6 p-8 sm:flex-row sm:justify-center lg:order-first">
          <MasteryGauge value={0.68} from={0.42} size={190} label="Mastery of Linear Algebra" />
          <ul className="space-y-3 text-sm text-slate-300">
            <li className="flex items-center gap-2">
              <Ear className="h-4 w-4 text-cyan-300" aria-hidden="true" /> Interrupt the voice tutor mid-sentence
            </li>
            <li className="flex items-center gap-2">
              <Hand className="h-4 w-4 text-amber-300" aria-hidden="true" /> Hands-on labs for kinesthetic learners
            </li>
            <li className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-indigo-300" aria-hidden="true" /> Misconceptions named, not just marked wrong
            </li>
          </ul>
        </GlassPanel>
        <div>
          <h2 id="mastery-heading" className="font-display text-4xl text-white sm:text-5xl">
            Progress you can measure.
          </h2>
          <p className="mt-4 max-w-xl text-[17px] leading-relaxed text-slate-300">
            Every quiz answer updates a Bayesian estimate of your mastery that accounts for lucky guesses and slips. A forgetting-curve forecast then tells you when to review so it sticks.
          </p>
          <Link href="/quiz" className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-300 hover:text-indigo-200">
            Try the adaptive quiz <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>

      <section id="about" aria-label="For teachers" className="mx-auto w-full max-w-7xl scroll-mt-24 px-4 pb-24 pt-8 sm:px-6 lg:px-8">
        <GlassPanel className="flex flex-col items-start justify-between gap-6 p-8 sm:p-10 md:flex-row md:items-center">
          <div>
            <h2 className="font-display text-3xl text-white sm:text-4xl">Teaching a class?</h2>
            <p className="mt-2 max-w-xl text-[15px] leading-relaxed text-slate-300">
              The teacher portal shows where students get stuck, which misconceptions recur, and who needs a check-in.
            </p>
          </div>
          <MagneticButton href={signedIn ? dashboard : "/register/teacher"} variant="glass">
            {signedIn ? "Open your dashboard" : "Create a teacher account"} <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </MagneticButton>
        </GlassPanel>
      </section>
      </main>
    </SmoothScroll>
  );
}
