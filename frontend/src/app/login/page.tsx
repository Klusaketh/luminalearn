"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useAuthStore } from "../../stores/useAuthStore";
import { enterWorkspace } from "../../utils/postSignIn";
import { Lock, Mail, Eye, EyeOff, GraduationCap, School, ShieldAlert, ArrowRight, CheckCircle2 } from "lucide-react";
import { GoogleAuthButton } from "../../components/auth/GoogleAuthButton";

type RoleTab = "student" | "teacher" | "admin";

function LoginForm() {
  const searchParams = useSearchParams();
  const { login, user, isAuthenticated, isLoading, error, clearError } = useAuthStore();

  const [activeTab, setActiveTab] = useState<RoleTab>("student");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [requiresVerification, setRequiresVerification] = useState(false);
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);

  useEffect(() => {
    if (searchParams.get("verified") === "true") {
      setVerifiedSuccess(true);
    }
  }, [searchParams]);

  // The only place that navigates after sign-in (password or Google), so it happens exactly once.
  const role = isAuthenticated ? user?.role : undefined;
  useEffect(() => {
    if (role) void enterWorkspace(role, searchParams.get("redirect"));
  }, [role, searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setRequiresVerification(false);
    clearError();

    if (!email.trim() || !password) {
      setFormError("Please enter both email address and password.");
      return;
    }

    try {
      await login(email.trim().toLowerCase(), password); // the effect above takes it from here
    } catch (err) {
      const msg = err instanceof Error && err.message ? err.message : "Invalid credentials. Please check your details.";
      if (msg.includes("EMAIL_VERIFICATION_REQUIRED")) {
        setRequiresVerification(true);
        setFormError("Email verification is required before signing in.");
      } else {
        setFormError(msg);
      }
    }
  };

  return (
    <div className="flex-1 text-slate-100 flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden font-sans">

      {/* Main Glassmorphic Container */}
      <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl z-10">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
            LuminaLearn Platform
          </div>
          <h1 className="font-display leading-tight text-white text-4xl">
            Welcome Back
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Access your adaptive Socratic learning portal
          </p>
        </div>

        {/* Verified Success Alert */}
        {verifiedSuccess && (
          <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>Email verified successfully! Please sign in with your password.</span>
          </div>
        )}

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-3 gap-1 p-1 bg-slate-950/80 border border-slate-800/80 rounded-xl mb-6">
          <button
            type="button"
            onClick={() => { setActiveTab("student"); setFormError(null); }}
            className={`flex items-center justify-center gap-1.5 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === "student"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            Student
          </button>

          <button
            type="button"
            onClick={() => { setActiveTab("teacher"); setFormError(null); }}
            className={`flex items-center justify-center gap-1.5 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === "teacher"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <School className="w-3.5 h-3.5" />
            Teacher
          </button>

          <button
            type="button"
            onClick={() => { setActiveTab("admin"); setFormError(null); }}
            className={`flex items-center justify-center gap-1.5 py-2 text-xs font-semibold rounded-lg transition-all ${
              activeTab === "admin"
                ? "bg-slate-700 text-white shadow-md shadow-slate-700/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Admin
          </button>
        </div>

        {/* Error Alert with Verification Link */}
        {(formError || error) && (
          <div className="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs space-y-2">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>{formError || error}</span>
            </div>
            {requiresVerification && (
              <div className="pt-2 border-t border-rose-500/20">
                <Link
                  href={`/verify-email?email=${encodeURIComponent(email.trim())}`}
                  className="text-indigo-400 hover:text-indigo-300 font-semibold underline text-xs inline-flex items-center gap-1"
                >
                  Verify your email with the 6-digit code &rarr;
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
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
                placeholder={
                  activeTab === "student"
                    ? "student@luminalearn.ai"
                    : activeTab === "teacher"
                    ? "instructor@luminalearn.ai"
                    : "admin@luminalearn.ai"
                }
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-medium text-slate-300">
                Password
              </label>
              <Link
                href="/forgot-password"
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                Forgot Password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
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

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 group disabled:opacity-50"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                Sign In to LuminaLearn
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
              Or continue with
            </span>
          </div>
        </div>

        {/* Google Authentication */}
        <GoogleAuthButton
          role={activeTab === "teacher" ? "teacher" : "student"}
          text="Continue with Google"
        />

        {/* Footer Navigation */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
          <p className="text-xs text-slate-400">
            Don&apos;t have an account?{" "}
            <Link
              href="/register/student"
              className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
            >
              Register Student
            </Link>{" "}
            or{" "}
            <Link
              href="/register/teacher"
              className="text-purple-400 hover:text-purple-300 font-semibold transition-colors"
            >
              Register Teacher
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 text-slate-100 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
