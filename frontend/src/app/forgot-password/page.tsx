"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { authService, OTPDelivery } from "../../services/authService";
import { OtpDeliveryNotice } from "../../components/auth/OtpDeliveryNotice";
import { Mail, ArrowLeft, ArrowRight, ShieldAlert, KeyRound, RotateCw } from "lucide-react";

const RESEND_COOLDOWN_SECONDS = 60;

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [delivery, setDelivery] = useState<OTPDelivery | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;
    const interval = setInterval(() => setCooldown((prev) => (prev > 0 ? prev - 1 : 0)), 1000);
    return () => clearInterval(interval);
  }, [cooldown]);

  const requestCode = async () => {
    setErrorMessage(null);
    if (!email.trim()) {
      setErrorMessage("Please enter your registered email address.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await authService.forgotPassword(email.trim().toLowerCase());
      setDelivery(res.otp_delivery);
      setCooldown(RESEND_COOLDOWN_SECONDS);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to send a password reset code.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void requestCode();
  };

  const resetHref = `/reset-password?email=${encodeURIComponent(email.trim().toLowerCase())}`;

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
            We&apos;ll email you a 6-digit code to choose a new password
          </p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {delivery ? (
          <div className="space-y-4">
            <OtpDeliveryNotice delivery={delivery} email={email.trim()} />
            {delivery === "email" && (
              <p className="text-[11px] text-slate-500">
                No email arrives if there is no account for this address.
              </p>
            )}

            {delivery !== "failed" && (
              <Link
                href={resetHref}
                className="w-full bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 text-sm"
              >
                Enter the code
                <ArrowRight className="w-4 h-4" />
              </Link>
            )}

            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>Didn&apos;t receive the code?</span>
              <button
                type="button"
                onClick={() => void requestCode()}
                disabled={cooldown > 0 || isLoading}
                className="inline-flex items-center gap-1.5 font-semibold text-indigo-400 hover:text-indigo-300 disabled:text-slate-600 disabled:cursor-not-allowed transition-colors"
              >
                <RotateCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
                {cooldown > 0 ? `Resend code in ${cooldown}s` : "Resend code"}
              </button>
            </div>
          </div>
        ) : (
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
                "Send Reset Code"
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
