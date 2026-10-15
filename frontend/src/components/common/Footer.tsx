"use client";

import React from "react";
import Link from "next/link";
import { Sparkles, ShieldCheck, CheckCircle2, Heart } from "lucide-react";
import { APP_NAME, APP_TAGLINE } from "@/utils/constants";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950 text-slate-400 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden font-sans">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
        
        {/* Col 1: Brand & Tagline */}
        <div className="space-y-4 md:col-span-1">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <span className="font-extrabold text-lg tracking-tight text-white">
              {APP_NAME}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {APP_TAGLINE}
          </p>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-medium">
            <CheckCircle2 className="w-3 h-3" />
            <span>Systems Operational</span>
          </div>
        </div>

        {/* Col 2: Platform Navigation */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Platform Navigation
          </h4>
          <ul className="space-y-2 text-xs">
            <li>
              <Link href="/" className="hover:text-indigo-400 transition-colors">
                Home Landing
              </Link>
            </li>
            <li>
              <Link href="/#features" className="hover:text-indigo-400 transition-colors">
                Features & Capabilities
              </Link>
            </li>
            <li>
              <Link href="/#about" className="hover:text-indigo-400 transition-colors">
                About LuminaLearn AI
              </Link>
            </li>
            <li>
              <Link href="/login" className="hover:text-indigo-400 transition-colors">
                Authentication Portal
              </Link>
            </li>
          </ul>
        </div>

        {/* Col 3: Portals & Workflows */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Learning Portals
          </h4>
          <ul className="space-y-2 text-xs">
            <li>
              <Link href="/register/student" className="hover:text-indigo-400 transition-colors">
                Student Registration
              </Link>
            </li>
            <li>
              <Link href="/register/teacher" className="hover:text-indigo-400 transition-colors">
                Teacher Portal Registration
              </Link>
            </li>
            <li>
              <Link href="/onboarding" className="hover:text-indigo-400 transition-colors">
                Diagnostic Assessment Wizard
              </Link>
            </li>
            <li>
              <Link href="/dashboard" className="hover:text-indigo-400 transition-colors">
                Student Dashboard
              </Link>
            </li>
          </ul>
        </div>

        {/* Col 4: Trust & Architecture */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Security & Trust
          </h4>
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Enterprise Grade AI</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-snug">
              Argon2id cryptography, JWT token authorization, and privacy-first data handling.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-slate-800/60 flex flex-col md:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <div>
          © {new Date().getFullYear()} LuminaLearn AI. All rights reserved. Project Aurora Monorepo.
        </div>
        <div className="flex items-center gap-1 text-[11px]">
          <span>Empowering Adaptive Education with</span>
          <Heart className="w-3 h-3 text-rose-500 fill-rose-500 inline" />
          <span>& Explainable AI</span>
        </div>
      </div>
    </footer>
  );
};
