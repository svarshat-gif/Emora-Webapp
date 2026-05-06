"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Orb } from "@/components/Orb";
import { Mic, MicOff, Send, Lock, Target, Check } from "lucide-react";
import { useState, useRef, useEffect, useCallback } from "react";
import { chatAPI, goalsAPI } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { getCompanion } from "@/lib/companions";

// ── Types ─────────────────────────────────────────────────────────────────────
type Message = {
  id: string;
  sender: "user" | "emora";
  text: string;
  emotion?: string;
  isRoutine?: boolean;   // true when the AI returned a schedule/goal plan
};

// ── Goal extractor ────────────────────────────────────────────────────────────
// Parses an AI routine response into saveable goal tasks.
function extractGoalsFromRoutine(text: string): { title: string; description: string; milestones: string[] }[] {
  const goals: { title: string; description: string; milestones: string[] }[] = [];

  // Each bold section header (e.g. "**📚 DEEP STUDY BLOCK 1 (9:00 – 11:30 AM)**") becomes a goal.
  // Arrow bullets ("→ something") become milestones of that goal.
  const sections = text.split(/\*\*[^\*]+\*\*/g);
  const headers = [...text.matchAll(/\*\*([^\*]+)\*\*/g)].map(m => m[1].replace(/[🌅📚💼🎓📖🏃🌙]/gu, "").trim());

  headers.forEach((header, i) => {
    if (!header || header.length < 3) return;
    const sectionText = sections[i + 1] || "";
    const milestones = [...sectionText.matchAll(/→\s*(.+)/g)]
      .map(m => m[1].trim())
      .filter(Boolean)
      .slice(0, 5);

    goals.push({
      title: header,
      description: `Daily routine block: ${header}`,
      milestones,
    });
  });

  // Fallback: if no headers parsed, create a single goal from the whole response
  if (goals.length === 0) {
    goals.push({
      title: "Daily Routine Plan",
      description: "AI-generated daily routine",
      milestones: [],
    });
  }

  return goals.slice(0, 6); // cap at 6 goals
}

