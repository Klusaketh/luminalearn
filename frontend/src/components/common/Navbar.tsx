"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/useAuthStore";
import {
  Sparkles,
  Menu,
  X,
  LogOut,
  User,
  GraduationCap,
  School,
  LayoutDashboard,
  Compass,
  FileText,
  BrainCircuit,
  BarChart3,
  BookOpen
} from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    setMobileMenuOpen(false);
    router.push("/");
  };

  const getDashboardPath = () => {
    if (!user) return "/dashboard";
    return user.role === "teacher" ? "/dashboard/teacher" : "/dashboard";
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-base tracking-tight text-white group-hover:text-indigo-400 transition-colors">
              LuminaLearn <span className="text-indigo-400 font-light">AI</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono -mt-1 tracking-wider uppercase">
              Adaptive Ecosystem
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-300">
          <Link
            href="/"
            className={`hover:text-white transition-colors ${
              pathname === "/" ? "text-indigo-400 font-semibold" : ""
            }`}
          >
            Home
          </Link>
          <Link
            href="/subjects"
            className={`flex items-center gap-1 hover:text-white transition-colors ${
              pathname.startsWith("/subjects") || pathname.startsWith("/courses") || pathname.startsWith("/topics") || pathname.startsWith("/lessons")
                ? "text-indigo-400 font-semibold"
                : ""
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            Subjects
          </Link>
          <Link
            href="/#features"
            className="hover:text-white transition-colors"
          >
            Features
          </Link>
          <Link
            href="/#about"
            className="hover:text-white transition-colors"
          >
            About AI
          </Link>

          {isAuthenticated && user && (
            <>
              <Link
                href={getDashboardPath()}
                className={`flex items-center gap-1.5 hover:text-white transition-colors ${
                  pathname.startsWith("/dashboard") ? "text-indigo-400 font-semibold" : ""
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                Dashboard
              </Link>

              {user.role === "student" && (
                <>
                  <Link
                    href="/onboarding/roadmap"
                    className={`flex items-center gap-1 hover:text-white transition-colors ${
                      pathname === "/onboarding/roadmap" ? "text-indigo-400 font-semibold" : ""
                    }`}
                  >
                    <Compass className="w-3.5 h-3.5" />
                    Learning
                  </Link>
                  <span className="flex items-center gap-1 opacity-60 cursor-not-allowed text-slate-400" title="AI Socratic Tutor — Coming Soon in Phase 3">
                    <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
                    AI Tutor
                    <span className="text-[9px] font-bold px-1 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      Soon
                    </span>
                  </span>
                  <span className="flex items-center gap-1 opacity-60 cursor-not-allowed text-slate-400" title="Progress Analytics — Coming Soon">
                    <BarChart3 className="w-3.5 h-3.5 text-purple-400" />
                    Progress
                    <span className="text-[9px] font-bold px-1 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Soon
                    </span>
                  </span>
                  <Link
                    href="/onboarding/profile"
                    className={`flex items-center gap-1 hover:text-white transition-colors ${
                      pathname === "/onboarding/profile" ? "text-indigo-400 font-semibold" : ""
                    }`}
                  >
                    <FileText className="w-3.5 h-3.5" />
                    Profile
                  </Link>
                </>
              )}
            </>
          )}
        </nav>

        {/* Auth CTA Actions (Desktop) */}
        <div className="hidden md:flex items-center gap-3">
          {isAuthenticated && user ? (
            <div className="flex items-center gap-3">
              {/* User Badge */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800">
                <div className="w-6 h-6 rounded-full bg-indigo-600/30 text-indigo-400 flex items-center justify-center text-xs font-bold">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : <User className="w-3 h-3" />}
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-xs font-semibold text-slate-200 leading-none">
                    {user.full_name}
                  </span>
                  <span className="text-[10px] text-indigo-400 capitalize leading-tight">
                    {user.role}
                  </span>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/40 hover:bg-rose-500/10 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register/student"
                className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all flex items-center gap-1.5"
              >
                <GraduationCap className="w-3.5 h-3.5" />
                Student Join
              </Link>
              <Link
                href="/register/teacher"
                className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
              >
                <School className="w-3.5 h-3.5" />
                Teacher Portal
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white border border-slate-800"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-slate-800 bg-slate-950/95 backdrop-blur-xl px-4 pt-3 pb-6 space-y-4 animate-in slide-in-from-top-2 duration-200">
          <nav className="flex flex-col gap-2 text-sm font-medium text-slate-300">
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="py-2 hover:text-white"
            >
              Home
            </Link>
            <Link
              href="/subjects"
              onClick={() => setMobileMenuOpen(false)}
              className="py-2 hover:text-white flex items-center gap-2"
            >
              <BookOpen className="w-4 h-4 text-indigo-400" />
              Academic Subjects
            </Link>
            <Link
              href="/#features"
              onClick={() => setMobileMenuOpen(false)}
              className="py-2 hover:text-white"
            >
              Features
            </Link>
            <Link
              href="/#about"
              onClick={() => setMobileMenuOpen(false)}
              className="py-2 hover:text-white"
            >
              About AI
            </Link>

            {isAuthenticated && user && (
              <>
                <Link
                  href={getDashboardPath()}
                  onClick={() => setMobileMenuOpen(false)}
                  className="py-2 text-indigo-400 font-semibold flex items-center gap-2"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>
                {user.role === "student" && (
                  <>
                    <Link
                      href="/onboarding/roadmap"
                      onClick={() => setMobileMenuOpen(false)}
                      className="py-2 hover:text-white flex items-center gap-2"
                    >
                      <Compass className="w-4 h-4" />
                      Learning Roadmap
                    </Link>
                    <span className="py-2 opacity-60 flex items-center justify-between text-slate-400">
                      <span className="flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4 text-indigo-400" />
                        AI Tutor
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">Soon</span>
                    </span>
                    <span className="py-2 opacity-60 flex items-center justify-between text-slate-400">
                      <span className="flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-purple-400" />
                        Progress
                      </span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">Soon</span>
                    </span>
                    <Link
                      href="/onboarding/profile"
                      onClick={() => setMobileMenuOpen(false)}
                      className="py-2 hover:text-white flex items-center gap-2"
                    >
                      <FileText className="w-4 h-4" />
                      Learner Profile
                    </Link>
                  </>
                )}
              </>
            )}
          </nav>

          <div className="pt-3 border-t border-slate-800">
            {isAuthenticated && user ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-2 rounded-lg bg-slate-900">
                  <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                    {user.full_name ? user.full_name.charAt(0).toUpperCase() : "U"}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">{user.full_name}</div>
                    <div className="text-xs text-indigo-400 capitalize">{user.role}</div>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full py-2.5 text-xs font-semibold text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center justify-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold bg-slate-900 border border-slate-800 text-white rounded-lg"
                >
                  Sign In
                </Link>
                <Link
                  href="/register/student"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold bg-indigo-600 text-white rounded-lg shadow-md shadow-indigo-600/30"
                >
                  Register Student
                </Link>
                <Link
                  href="/register/teacher"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full py-2 text-center text-xs font-semibold bg-purple-600 text-white rounded-lg"
                >
                  Register Teacher
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
