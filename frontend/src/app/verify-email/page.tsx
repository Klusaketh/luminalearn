"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "../../services/authService";
import {
  MailCheck,
  CheckCircle2,
  ShieldAlert,
  ArrowLeft,
  RotateCw,
  ArrowRight,
  Clock,
  AlertTriangle,
} from "lucide-react";

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [email, setEmail] = useState("");
  const [digits, setDigits] = useState<string[]>(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isAlreadyVerified, setIsAlreadyVerified] = useState(false);
  const [isExpired, setIsExpired] = useState(false);
  const [isAttemptLocked, setIsAttemptLocked] = useState(false);
  const [cooldown, setCooldown] = useState(60);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Initialize email from URL search params & focus first input
  useEffect(() => {
    const urlEmail = searchParams.get("email");
    if (urlEmail) {
      setEmail(urlEmail);
    }
    inputRefs.current[0]?.focus();
  }, [searchParams]);

  // 60-second resend countdown timer
  useEffect(() => {
    if (cooldown <= 0) return;
    const interval = setInterval(() => {
      setCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [cooldown]);

  const handleDigitChange = (index: number, value: string) => {
    // Only accept numeric characters
    const char = value.replace(/\D/g, "").slice(-1);
    const newDigits = [...digits];
    newDigits[index] = char;
    setDigits(newDigits);
    setErrorMessage(null);

    // Auto-advance focus to next input
    if (char && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace") {
      if (!digits[index] && index > 0) {
        // Move to previous input on backspace if current is empty
        inputRefs.current[index - 1]?.focus();
      }
    } else if (e.key === "ArrowLeft" && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === "ArrowRight" && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "");
    if (!pasted) return;

    const newDigits = [...digits];
    for (let i = 0; i < 6; i++) {
      newDigits[i] = pasted[i] || "";
    }
    setDigits(newDigits);
    setErrorMessage(null);

    // Focus last filled digit or final input
    const nextIndex = Math.min(pasted.length, 5);
    inputRefs.current[nextIndex]?.focus();
  };

  const otpValue = digits.join("");
  const isComplete = otpValue.length === 6 && digits.every((d) => d !== "");

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!email.trim()) {
      setErrorMessage("Please enter the email address to verify.");
      return;
    }
    if (!isComplete) {
      setErrorMessage("Please enter all 6 digits of your verification code.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setIsExpired(false);
    setIsAttemptLocked(false);

    try {
      await authService.verifyEmail(email.trim().toLowerCase(), otpValue);
      setIsSuccess(true);
      // Requirement 16: Successful verification redirects user to /login
      setTimeout(() => {
        router.push("/login?verified=true");
      }, 2000);
    } catch (err: any) {
      const msg = err.message || "Verification failed.";
      if (msg.toLowerCase().includes("already verified")) {
        setIsAlreadyVerified(true);
      } else {
        setErrorMessage(msg);
      }

      if (msg.toLowerCase().includes("expired")) {
        setIsExpired(true);
      } else if (msg.toLowerCase().includes("maximum verification attempts")) {
        setIsAttemptLocked(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    if (cooldown > 0 || isResending) return;
    if (!email.trim()) {
      setErrorMessage("Please provide your email address to receive a new code.");
      return;
    }

    setIsResending(true);
    setErrorMessage(null);
    setIsExpired(false);
    setIsAttemptLocked(false);

    try {
      await authService.resendOTP(email.trim().toLowerCase());
      setCooldown(60);
      setDigits(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (err: any) {
      const msg = err.message || "Failed to resend verification code.";
      if (msg.toLowerCase().includes("already verified")) {
        setIsAlreadyVerified(true);
      } else {
        setErrorMessage(msg);
      }
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden font-sans">
      {/* Background Ambient Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-indigo-600/15 blur-[140px] rounded-full pointer-events-none" />

      {/* Main Glassmorphic Card */}
      <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-8 shadow-2xl z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <MailCheck className="w-3.5 h-3.5" />
            Two-Step Email Verification
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Enter 6-Digit Code
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {email ? (
              <span>
                Sent to <strong className="text-slate-200">{email}</strong>
              </span>
            ) : (
              "Enter your registered email and the 6-digit code"
            )}
          </p>
        </div>

        {/* Success State */}
        {isSuccess ? (
          <div className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center space-y-4 animate-in fade-in duration-300">
            <div className="w-14 h-14 bg-emerald-500/20 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto text-emerald-400 shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Email Verified!</h3>
              <p className="text-xs text-slate-300 mt-1">
                Your account has been successfully activated. Redirecting you to sign in...
              </p>
            </div>
            <Link
              href="/login?verified=true"
              className="inline-flex items-center justify-center gap-2 w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors shadow-md"
            >
              Proceed to Sign In
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : isAlreadyVerified || (errorMessage && errorMessage.toLowerCase().includes("already verified")) ? (
          <div className="p-6 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-center space-y-4 animate-in fade-in duration-300">
            <div className="w-14 h-14 bg-emerald-500/20 border border-emerald-500/40 rounded-full flex items-center justify-center mx-auto text-emerald-400 shadow-lg shadow-emerald-500/20">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">Email Already Verified!</h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                Your account for <strong className="text-slate-100">{email || "this email"}</strong> has already been verified and is active. You do not need to enter a code!
              </p>
            </div>
            <div className="pt-2">
              <Link
                href={`/login?email=${encodeURIComponent(email)}`}
                className="inline-flex items-center justify-center gap-2 w-full py-3 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold rounded-lg transition-all shadow-lg shadow-indigo-600/25"
              >
                Sign In to Your Account
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleVerify} className="space-y-6">
            {/* Email Input (if not passed via URL) */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Account Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@domain.com"
                className="w-full bg-slate-950/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-lg px-3 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all"
              />
            </div>

            {/* 6-Digit OTP Inputs */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-medium text-slate-300">
                  Verification Code (OTP)
                </label>
                <span className="text-[11px] text-slate-500">Expires in 10 minutes</span>
              </div>
              <div className="flex justify-between gap-2" onPaste={handlePaste}>
                {digits.map((digit, idx) => (
                  <input
                    key={idx}
                    ref={(el) => {
                      inputRefs.current[idx] = el;
                    }}
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={1}
                    value={digit}
                    disabled={isLoading || isAttemptLocked}
                    onChange={(e) => handleDigitChange(idx, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(idx, e)}
                    className={`w-12 h-14 text-center text-2xl font-bold font-mono rounded-xl bg-slate-950/80 border transition-all outline-none ${
                      digit
                        ? "border-indigo-500 text-indigo-300 ring-1 ring-indigo-500/50"
                        : "border-slate-800 text-slate-100 focus:border-indigo-400 focus:ring-1 focus:ring-indigo-400"
                    } ${
                      errorMessage ? "border-rose-500/60" : ""
                    } disabled:opacity-50`}
                  />
                ))}
              </div>
            </div>

            {/* Error & Warning Alert States */}
            {errorMessage && (
              <div
                className={`p-3.5 rounded-xl border text-xs flex items-start gap-2.5 ${
                  isAttemptLocked
                    ? "bg-rose-500/10 border-rose-500/40 text-rose-300"
                    : isExpired
                    ? "bg-amber-500/10 border-amber-500/40 text-amber-300"
                    : "bg-rose-500/10 border-rose-500/30 text-rose-400"
                }`}
              >
                {isAttemptLocked ? (
                  <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                ) : isExpired ? (
                  <Clock className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                ) : (
                  <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                )}
                <div className="space-y-1">
                  <div className="font-semibold">
                    {isAttemptLocked
                      ? "Verification Locked"
                      : isExpired
                      ? "Code Expired"
                      : "Verification Error"}
                  </div>
                  <div>{errorMessage}</div>
                </div>
              </div>
            )}

            {/* Verify Button */}
            <button
              type="submit"
              disabled={isLoading || !isComplete || isAttemptLocked}
              className="w-full bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 px-4 rounded-lg transition-all shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Verify Code
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            {/* Resend OTP Section with 60s Cooldown */}
            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>Didn&apos;t receive the code?</span>
              <button
                type="button"
                onClick={handleResend}
                disabled={cooldown > 0 || isResending}
                className="inline-flex items-center gap-1.5 font-semibold text-indigo-400 hover:text-indigo-300 disabled:text-slate-600 disabled:cursor-not-allowed transition-colors"
              >
                <RotateCw className={`w-3.5 h-3.5 ${isResending ? "animate-spin" : ""}`} />
                {cooldown > 0 ? `Resend code in ${cooldown}s` : "Resend code"}
              </button>
            </div>
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

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <VerifyEmailForm />
    </Suspense>
  );
}
