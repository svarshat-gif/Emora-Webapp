"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, BrainCircuit, Heart, Sparkles } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative px-6">
      
      <main className="max-w-4xl w-full flex flex-col items-center z-10 pt-20">
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="w-32 h-32 rounded-full mb-8 relative flex items-center justify-center shadow-[0_0_40px_rgba(124,77,255,0.5)]"
        >
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary via-primary-container to-secondary opacity-80 blur-md"></div>
          <div className="absolute inset-2 rounded-full bg-surface-highest/80 backdrop-blur-xl border border-white/20"></div>
          <Sparkles className="w-10 h-10 text-primary relative z-10" />
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl md:text-7xl font-semibold tracking-tight text-center mb-6 text-glow"
        >
          Your Digital <br/><span className="text-primary-container">Sanctuary.</span>
        </motion.h1>

        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-xl text-on-surface-variant text-center max-w-2xl mb-12"
        >
          Emora is an AI emotional companion that helps you navigate your feelings, 
          set mindful goals, and find clarity through guided journaling.
        </motion.p>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
        >
          <Link href="/login" className="group">
            <div className="glass-panel hover:bg-white/10 transition-all duration-300 rounded-full px-8 py-4 flex items-center justify-center gap-2 text-white font-medium border-t border-l border-white/20">
              Start Your Journey <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        </motion.div>

        {/* Feature Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-24 w-full"
        >
          <div className="glass-panel p-8 rounded-[24px] flex flex-col gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <BrainCircuit />
            </div>
            <h3 className="text-xl font-medium text-foreground">Emotional Intelligence</h3>
            <p className="text-on-surface-variant">Advanced AI that understands nuances in your voice and text, adapting to your emotional state in real-time.</p>
          </div>
          
          <div className="glass-panel p-8 rounded-[24px] flex flex-col gap-4">
            <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center text-secondary">
              <Heart />
            </div>
            <h3 className="text-xl font-medium text-foreground">Safe & Private</h3>
            <p className="text-on-surface-variant">Your feelings are your own. Everything is secured with enterprise-grade encryption to ensure peace of mind.</p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
