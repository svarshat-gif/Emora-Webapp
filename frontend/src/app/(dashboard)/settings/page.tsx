"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "@/store/authStore";
import { updateProfile } from "@/lib/api/auth";
import { getCompanion, COMPANIONS } from "@/lib/companions";
import { Orb } from "@/components/Orb";
import { Heart, Zap, Brain, Moon, User, Flame, BookOpen, Check, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const COMPANION_LIST = [
  { key: "sera",      Icon: Heart,  iconColor: "text-violet-300" },
  { key: "motivator", Icon: Zap,    iconColor: "text-amber-300"  },
  { key: "rational",  Icon: Brain,  iconColor: "text-cyan-300"   },
  { key: "luna",      Icon: Moon,   iconColor: "text-pink-300"   },
] as const;

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.4, ease: [0.22, 1, 0.36, 1] } }),
};

export default function SettingsPage() {
  const { user, updateUser } = useAuthStore();
  const companion = getCompanion(user?.personality);
  const [switching, setSwitching] = useState<string | null>(null);
  const [saved, setSaved] = useState<string | null>(null);

  const handleSwitch = async (key: string) => {
    if (key === user?.personality || switching) return;
    setSwitching(key);
    try {
      const updated = await updateProfile({ personality: key as "sera" | "motivator" | "rational" | "luna" });
      updateUser({ personality: updated.personality });
      setSaved(key);
      setTimeout(() => setSaved(null), 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setSwitching(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-8 py-10 space-y-8">

      {/* Header */}
      <motion.div custom={0} variants={fadeUp} initial="hidden" animate="show">
        <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: companion.color }}>
          Account
        </p>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-white/40 text-sm mt-1">Manage your profile and companion.</p>
      </motion.div>

      {/* Profile info */}
      <motion.div
        custom={1} variants={fadeUp} initial="hidden" animate="show"
        className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6 space-y-4"
      >
        <div className="flex items-center gap-2 mb-5">
          <User className="w-3.5 h-3.5 text-white/30" />
          <h2 className="text-xs font-semibold uppercase tracking-widest text-white/30">Profile</h2>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-[11px] text-white/30 uppercase tracking-wider block mb-1.5">Name</label>
            <div
              className="px-4 py-3 rounded-xl text-sm text-white/70 border border-white/[0.06] bg-white/[0.03]"
            >
              {user?.name ?? "—"}
            </div>
          </div>
          <div>
            <label className="text-[11px] text-white/30 uppercase tracking-wider block mb-1.5">Email</label>
            <div
              className="px-4 py-3 rounded-xl text-sm text-white/70 border border-white/[0.06] bg-white/[0.03]"
            >
              {user?.email ?? "—"}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Companion switcher */}
      <motion.div
        custom={2} variants={fadeUp} initial="hidden" animate="show"
        className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6"
      >
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-widest text-white/30 mb-0.5">Your Companion</h2>
            <p className="text-sm text-white/60">Switch anytime — your history stays safe.</p>
          </div>
          <AnimatePresence>
            {saved && (
              <motion.div
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.85 }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
                style={{ background: `${companion.color}18`, color: companion.color, border: `1px solid ${companion.color}30` }}
              >
                <Check className="w-3 h-3" /> Switched!
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {COMPANION_LIST.map(({ key, Icon, iconColor }) => {
            const c = COMPANIONS[key];
            const isActive = user?.personality === key;
            const isLoading = switching === key;

            return (
              <motion.button
                key={key}
                whileHover={!isActive && !switching ? { scale: 1.02, y: -1 } : {}}
                whileTap={!isActive && !switching ? { scale: 0.98 } : {}}
                onClick={() => handleSwitch(key)}
                disabled={!!switching}
                className={cn(
                  "relative p-4 rounded-2xl border text-left transition-all duration-300 overflow-hidden",
                  isActive ? "cursor-default" : "cursor-pointer",
                  switching && !isLoading ? "opacity-40" : ""
                )}
                style={{
                  background: isActive ? `${c.color}12` : "rgba(255,255,255,0.02)",
                  borderColor: isActive ? `${c.color}35` : "rgba(255,255,255,0.06)",
                  boxShadow: isActive ? `0 0 30px ${c.glowSoft}` : "none",
                }}
              >
                {/* Active glow */}
                {isActive && (
                  <div
                    className="absolute inset-0 pointer-events-none opacity-10"
                    style={{ background: `radial-gradient(ellipse at 30% 40%, ${c.color}, transparent 70%)` }}
                  />
                )}

                <div className="flex items-start justify-between mb-3 relative z-10">
                  {/* Orb or icon */}
                  <div className="w-10 h-10 shrink-0">
                    {isActive ? (
                      <Orb className="w-full h-full" companion={key} isListening />
                    ) : (
                      <div
                        className="w-full h-full rounded-full flex items-center justify-center bg-white/[0.05]"
                      >
                        <Icon className={cn("w-4 h-4", iconColor, "opacity-60")} />
                      </div>
                    )}
                  </div>

                  {/* Status badge */}
                  {isActive && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                      style={{ background: c.color }}
                    >
                      <Check className="w-3 h-3 text-white" strokeWidth={2.5} />
                    </motion.div>
                  )}
                  {isLoading && (
                    <Loader2 className="w-4 h-4 animate-spin shrink-0" style={{ color: c.color }} />
                  )}
                </div>

                <div className="relative z-10">
                  <p className={cn("text-sm font-bold leading-tight mb-0.5", isActive ? "text-white" : "text-white/50")}>
                    {c.name}
                  </p>
                  <p className={cn("text-xs leading-tight", isActive ? "text-white/50" : "text-white/25")}>
                    {c.title}
                  </p>
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Current companion description */}
        <motion.div
          key={user?.personality}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mt-4 px-4 py-3 rounded-xl text-xs text-white/40 leading-relaxed border"
          style={{ borderColor: `${companion.color}18`, background: `${companion.color}07` }}
        >
          <span style={{ color: companion.color }} className="font-semibold">{companion.name}</span>
          {" "}— {companion.description}
        </motion.div>
      </motion.div>

      {/* Stats */}
      <motion.div
        custom={3} variants={fadeUp} initial="hidden" animate="show"
        className="rounded-2xl border border-white/[0.07] bg-white/[0.02] p-6"
      >
        <div className="flex items-center gap-2 mb-5">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-white/30">Your Journey</h2>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Day Streak",      value: user?.streak ?? 0,                    Icon: Flame,    color: "#fb923c" },
            { label: "Journal Entries", value: user?.total_entries ?? 0,              Icon: BookOpen, color: companion.color },
            { label: "Goals Met",       value: user?.stats?.goals_completed ?? 0,     Icon: Check,    color: "#4ade80" },
          ].map(({ label, value, Icon, color }) => (
            <div
              key={label}
              className="p-4 rounded-2xl border text-center"
              style={{ background: `${color}08`, borderColor: `${color}18` }}
            >
              <Icon className="w-4 h-4 mx-auto mb-2 opacity-50" style={{ color }} />
              <p className="text-2xl font-bold" style={{ color }}>{value}</p>
              <p className="text-[11px] text-white/30 mt-1">{label}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
