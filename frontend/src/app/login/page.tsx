"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, KeyRound, AlertCircle, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { extractApiError } from "@/lib/utils/apiError";
import { clearTokens } from "@/lib/api/client";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();

  // Wipe any stale tokens the moment the login page is opened.
  // This prevents the auth interceptor from attempting a token refresh
  // on a 401 wrong-credentials response and surfacing a false "Network Error".
  useEffect(() => { clearTokens(); }, []);
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(extractApiError(err, "Invalid email or password."));
    }
  };

  return (
    <div className="min-h-screen flex">

      {/* ── Left brand panel (desktop only) ── */}
      <motion.div
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center p-16 relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0a3d]/80 via-[#0d1628]/60 to-transparent" />
        <div className="absolute top-1/4 left-1/4 w-64 h-64 rounded-full bg-primary/20 blur-[80px]" />
        <div className="absolute bottom-1/4 right-1/4 w-48 h-48 rounded-full bg-secondary/15 blur-[60px]" />

        <div className="relative z-10 flex flex-col items-center text-center max-w-sm">
          {/* Animated orb */}
          <div className="relative w-28 h-28 mb-10">
            <motion.div
              animate={{ scale: [1, 1.08, 1], opacity: [0.5, 0.8, 0.5] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="absolute inset-0 rounded-full bg-primary/30 blur-[30px]"
            />
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute inset-2 rounded-full bg-gradient-to-tr from-primary via-primary-container to-secondary"
            />
            <div className="absolute inset-[10px] rounded-full bg-surface/50 backdrop-blur-md border border-white/20 flex items-center justify-center">
              <Sparkles className="w-7 h-7 text-primary" />
            </div>
          </div>

          <h1 className="text-4xl font-bold text-foreground mb-4 text-glow">Emora</h1>
          <p className="text-lg text-white/60 leading-relaxed mb-10">
            Your AI companion for emotional wellness, mindful journaling, and inner clarity.
          </p>

          {/* Feature pills */}
          {["Emotion-aware AI chat", "Daily mood journal", "Goal & routine tracking"].map(f => (
            <div key={f} className="flex items-center gap-3 mb-3 w-full">
              <div className="w-2 h-2 rounded-full bg-primary shrink-0 shadow-[0_0_8px_rgba(165,138,255,0.8)]" />
              <span className="text-sm text-white/50">{f}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Right form panel ── */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-sm"
        >
          {/* Mobile logo */}
          <div className="flex items-center gap-3 mb-10 lg:hidden">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-secondary" />
            <span className="text-xl font-semibold text-foreground">Emora</span>
          </div>

          <h2 className="text-3xl font-bold text-foreground mb-1">Welcome back</h2>
          <p className="text-white/40 mb-8 text-sm">Sign in to continue your journey.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div className="relative group">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-primary transition-colors pointer-events-none" />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Email address"
                required
                autoComplete="email"
                className="input-glass pl-11"
              />
            </div>

            {/* Password */}
            <div className="relative group">
              <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-primary transition-colors pointer-events-none" />
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Password"
                required
                autoComplete="current-password"
                className="input-glass pl-11"
              />
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 text-red-400 text-xs px-1"
              >
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                {error}
              </motion.div>
            )}

            <button type="submit" disabled={isLoading} className="btn-primary mt-2">
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                    className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full inline-block" />
                  Signing in…
                </span>
              ) : "Sign In"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-white/30">
            No account?{" "}
            <Link href="/signup" className="text-primary hover:text-primary/80 font-medium transition-colors">
              Create one free
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