// Detect if an AI message is a routine/schedule response
function isRoutineResponse(text: string): boolean {
  return (
    (text.includes("AM") || text.includes("PM")) &&
    (text.includes("MORNING") || text.includes("STUDY") || text.includes("EVENING") ||
     text.includes("BLOCK") || text.includes("🌅") || text.includes("📚"))
  );
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function ChatPage() {
  const { user } = useAuthStore();
  const companion = getCompanion(user?.personality);
  const firstName = user?.name?.split(" ")[0] ?? "friend";

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", sender: "emora", text: companion.greeting(firstName) },
  ]);

  // Load journal insight context passed from the calendar page
  useEffect(() => {
    const raw = sessionStorage.getItem("emora_chat_context");
    if (!raw) return;
    sessionStorage.removeItem("emora_chat_context");
    try {
      const ctx = JSON.parse(raw) as { entryTitle: string; emotion: string; insight: string; therapyFocus: string };
      const opener = `I just read your journal entry "${ctx.entryTitle}" and I want to explore it with you more deeply.\n\n${ctx.insight}\n\nI'd like to work through this together. Where does that land for you — does any part of that feel especially true right now?`;
      setMessages(prev => [
        ...prev,
        { id: "ctx-" + Date.now(), sender: "emora", text: opener },
      ]);
    } catch { /* ignore malformed context */ }
  }, []);
  const [savedGoalId, setSavedGoalId] = useState<string | null>(null);
  const [savingGoalId, setSavingGoalId] = useState<string | null>(null);

  // Voice state
  const [isRecording, setIsRecording] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ── Send message ─────────────────────────────────────────────────────────
  const handleSend = async (forcedText?: string) => {
    const text = (typeof forcedText === 'string' ? forcedText : input).trim();
    if (!text || isLoading) return;

    const userMsg: Message = { id: Date.now().toString(), sender: "user", text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await chatAPI.sendMessage(text, user?.personality ?? "sera");
      const responseText = res.data?.response ?? res.response ?? "I'm here with you.";
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: "emora",
        text: responseText,
        emotion: res.data?.emotion?.dominant_emotion,
        isRoutine: isRoutineResponse(responseText),
      }]);
    } catch {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: "emora",
        text: "I'm having a moment of quiet. But I'm still right here with you.",
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── Voice input (speech → text for chat) ─────────────────────────────────
  const stopVoice = useCallback(() => {
    recognitionRef.current?.stop();
    recognitionRef.current = null;
    setIsRecording(false);
  }, []);

  const toggleVoice = useCallback(() => {
    setVoiceError("");
    if (isRecording) { stopVoice(); return; }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setVoiceError("Voice input isn't supported in this browser. Try Chrome.");
      return;
    }

    const recognition = new SR();
    recognitionRef.current = recognition;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    let finalText = "";
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += t;
        else interim = t;
      }
      setInput(finalText + interim);
    };

    recognition.onend = () => {
      setIsRecording(false);
      recognitionRef.current = null;
      // Removed auto-send to give user control over completing/editing their sentence
    };

    recognition.onerror = (e: SpeechRecognitionErrorEvent) => {
      if (e.error !== "aborted") setVoiceError("Mic error: " + e.error);
      stopVoice();
    };

    recognition.start();
    setIsRecording(true);
  }, [isRecording, stopVoice, handleSend, input]);

  // ── Save routine to Goals page ────────────────────────────────────────────
  const handleSaveGoals = async (msg: Message) => {
    setSavingGoalId(msg.id);
    try {
      const parsedGoals = extractGoalsFromRoutine(msg.text);
      await Promise.all(
        parsedGoals.map(g => goalsAPI.createGoal(g.title, g.description, g.milestones))
      );
      setSavedGoalId(msg.id);
    } catch (e) {
      console.error("Failed to save goals", e);
    } finally {
      setSavingGoalId(null);
    }
  };

  // ── Render message bubble with markdown-lite formatting ───────────────────
  const renderMessageText = (text: string) => {
    // Convert **bold** and → bullets to styled spans
    const lines = text.split("\n");
    return lines.map((line, i) => {
      if (!line.trim()) return <div key={i} className="h-2" />;

      // Bold headers
      if (/^\*\*[^*]+\*\*$/.test(line.trim())) {
        return (
          <p key={i} className="font-semibold mt-3 mb-1 first:mt-0 text-white/90">
            {line.replace(/\*\*/g, "")}
          </p>
        );
      }
      // Lines with bold inside
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      return (
        <p key={i} className="leading-relaxed">
          {parts.map((part, j) =>
            part.startsWith("**") ? (
              <strong key={j} className="text-white/90 font-semibold">
                {part.replace(/\*\*/g, "")}
              </strong>
            ) : (
              <span key={j}>{part}</span>
            )
          )}
        </p>
      );
    });
  };

  return (
    <div className="h-screen flex flex-col">

      {/* ── Header ──────────────────────────────────────────────────────────── */}
      <div
        className="flex items-center gap-4 px-6 py-4 border-b shrink-0"
        style={{ borderColor: `${companion.color}18`, background: `${companion.color}06` }}
      >
        <div className="w-10 h-10 shrink-0">
          <Orb className="w-full h-full" companion={user?.personality ?? "sera"} isSpeaking={isLoading} />
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-bold text-white leading-tight">{companion.name}</h1>
          <p className="text-xs leading-tight" style={{ color: companion.color }}>{companion.title}</p>
        </div>
        <div
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border"
          style={{ color: companion.color, borderColor: `${companion.color}30`, background: `${companion.color}0d` }}
        >
          <Lock className="w-3 h-3" /> Private
        </div>
      </div>

      {/* ── Messages ────────────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
              className={`flex gap-3 ${msg.sender === "user" ? "flex-row-reverse" : "flex-row"}`}
            >
              {/* Avatar */}
              {msg.sender === "emora" ? (
                <div className="w-8 h-8 shrink-0 mt-1">
                  <Orb className="w-full h-full" companion={user?.personality ?? "sera"} />
                </div>
              ) : (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 mt-1"
                  style={{ background: `linear-gradient(135deg, ${companion.color}60, ${companion.color}30)` }}
                >
                  {firstName[0].toUpperCase()}
                </div>
              )}

              <div className="flex flex-col gap-2 max-w-[72%]">
                {/* Bubble */}
                <div
                  className="rounded-2xl px-4 py-3 text-sm leading-relaxed"
                  style={msg.sender === "emora" ? {
                    background: "rgba(255,255,255,0.04)",
                    border: `1px solid ${companion.color}22`,
                    borderLeft: `2px solid ${companion.color}`,
                    color: "rgba(226,232,255,0.9)",
                  } : {
                    background: `${companion.color}18`,
                    border: `1px solid ${companion.color}30`,
                    color: "rgba(226,232,255,0.95)",
                  }}
                >
                  <div className="space-y-0.5">
                    {msg.sender === "emora" ? renderMessageText(msg.text) : msg.text}
                  </div>
                </div>

                {/* Save to Goals button — shown when AI returns a schedule */}
                {msg.sender === "emora" && msg.isRoutine && (
                  <motion.button
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    onClick={() => handleSaveGoals(msg)}
                    disabled={!!savingGoalId || savedGoalId === msg.id}
                    className="self-start flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all duration-200 disabled:opacity-60"
                    style={{
                      background: savedGoalId === msg.id ? `${companion.color}20` : "rgba(255,255,255,0.04)",
                      borderColor: `${companion.color}40`,
                      color: companion.color,
                    }}
                  >
                    {savingGoalId === msg.id ? (
                      <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        className="w-3 h-3 border border-current border-t-transparent rounded-full inline-block" />
                    ) : savedGoalId === msg.id ? (
                      <Check className="w-3 h-3" />
                    ) : (
                      <Target className="w-3 h-3" />
                    )}
                    {savedGoalId === msg.id ? "Saved to Goals!" : savingGoalId === msg.id ? "Saving…" : "Save to Goals"}
                  </motion.button>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              className="flex gap-3 items-center"
            >
              <div className="w-8 h-8 shrink-0">
                <Orb className="w-full h-full" companion={user?.personality ?? "sera"} isSpeaking />
              </div>
              <div
                className="flex items-center gap-1.5 px-4 py-3 rounded-2xl"
                style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${companion.color}22` }}
              >
                {[0, 0.18, 0.36].map((delay, i) => (
                  <motion.div
                    key={i}
                    animate={{ scale: [1, 1.4, 1], opacity: [0.4, 1, 0.4] }}
                    transition={{ repeat: Infinity, duration: 1.2, delay }}
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: companion.color }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ───────────────────────────────────────────────────────────── */}
      <div
        className="px-6 py-4 border-t shrink-0"
        style={{ borderColor: "rgba(255,255,255,0.05)", background: "rgba(6,11,24,0.6)", backdropFilter: "blur(20px)" }}
      >
        {/* Voice error */}
        {voiceError && (
          <p className="text-xs text-red-400 mb-2 px-1">{voiceError}</p>
        )}

        <div
          className="flex items-end gap-3 rounded-2xl border px-4 py-3 transition-all duration-200"
          style={{
            background: "rgba(255,255,255,0.03)",
            borderColor: isRecording ? companion.color : `${companion.color}20`,
            boxShadow: isRecording ? `0 0 16px ${companion.color}30` : "none",
          }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder={isRecording ? "Listening… speak now" : "Type your feelings or thoughts…"}
            rows={1}
            disabled={isLoading}
            className="flex-1 bg-transparent text-white/90 placeholder:text-white/25 text-sm resize-none focus:outline-none leading-relaxed max-h-32"
            style={{ scrollbarWidth: "none" }}
          />

          <div className="flex items-center gap-2 shrink-0 pb-0.5">
            {/* Mic button — voice to text */}
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={toggleVoice}
              disabled={isLoading}
              className="p-2 rounded-xl transition-all relative"
              style={{
                background: isRecording ? `${companion.color}25` : "transparent",
                color: isRecording ? companion.color : "rgba(255,255,255,0.25)",
              }}
              title={isRecording ? "Stop recording" : "Voice input"}
            >
              {isRecording ? (
                <>
                  <motion.div
                    className="absolute inset-0 rounded-xl border"
                    style={{ borderColor: companion.color }}
                    animate={{ scale: [1, 1.3], opacity: [0.6, 0] }}
                    transition={{ repeat: Infinity, duration: 0.9 }}
                  />
                  <MicOff className="w-4 h-4 relative z-10" />
                </>
              ) : (
                <Mic className="w-4 h-4 hover:text-white/50 transition-colors" />
              )}
            </motion.button>

            {/* Send button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleSend()}
              disabled={isLoading || !input.trim()}
              className="w-8 h-8 rounded-xl flex items-center justify-center transition-all disabled:opacity-30"
              style={{ background: input.trim() ? companion.color : "rgba(255,255,255,0.06)" }}
            >
              <Send className="w-3.5 h-3.5 text-white" />
            </motion.button>
          </div>
        </div>

        <p className="text-center text-[10px] text-white/15 mt-2">
          {companion.name} · Your conversations are private and secure
        </p>
      </div>
    </div>
  );
}
