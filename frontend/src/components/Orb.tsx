"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { getCompanion } from "@/lib/companions";

interface OrbProps {
  className?: string;
  isSpeaking?: boolean;
  isListening?: boolean;
  companion?: string;
}

export function Orb({ className, isSpeaking, isListening, companion = "sera" }: OrbProps) {
  const c = getCompanion(companion);

  return (
    <div className={cn("relative flex items-center justify-center select-none", className)}>
      {/* Ambient glow — outward light, not a dark blob */}
      <motion.div
        animate={{
          scale: isSpeaking ? [1, 1.35, 1] : isListening ? [1, 1.2, 1] : [1, 1.1, 1],
          opacity: isSpeaking ? [0.5, 0.85, 0.5] : isListening ? [0.3, 0.6, 0.3] : [0.2, 0.45, 0.2],
        }}
        transition={{
          duration: isSpeaking ? 1.0 : isListening ? 0.7 : 3.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute inset-0 rounded-full"
        style={{ backgroundColor: c.color, filter: "blur(16px)" }}
      />

      {/* Slow outer ring */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        className="absolute inset-0 rounded-full border"
        style={{ borderColor: `${c.color}55` }}
      />

      {/* Inner dashed ring when active */}
      {(isSpeaking || isListening) && (
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          className="absolute inset-[10%] rounded-full border border-dashed"
          style={{ borderColor: `${c.color}40` }}
        />
      )}

      {/* Gradient core — luminous, not dark */}
      <div
        className={cn("absolute inset-[10%] rounded-full bg-gradient-to-tr", c.gradient)}
        style={{ boxShadow: `inset 0 0 24px rgba(255,255,255,0.3), 0 0 20px ${c.glowSoft}` }}
      />

      {/* Glass overlay */}
      <div
        className="absolute inset-[18%] rounded-full border border-white/40 backdrop-blur-[2px]"
        style={{ background: "rgba(255,255,255,0.1)" }}
      />

      {/* Companion initial */}
      <span
        className="relative z-10 font-bold text-white leading-none drop-shadow-sm"
        style={{ fontSize: "28%" }}
      >
        {c.name[0]}
      </span>
    </div>
  );
}
