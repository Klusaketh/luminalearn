"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ArrowUpRight, Play } from "lucide-react";
import { useAuthStore } from "@/stores/useAuthStore";
import { homePathFor } from "@/utils/routes";
import { MagneticButton } from "@/components/ui/MagneticButton";
import { RevealText } from "@/components/motion/RevealText";
import { TagLabel } from "@/components/motion/TagLabel";
import { HeroCanvas } from "./hero/HeroCanvas";

const TAGS = ["Adaptive AI", "Bayesian mastery", "RAG tutor"];
const EASE = [0.16, 1, 0.3, 1] as const;

/** A hairline that draws in from the left. */
function Divider({ delay }: { delay: number }) {
  return (
    <span
      aria-hidden="true"
      className="block h-px w-full origin-left animate-line-draw bg-gradient-to-r from-white/25 via-white/10 to-transparent"
      style={{ animationDelay: `${delay}s` }}
    />
  );
}

export function Hero() {
  const reduceMotion = useReducedMotion();
  const { isAuthenticated, user } = useAuthStore();
  const signedIn = isAuthenticated && user !== null;
  const primaryHref = signedIn && user ? homePathFor(user.role) : "/register/student";

  const fade = (delay: number) =>
    reduceMotion
      ? {}
      : {
          initial: { opacity: 0, y: 14 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.9, delay, ease: EASE },
        };

  return (
    <section id="top" aria-label="Introduction" className="relative isolate flex min-h-[100svh] w-full flex-col overflow-hidden">
      <HeroCanvas className="-z-10 [mask-image:linear-gradient(to_bottom,black_75%,transparent)]" />

      <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col justify-between px-4 pb-8 pt-28 sm:px-6 sm:pt-32 lg:px-8">
        <RevealText
          as="h1"
          immediate
          delay={reduceMotion ? 0 : 1.0}
          stagger={0.08}
          text="Learning that *adapts* to you"
          className="max-w-[11ch] font-display text-[3.1rem] leading-[0.98] text-white sm:text-7xl lg:text-[6.4rem]"
        />

        <div className="mt-16 space-y-6">
          <Divider delay={reduceMotion ? 0 : 1.6} />
          <div className="grid gap-8 md:grid-cols-2 md:items-end">
            <motion.p {...fade(1.8)} className="tag-label max-w-sm leading-relaxed !tracking-[0.14em] text-slate-300">
              It tracks what you know (every answer, every misconception) and reshapes your next step in real time.
            </motion.p>
            <motion.div {...fade(1.95)} className="md:justify-self-end">
              <p className="max-w-md text-[15px] leading-relaxed text-slate-300">
                Four AI tutors, grounded in your curriculum, diagnose what you already know and guide you to the answer, without ever handing it over.
              </p>
              <div className="mt-5 flex items-center gap-2">
                <MagneticButton href={primaryHref} variant="light" size="lg" cursorLabel="Start">
                  {signedIn ? "Continue learning" : "Start Learning"}
                  <ArrowUpRight className="h-5 w-5" aria-hidden="true" />
                </MagneticButton>
                <MagneticButton
                  href="#see-it-think"
                  variant="outline"
                  size="lg"
                  strength={0.3}
                  className="w-14 !px-0"
                  aria-label="See the tutor think"
                  cursorLabel="Watch"
                >
                  <Play className="h-5 w-5" aria-hidden="true" />
                </MagneticButton>
              </div>
            </motion.div>
          </div>
          <Divider delay={reduceMotion ? 0 : 2.05} />
          <motion.ul {...fade(2.2)} aria-label="Highlights" className="flex flex-wrap items-center gap-x-4 gap-y-2">
            {TAGS.map((tag, index) => (
              <li key={tag} className="flex items-center gap-4">
                {index > 0 && <span aria-hidden="true" className="h-1 w-1 rounded-full bg-aurora-teal/70" />}
                <TagLabel>{tag}</TagLabel>
              </li>
            ))}
          </motion.ul>
        </div>
      </div>
    </section>
  );
}
