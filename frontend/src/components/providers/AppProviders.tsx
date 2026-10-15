"use client";

import React, { useEffect } from "react";
import { useAuthStore } from "@/stores/useAuthStore";
import { Navbar } from "@/components/common/Navbar";
import { Footer } from "@/components/common/Footer";

export const AppProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    // Automatically rehydrate login state from localStorage on app load / refresh
    initializeAuth();
  }, [initializeAuth]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/20 selection:text-indigo-300">
      <Navbar />
      <div className="flex-1 flex flex-col">{children}</div>
      <Footer />
    </div>
  );
};
