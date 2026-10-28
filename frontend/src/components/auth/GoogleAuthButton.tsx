"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuthStore } from "../../stores/useAuthStore";

interface GoogleAuthButtonProps {
  role?: "student" | "teacher";
  preferredModality?: "visual" | "auditory" | "read_write" | "kinesthetic";
  text?: string;
  className?: string;
}

declare global {
  interface Window {
    google?: any;
  }
}

export function GoogleAuthButton({
  role = "student",
  preferredModality = "visual",
  text = "Continue with Google",
  className = "",
}: GoogleAuthButtonProps) {
  const { loginWithGoogle, isLoading } = useAuthStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [showDevModal, setShowDevModal] = useState(false);
  const [devEmail, setDevEmail] = useState("");
  const [devName, setDevName] = useState("");

  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  const handleCredentialResponse = useCallback(async (credential: string) => {
    setIsProcessing(true);
    setAuthError(null);
    try {
      // Signing in is all this button does: the page it sits on navigates once the session exists.
      await loginWithGoogle(credential, role, preferredModality);
    } catch (err: any) {
      setAuthError(err.message || "Google authentication failed. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  }, [loginWithGoogle, role, preferredModality]);

  useEffect(() => {
    if (!googleClientId) return;

    // Load Google Identity Services script if not already loaded
    const scriptId = "google-gsi-client";
    let script = document.getElementById(scriptId) as HTMLScriptElement | null;

    const initGsi = () => {
      if (window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: (response: any) => {
            if (response?.credential) {
              handleCredentialResponse(response.credential);
            }
          },
        });
      }
    };

    if (!script) {
      script = document.createElement("script");
      script.id = scriptId;
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = initGsi;
      document.body.appendChild(script);
    } else if (window.google?.accounts?.id) {
      initGsi();
    }
  }, [googleClientId, handleCredentialResponse]);

  const handleClick = () => {
    setAuthError(null);
    if (googleClientId && window.google?.accounts?.id) {
      setIsProcessing(true);
      try {
        window.google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            setIsProcessing(false);
            console.warn("Google One Tap prompt was not displayed or was skipped:", notification);
          }
        });
      } catch (err) {
        setIsProcessing(false);
        setAuthError("Unable to open Google Sign-In prompt. Please ensure popups and cookies are enabled.");
      }
    } else {
      if (process.env.NODE_ENV === "production") {
        setAuthError("Google Sign-In is currently being configured for this deployment. Please use email and password authentication.");
      } else {
        // In local development, show explicit dev simulation modal if Client ID is missing
        setShowDevModal(true);
      }
    }
  };

  const handleDevSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!devEmail.trim()) return;
    if (process.env.NODE_ENV === "production") {
      setAuthError("Development mock tokens are strictly forbidden in production.");
      setShowDevModal(false);
      return;
    }
    const cred = `dev-google:${devEmail.trim()}:${devName.trim() || devEmail.split("@")[0]}`;
    setShowDevModal(false);
    handleCredentialResponse(cred);
  };

  return (
    <>
      <button
        type="button"
        onClick={handleClick}
        disabled={isLoading || isProcessing}
        className={`w-full flex items-center justify-center gap-3 bg-slate-950/80 hover:bg-slate-900 text-slate-200 border border-slate-700/80 hover:border-slate-600 rounded-lg py-2.5 px-4 text-xs font-semibold transition-all shadow-md group disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      >
        {isProcessing ? (
          <div className="w-4 h-4 border-2 border-slate-400 border-t-white rounded-full animate-spin" />
        ) : (
          <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
            />
            <path
              fill="#34A853"
              d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
            />
            <path
              fill="#EA4335"
              d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
            />
          </svg>
        )}
        <span>{text}</span>
      </button>

      {authError && (
        <div className="mt-2 p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          {authError}
        </div>
      )}

      {/* Dev Mode Instant Google Auth Modal (strictly development testing) */}
      {showDevModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                  />
                </svg>
                <h4 className="text-sm font-bold text-white">Google Sign-In</h4>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30">
                Dev Test
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Google Client ID not yet set in environment. Simulate Google Sign-In for local development:
            </p>
            <form onSubmit={handleDevSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1">
                  Google Email
                </label>
                <input
                  type="email"
                  required
                  placeholder="e.g. saketh.paramkusam5@gmail.com"
                  value={devEmail}
                  onChange={(e) => setDevEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-600 focus:border-indigo-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1">
                  Full Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Saketh Paramkusam"
                  value={devName}
                  onChange={(e) => setDevName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-600 focus:border-indigo-500 outline-none"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowDevModal(false)}
                  className="w-1/2 py-2 text-xs text-slate-400 hover:text-white border border-slate-800 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-1/2 py-2 text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg shadow-md"
                >
                  Continue
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
