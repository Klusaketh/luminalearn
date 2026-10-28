"use client";

import React, { useState } from "react";
import Link from "next/link";
import { authService } from "../../services/authService";
import { Mail, ArrowLeft, CheckCircle2, ShieldAlert, KeyRound } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [issuedToken, setIssuedToken] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);
    setIssuedToken(null);

    if (!email.trim()) {
      setErrorMessage("Please enter your registered email address.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await authService.forgotPassword(email.trim());
      setSuccessMessage(res.message);
      if (res.detail) {
        setIssuedToken(res.detail);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to issue password reset.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 text-slate-100 flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden font-sans">

      {/* Main Glassmorphic Container */}
      <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl z-10">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
            <KeyRound className="w-3.5 h-3.5" />
            Account Recovery
          </div>
          <h1 className="font-display leading-tight text-white text-4xl">
            Forgot Password?
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Enter your email to receive a password reset token
          </p>
        </div>

        {/* Success Alert */}
        {successMessage && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs space-y-2">
            <div className="flex items-center gap-2 font-semibold text-sm">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              Reset Request Processed
            </div>
            <p>{successMessage}</p>
            {issuedToken && (
              <div className="pt-2 border-t border-emerald-500/20">
                <span className="text-[11px] text-slate-400 block mb-1">Development Reset Token:</span>
                <code className="bg-slate-950 p-2 rounded text-[11px] text-emerald-300 font-mono block break-all select-all border border-emerald-500/20">
                  {issuedToken}
                </code>
                <Link
                  href={`/reset-password?token=${encodeURIComponent(issuedToken)}`}
                  className="inline-block mt-3 text-xs text-indigo-400 hover:text-indigo-300 font-semibold underline"
                >
                  Proceed to Reset Password &rarr;
                </Link>
              </div>
            )}
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Form */}
        {!successMessage && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Registered Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@example.com"
                  className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Send Password Reset Link"
              )}
            </button>
          </form>
        )}

        {/* Footer Navigation */}
        <div className="mt-8 pt-6 border-t border-slate-800/80 text-center">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
