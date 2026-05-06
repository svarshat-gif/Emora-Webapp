"use client";

import { motion } from "framer-motion";
import { Orb } from "@/components/Orb";
import { Flame, BookOpen, MessageCircle, ArrowRight, Sparkles } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { getCompanion } from "@/lib/companions";
import Link from "next/link";

function getGreeting() {
  const h = new Date().getHours();
  if (h < 5)  return "Still up?";
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  if (h < 21) return "Good evening";
  return "Good night";
}

const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  show: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.08, duration: 0.45, ease: [0.22, 1, 0.36, 1] } }),
};

export default function DashboardPage() {
  const { user } = useAuthStore();
  const firstName = user?.name?.split(" ")[0] ?? "there";
  const companion = getCompanion(user?.personality);

  return (
    <div className="max-w-5xl mx-auto px-8 py-10 space-y-8">

      {/* ── Greeting ── */}
      <motion.div custom={0} variants={fadeUp} initial="hidden" animate="show">
        <p className="text-sm font-medium mb-1" style={{ color: companion.color }}>
          {companion.name} is here with you
        </p>
        <h1 className="text-4xl font-bold text-white tracking-tight">
          {getGreeting()}, {firstName}.
        </h1>
        <p className="text-white/40 mt-2 text-sm">
          Your emotional sanctuary is ready. How are you feeling today?
        </p>
      </motion.div>

      {/* ── Stats row ── */}
      <motion.div
        custom={1} variants={fadeUp} initial="hidden" animate="show"
        className="grid grid-cols-3 gap-3"
      >
        {/* Streak */}
        <div
          className="relative rounded-2xl p-5 border overflow-hidden"
          style={{ background: "rgba(251,146,60,0.06)", borderColor: "rgba(251,146,60,0.15)" }}
        >
          <div className="absolute top-3 right-3">
            <Flame className="w-4 h-4 text-orange-400/50" />
          </div>
          <p className="text-3xl font-bold text-orange-300">{user?.streak ?? 0}</p>
          <p className="text-xs text-white/40 mt-1">Day streak</p>
        </div>

        {/* Entries */}
        <div
          className="relative rounded-2xl p-5 border overflow-hidden"
          style={{ background: `${companion.color}0d`, borderColor: `${companion.color}22` }}
        >
          <div className="absolute top-3 right-3">
            <BookOpen className="w-4 h-4 opacity-30" style={{ color: companion.color }} />
          </div>
          <p className="text-3xl font-bold" style={{ color: companion.color }}>
            {user?.total_entries ?? 0}
          </p>
          <p className="text-xs text-white/40 mt-1">Journal entries</p>
        </div>

        {/* Sessions */}
        <div className="relative rounded-2xl p-5 border border-white/[0.06] bg-white/[0.03] overflow-hidden">
          <div className="absolute top-3 right-3">
            <MessageCircle className="w-4 h-4 text-white/20" />
          </div>
          <p className="text-3xl font-bold text-white/60">∞</p>
          <p className="text-xs text-white/40 mt-1">Sessions available</p>
        </div>
      </motion.div>

      {/* ── Main CTA — Start a session ── */}
      <motion.div custom={2} variants={fadeUp} initial="hidden" animate="show">
        <Link href="/chat">
          <motion.div
            whileHover={{ scale: 1.015, y: -2 }}
            whileTap={{ scale: 0.99 }}
            className="relative rounded-3xl p-8 border overflow-hidden cursor-pointer group"
            style={{
              background: `linear-gradient(135deg, ${companion.color}10, ${companion.color}05)`,
              borderColor: `${companion.color}25`,
              boxShadow: `0 0 60px ${companion.glowSoft}`,
            }}
          >
            {/* Background glow orb */}
            <div
              className="absolute right-8 top-1/2 -translate-y-1/2 w-36 h-36 rounded-full pointer-events-none"
              style={{ backgroundColor: companion.color, filter: "blur(50px)", opacity: 0.12 }}
            />

            <div className="flex items-center justify-between relative z-10">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4" style={{ color: companion.color }} />
                  <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: companion.color }}>
                    Your companion
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-white mb-1">{companion.name}</h2>
                <p className="text-white/40 text-sm mb-6">{companion.title} · Ready to listen</p>

                <div
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold text-white transition-all group-hover:gap-3"
                  style={{ background: `${companion.color}25`, border: `1px solid ${companion.color}40` }}
                >
                  Begin session
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
                </div>
              </div>

              {/* Companion orb */}
              <div className="w-24 h-24 shrink-0 ml-8">
                <Orb
                  className="w-full h-full"
                  companion={user?.personality ?? "sera"}
                  isListening
                />
              </div>
            </div>
          </motion.div>
        </Link>
      </motion.div>

      {/* ── Quick actions ── */}
      <motion.div custom={3} variants={fadeUp} initial="hidden" animate="show">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-white/30 mb-4">Quick actions</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link href="/calendar">
            <motion.div
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              className="p-5 rounded-2xl border border-white/[0.07] bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer"
            >
              <BookOpen className="w-5 h-5 text-white/40 mb-3" />
              <p className="text-sm font-semibold text-white/70">New journal entry</p>
              <p className="text-xs text-white/30 mt-0.5">Capture today's thoughts</p>
            </motion.div>
          </Link>

          <Link href="/goals">
            <motion.div
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              className="p-5 rounded-2xl border border-white/[0.07] bg-white/[0.02] hover:bg-white/[0.04] transition-all cursor-pointer"
            >
              <Flame className="w-5 h-5 text-orange-400/50 mb-3" />
              <p className="text-sm font-semibold text-white/70">Daily routine</p>
              <p className="text-xs text-white/30 mt-0.5">Check off your habits</p>
            </motion.div>
          </Link>
        </div>
      </motion.div>

      {/* ── About companion ── */}
      <motion.div custom={4} variants={fadeUp} initial="hidden" animate="show">
        <div
          className="rounded-2xl p-5 border"
          style={{ background: `${companion.color}07`, borderColor: `${companion.color}18` }}
        >
          <p className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: companion.color }}>
            About {companion.name}
          </p>
          <p className="text-white/50 text-sm leading-relaxed">{companion.description}</p>
        </div>
      </motion.div>

    </div>
  );
}
