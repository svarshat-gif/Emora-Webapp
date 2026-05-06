"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mail, KeyRound, User, Heart, Zap, Brain, Moon, AlertCircle, Check, Stars } from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { extractApiError } from "@/lib/utils/apiError";
import { cn } from "@/lib/utils";

const PERSONALITIES = [
  {
    value: "sera" as const,
    label: "Sera",
    desc: "Calm & empathetic",
    Icon: Heart,
    gradient: "from-rose-400/80 to-pink-500/80",
    glow: "rgba(244,114,182,0.5)",
    border: "border-rose-400/50",
    activeBg: "bg-rose-400/10",
    iconColor: "text-rose-300",
  },
  {
    value: "motivator" as const,
    label: "Blaze",
    desc: "Energetic & uplifting",
    Icon: Zap,
    gradient: "from-amber-400/80 to-orange-500/80",
    glow: "rgba(251,191,36,0.5)",
    border: "border-amber-400/50",
    activeBg: "bg-amber-400/10",
    iconColor: "text-amber-300",
  },
  {
    value: "rational" as const,
    label: "Nova",
    desc: "Logical & analytical",
    Icon: Brain,
    gradient: "from-cyan-400/80 to-blue-500/80",
    glow: "rgba(34,211,238,0.5)",
    border: "border-cyan-400/50",
    activeBg: "bg-cyan-400/10",
    iconColor: "text-cyan-300",
  },
  {
    value: "luna" as const,
    label: "Luna",
    desc: "Warm & supportive",
    Icon: Moon,
    gradient: "from-pink-400/80 to-rose-500/80",
    glow: "rgba(244,114,182,0.5)",
    border: "border-pink-400/50",
    activeBg: "bg-pink-400/10",
    iconColor: "text-pink-300",
  },
] as const;

const PASSWORD_RULES = [
  { label: "8+ characters", test: (p: string) => p.length >= 8 },
  { label: "Uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "One number", test: (p: string) => /\d/.test(p) },
];

export default function SignupPage() {
  const router = useRouter();
  const { signup, isLoading } = useAuthStore();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [personality, setPersonality] = useState<"sera" | "motivator" | "rational" | "luna">("sera");
  const [error, setError] = useState("");
  const [showRules, setShowRules] = useState(false);

  const allRulesMet = PASSWORD_RULES.every(r => r.test(password));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!allRulesMet) {
      setShowRules(true);
      setError("Please meet all password requirements.");
      return;
    }
    try {
      await signup(email, password, name, personality);
      router.push("/dashboard");
    } catch (err) {
      setError(extractApiError(err, "Could not create account. Please try again."));
    }
  };

  const activeP = PERSONALITIES.find(p => p.value === personality)!;

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
              <Stars className="w-7 h-7 text-primary" />
            </div>
          </div>

          <h1 className="text-4xl font-bold text-foreground mb-4 text-glow">Join Emora</h1>
          <p className="text-lg text-white/60 leading-relaxed mb-10">
            Start your journey to emotional clarity, mindful journaling, and inner balance.
          </p>

          {/* Companion preview */}
          <div className="w-full space-y-3">
            {PERSONALITIES.map(p => (
              <motion.div
                key={p.value}
                animate={personality === p.value ? { scale: 1.02, opacity: 1 } : { scale: 1, opacity: 0.45 }}
                transition={{ duration: 0.3 }}
                className="flex items-center gap-3 w-full"
              >
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                  personality === p.value
                    ? `bg-gradient-to-br ${p.gradient}`
                    : "bg-white/10"
                )}>
                  <p.Icon className="w-4 h-4 text-white" />
                </div>
                <div className="text-left">
                  <div className={cn("text-sm font-semibold", personality === p.value ? "text-foreground" : "text-white/40")}>
                    {p.label}
                  </div>
                  <div className="text-xs text-white/30">{p.desc}</div>
                </div>
                {personality === p.value && (
                  <motion.div
                    layoutId="active-indicator"
                    className="ml-auto w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_rgba(165,138,255,0.8)]"
                  />
                )}
              </motion.div>
            ))}
          </div>
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

          <h2 className="text-3xl font-bold text-foreground mb-1">Create account</h2>
          <p className="text-white/40 mb-8 text-sm">Your journey to emotional clarity starts here.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div className="relative group">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-primary transition-colors pointer-events-none" />
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder="Your name"
                required
                autoComplete="name"
                className="input-glass pl-11"
              />
            </div>

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
            <div className="space-y-2">
              <div className="relative group">
                <KeyRound className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-primary transition-colors pointer-events-none" />
                <input
                  type="password"
                  value={password}
                  onChange={e => { setPassword(e.target.value); setShowRules(true); }}
                  onFocus={() => setShowRules(true)}
                  placeholder="Password"
                  required
                  autoComplete="new-password"
                  className="input-glass pl-11"
                />
              </div>

              {/* Password rules */}
              {showRules && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3 px-1 flex-wrap"
                >
                  {PASSWORD_RULES.map(rule => {
                    const met = rule.test(password);
                    return (
                      <div key={rule.label} className={cn(
                        "flex items-center gap-1.5 text-xs transition-colors",
                        met ? "text-emerald-400" : "text-white/30"
                      )}>
                        <div className={cn(
                          "w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 transition-all",
                          met ? "bg-emerald-400/20" : "bg-white/5"
                        )}>
                          <Check className="w-2 h-2" />
                        </div>
                        {rule.label}
                      </div>
                    );
                  })}
                </motion.div>
              )}
            </div>

            {/* Companion picker */}
            <div className="space-y-2 pt-1">
              <p className="text-xs text-white/30 uppercase tracking-widest px-1">Your companion</p>
              <div className="grid grid-cols-2 gap-2">
                {PERSONALITIES.map(p => {
                  const isActive = personality === p.value;
                  return (
                    <motion.button
                      key={p.value}
                      type="button"
                      onClick={() => setPersonality(p.value)}
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      className={cn(
                        "p-3 rounded-2xl border text-center transition-all duration-200 relative overflow-hidden",
                        isActive
                          ? `${p.activeBg} ${p.border}`
                          : "border-white/[0.08] bg-white/[0.03] hover:bg-white/[0.06] hover:border-white/15"
                      )}
                      style={isActive ? { boxShadow: `0 0 24px ${p.glow}` } : {}}
                    >
                      {isActive && (
                        <div className={`absolute inset-0 bg-gradient-to-b ${p.gradient} opacity-[0.07]`} />
                      )}
                      <div className={cn(
                        "w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center",
                        isActive ? `bg-gradient-to-br ${p.gradient}` : "bg-white/10"
                      )}>
                        <p.Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className={cn("text-xs font-semibold leading-tight", isActive ? "text-foreground" : "text-white/40")}>
                        {p.label}
                      </div>
                      <div className="text-[10px] text-white/25 mt-0.5 leading-tight">{p.desc}</div>
                    </motion.button>
                  );
                })}
              </div>
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
                  Creating account…
                </span>
              ) : "Create Account"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-white/30">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:text-primary/80 font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
