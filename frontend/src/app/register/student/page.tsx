"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../../../stores/useAuthStore";
import { Mail, Lock, User, Eye, EyeOff, GraduationCap, ShieldAlert, ArrowRight, Eye as VisualIcon, Headphones, BookOpen, Target } from "lucide-react";
import { GoogleAuthButton } from "../../../components/auth/GoogleAuthButton";
import { enterWorkspace } from "../../../utils/postSignIn";

type VARKModality = "visual" | "auditory" | "read_write" | "kinesthetic";

export default function StudentRegistrationPage() {
  const router = useRouter();
  const { registerStudent, user, isAuthenticated, isLoading, error, clearError } = useAuthStore();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [modality, setModality] = useState<VARKModality>("visual");
  const [formError, setFormError] = useState<string | null>(null);

  // Already signed in (or just signed in with Google): continue into the workspace, once.
  const role = isAuthenticated ? user?.role : undefined;
  useEffect(() => {
    if (role) void enterWorkspace(role, null);
  }, [role]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    clearError();

    if (!fullName.trim() || !email.trim() || !password) {
      setFormError("Please fill out all required fields.");
      return;
    }

    if (password.length < 8) {
      setFormError("Password must be at least 8 characters long.");
      return;
    }

    try {
      await registerStudent({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        preferred_modality: modality,
      });
      router.push(`/verify-email?email=${encodeURIComponent(email.trim())}`);
    } catch (err: any) {
      setFormError(err.message || "Registration failed. Please check details.");
    }
  };

  const varkOptions: { id: VARKModality; title: string; desc: string; icon: any }[] = [
    {
      id: "visual",
      title: "Visual",
      desc: "Diagrams & visual maps",
      icon: VisualIcon,
    },
    {
      id: "auditory",
      title: "Auditory",
      desc: "Voice & spoken explanation",
      icon: Headphones,
    },
    {
      id: "read_write",
      title: "Read / Write",
      desc: "Text summaries & articles",
      icon: BookOpen,
    },
    {
      id: "kinesthetic",
      title: "Kinesthetic",
      desc: "Interactive practice & step-by-step",
      icon: Target,
    },
  ];

  return (
    <div className="flex-1 text-slate-100 flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden font-sans">

      {/* Main Container */}
      <div className="w-full max-w-lg bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl z-10">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
            <GraduationCap className="w-3.5 h-3.5" />
            Student Account Registration
          </div>
          <h1 className="font-display leading-tight text-white text-4xl">
            Join LuminaLearn AI
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Personalized Socratic AI Tutoring tailored to your cognitive style
          </p>
        </div>

        {/* Error Alert */}
        {(formError || error) && (
          <div className="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{formError || error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Full Name
            </label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Alex Mercer"
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex.mercer@student.edu"
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 8 characters"
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-10 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 text-xs"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* VARK Modality Selection Cards */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-2">
              Preferred Learning Style (VARK Model)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {varkOptions.map((opt) => {
                const IconComponent = opt.icon;
                const isSelected = modality === opt.id;
                return (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setModality(opt.id)}
                    className={`flex flex-col items-start p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? "bg-indigo-600/20 border-indigo-500 text-white ring-1 ring-indigo-500"
                        : "bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-300"
                    }`}
                  >
                    <div className="flex items-center gap-1.5 font-semibold text-xs mb-0.5">
                      <IconComponent className={`w-3.5 h-3.5 ${isSelected ? "text-indigo-400" : "text-slate-500"}`} />
                      {opt.title}
                    </div>
                    <span className="text-[11px] text-slate-500 leading-snug">
                      {opt.desc}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-4 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 group disabled:opacity-50"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                Create Student Account
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-slate-900/90 px-3 text-slate-500 font-medium">
              Or sign up with
            </span>
          </div>
        </div>

        {/* Google Sign Up */}
        <GoogleAuthButton
          role="student"
          preferredModality={modality}
          text="Sign up with Google"
        />

        {/* Footer Navigation */}
        <div className="mt-6 pt-6 border-t border-slate-800/80 text-center">
          <p className="text-xs text-slate-400">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
            >
              Sign In Here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
