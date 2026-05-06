"use client";

import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Plus, X, BookOpen, Mic, Flame, PenLine, Square, MessageCircle } from "lucide-react";
import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { createEntry as createJournalEntry, getEntry as fetchJournalEntry, getEntryInsights, getCalendarData as fetchCalendarData, type DayEntry } from "@/lib/api/journal";
import { generateEmotionGoals } from "@/lib/api/goals";
import { getStreak } from "@/lib/api/profile";
import { useAuthStore } from "@/store/authStore";
import { getCompanion } from "@/lib/companions";
import { cn } from "@/lib/utils";

type CalendarData = Record<string, DayEntry>;

const EMOTION_META: Record<string, { label: string; color: string }> = {
  joy:      { label: "Joy",      color: "#f59e0b" },
  sadness:  { label: "Sadness",  color: "#60a5fa" },
  anger:    { label: "Anger",    color: "#f87171" },
  fear:     { label: "Fear",     color: "#a78bfa" },
  disgust:  { label: "Disgust",  color: "#4ade80" },
  surprise: { label: "Surprise", color: "#fb923c" },
  neutral:  { label: "Neutral",  color: "#94a3b8" },
};
const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MAX_RECORD_SECS = 120; // 2 min cap

function getMostFrequent(data: CalendarData) {
  const counts: Record<string, number> = {};
  Object.values(data).forEach(e => { counts[e.dominant_emotion] = (counts[e.dominant_emotion] || 0) + 1; });
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return top ? top[0] : null;
}

// Convert blob to base64 data URL
function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export default function CalendarPage() {
  const { user } = useAuthStore();
  const companion = getCompanion(user?.personality);
  const router = useRouter();

  const [currentDate, setCurrentDate] = useState(new Date());
  const [data, setData] = useState<CalendarData>({});
  const [direction, setDirection] = useState(0);
  const [streak, setStreak] = useState<number>(0);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState<"write" | "voice">("write");

  // Write tab
  const [newTitle, setNewTitle] = useState("");
  const [newText, setNewText]   = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const titleRef = useRef<HTMLInputElement>(null);

  // Voice memo tab — actual audio recording (no transcription)
  const [isRecording, setIsRecording]     = useState(false);
  const [audioDataUrl, setAudioDataUrl]   = useState<string | null>(null);
  const [voiceTitle, setVoiceTitle]       = useState("");
  const [voiceError, setVoiceError]       = useState("");
  const [recordSecs, setRecordSecs]       = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef        = useRef<MediaStream | null>(null);
  const chunksRef        = useRef<Blob[]>([]);
  const timerRef         = useRef<ReturnType<typeof setInterval> | null>(null);

  // Playback modal state
  const [playingEntry, setPlayingEntry] = useState<{ id: string; audioUrl: string | null; title: string; emotion: string; isVoice: boolean; text?: string } | null>(null);
  const [playbackLoading, setPlaybackLoading]   = useState(false);
  const [insights, setInsights]                 = useState<{ insight: string; suggestions: string[]; affirmation: string; transcript?: string; source?: string } | null>(null);
  const [insightsLoading, setInsightsLoading]   = useState(false);
  const [goalsUpdated, setGoalsUpdated]         = useState(false);
  const [goalsUpdating, setGoalsUpdating]       = useState(false);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    loadCalendar();
  }, [currentDate]);

  useEffect(() => {
    getStreak()
      .then(res => setStreak(res?.streak ?? 0))
      .catch(() => setStreak(user?.streak ?? 0));
  }, [user?.streak]);

  useEffect(() => {
    if (showModal) {
      setTimeout(() => titleRef.current?.focus(), 50);
    } else {
      stopRecording();
      setAudioDataUrl(null);
      setVoiceTitle("");
      setVoiceError("");
      setNewTitle("");
      setNewText("");
      setRecordSecs(0);
      setActiveTab("write");
    }
  }, [showModal]);

  const loadCalendar = async () => {
    try {
      const result = await fetchCalendarData(currentDate.getFullYear(), currentDate.getMonth() + 1);
      setData(result || {});
    } catch { setData({}); }
  };

  const navigate = (dir: number) => {
    setDirection(dir);
    setCurrentDate(d => new Date(d.getFullYear(), d.getMonth() + dir, 1));
  };

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDay = new Date(year, month, 1).getDay();
  const monthName = currentDate.toLocaleString("default", { month: "long" });
  const today = new Date();
  const isCurrentMonth = today.getMonth() === month && today.getFullYear() === year;
  const entryCount = Object.keys(data).length;
  const topEmotion = getMostFrequent(data);

  // ── Write save ─────────────────────────────────────────────────────────────
  const handleSaveWrite = async () => {
    if (!newTitle.trim() || !newText.trim()) return;
    setIsSaving(true);
    try {
      await createJournalEntry(newText, newTitle);
      await loadCalendar();
      setShowModal(false);
    } catch (e) { console.error(e); }
    finally { setIsSaving(false); }
  };

  // ── Voice memo save ────────────────────────────────────────────────────────
  const handleSaveVoice = async () => {
    if (!audioDataUrl) return;
    setIsSaving(true);
    const title = voiceTitle.trim() || `Voice Memo – ${new Date().toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}`;
    const text = `VOICE_MEMO::${audioDataUrl}`;
    try {
      await createJournalEntry(text, title);
      await loadCalendar();
      setShowModal(false);
    } catch (e) { console.error(e); }
    finally { setIsSaving(false); }
  };

  // ── Audio recorder ─────────────────────────────────────────────────────────
  const stopRecording = useCallback(() => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
    mediaRecorderRef.current = null;
    setIsRecording(false);
  }, []);

  const startRecording = async () => {
    setVoiceError("");
    setAudioDataUrl(null);
    setRecordSecs(0);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Pick supported mime type
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/ogg";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const dataUrl = await blobToDataUrl(blob);
        setAudioDataUrl(dataUrl);
        if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
      };

      recorder.start(200); // collect chunks every 200ms
      setIsRecording(true);

      // Timer + auto-stop at max duration
      timerRef.current = setInterval(() => {
        setRecordSecs(s => {
          if (s + 1 >= MAX_RECORD_SECS) {
            stopRecording();
            return MAX_RECORD_SECS;
          }
          return s + 1;
        });
      }, 1000);

    } catch {
      setVoiceError("Couldn't access microphone — please allow mic permissions and try again.");
    }
  };

  const toggleRecording = () => { if (isRecording) stopRecording(); else startRecording(); };

  const formatTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  // ── Click calendar day ─────────────────────────────────────────────────────
  const handleDayClick = async (day: number) => {
    const entry = data[String(day)];
    if (!entry) return;
    setPlaybackLoading(true);
    setInsights(null);
    setGoalsUpdated(false);
    try {
      const full = await fetchJournalEntry(entry.id);
      const MARKER = "VOICE_MEMO::";
      if (full.text.startsWith(MARKER)) {
        const audioUrl = full.text.slice(MARKER.length);
        setPlayingEntry({ id: entry.id, audioUrl, title: full.title ?? "Voice Memo", emotion: entry.dominant_emotion, isVoice: true });
      } else {
        setPlayingEntry({ id: entry.id, audioUrl: null, title: full.title ?? "Journal Entry", emotion: entry.dominant_emotion, isVoice: false, text: full.text });
      }
    } catch { /* ignore */ }
    finally { setPlaybackLoading(false); }
  };

  const handleViewInsights = async () => {
    if (!playingEntry || insightsLoading) return;
    setInsightsLoading(true);
    try {
      const result = await getEntryInsights(playingEntry.id);
      setInsights(result);
    } catch { /* ignore */ }
    finally { setInsightsLoading(false); }
  };

  const handleLearnMore = () => {
    if (!playingEntry || !insights) return;
    sessionStorage.setItem("emora_chat_context", JSON.stringify({
      entryTitle: playingEntry.title,
      emotion: playingEntry.emotion,
      insight: insights.insight,
      therapyFocus: (insights as any).therapy_focus ?? "",
    }));
    router.push("/chat");
  };

  const handleUpdateGoals = async () => {
    if (!playingEntry || goalsUpdating || goalsUpdated) return;
    setGoalsUpdating(true);
    try {
      await generateEmotionGoals(playingEntry.emotion, playingEntry.title);
      setGoalsUpdated(true);
    } catch { /* ignore */ }
    finally { setGoalsUpdating(false); }
  };

  const variants = {
    enter: (d: number) => ({ x: d > 0 ? 60 : -60, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit:  (d: number) => ({ x: d > 0 ? -60 : 60, opacity: 0 }),
  };

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 h-full">

      {/* ── Header ── */}
      <header className="flex items-end justify-between shrink-0">
        <div>
          <h1 className="text-3xl font-semibold text-foreground mb-1">Journal Calendar</h1>
          <p className="text-on-surface-variant text-sm">Your emotional landscape, one day at a time.</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-primary-container hover:bg-primary-container/80 text-foreground font-medium py-2.5 px-5 rounded-full text-sm transition-all shadow-lg shadow-primary-container/20"
        >
          <Plus className="w-4 h-4" /> New Entry
        </motion.button>
      </header>

      {/* ── Stats Row ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 shrink-0">
        <div className="glass-panel relative rounded-2xl p-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/8 to-transparent" />
          <p className="text-2xl font-bold text-primary">{entryCount}</p>
          <p className="text-xs text-on-surface-variant mt-0.5">Entries this month</p>
        </div>
        <div className="glass-panel relative rounded-2xl p-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-orange-500/8 to-transparent" />
          <div className="flex items-center gap-2 mb-0.5">
            <Flame className="w-4 h-4 text-orange-400" />
            <p className="text-2xl font-bold text-orange-400">{streak}</p>
          </div>
          <p className="text-xs text-on-surface-variant">Day streak</p>
        </div>
        <div className="glass-panel relative rounded-2xl p-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-secondary/8 to-transparent" />
          {topEmotion ? (
            <>
              <div className="flex items-center gap-2 mb-0.5">
                <div className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: EMOTION_META[topEmotion]?.color }} />
                <p className="text-sm font-semibold text-foreground capitalize">{EMOTION_META[topEmotion]?.label}</p>
              </div>
              <p className="text-xs text-on-surface-variant">Top emotion</p>
            </>
          ) : <p className="text-xs text-on-surface-variant mt-1">No entries yet</p>}
        </div>
        <div className="glass-panel relative rounded-2xl p-4 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-tertiary/8 to-transparent" />
          <p className="text-[10px] font-medium text-on-surface-variant mb-2 uppercase tracking-wider">Emotions</p>
          <div className="flex flex-wrap gap-x-2 gap-y-1">
            {Object.entries(EMOTION_META).map(([key, { label, color }]) => (
              <div key={key} className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color, boxShadow: `0 0 4px ${color}` }} />
                <span className="text-[10px] text-on-surface-variant">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Calendar Card ── */}
      <div className="glass-panel relative flex-1 rounded-[28px] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between px-8 pt-6 pb-4 shrink-0 border-b border-white/5">
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => navigate(-1)}
            className="w-9 h-9 rounded-full border border-white/10 hover:border-white/25 hover:bg-white/5 flex items-center justify-center transition-all">
            <ChevronLeft className="w-4 h-4 text-on-surface-variant" />
          </motion.button>
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div key={`${monthName}-${year}`} custom={direction} variants={variants}
              initial="enter" animate="center" exit="exit"
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }} className="text-center">
              <h2 className="text-xl font-semibold text-foreground">{monthName}</h2>
              <p className="text-xs text-on-surface-variant">{year}</p>
            </motion.div>
          </AnimatePresence>
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }} onClick={() => navigate(1)}
            className="w-9 h-9 rounded-full border border-white/10 hover:border-white/25 hover:bg-white/5 flex items-center justify-center transition-all">
            <ChevronRight className="w-4 h-4 text-on-surface-variant" />
          </motion.button>
        </div>

        <div className="grid grid-cols-7 px-4 pt-4 pb-2 shrink-0">
          {DAY_LABELS.map(d => (
            <div key={d} className="text-center text-[11px] font-semibold text-on-surface-variant/60 uppercase tracking-wider">{d}</div>
          ))}
        </div>

        <AnimatePresence mode="wait" custom={direction}>
          <motion.div key={`grid-${monthName}-${year}`} custom={direction} variants={variants}
            initial="enter" animate="center" exit="exit"
            transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            className="grid grid-cols-7 gap-1.5 px-4 pb-5 flex-1">
            {Array.from({ length: firstDay }).map((_, i) => <div key={`e-${i}`} className="rounded-xl min-h-[56px]" />)}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1;
              const entry = data[String(day)];
              const isToday = isCurrentMonth && today.getDate() === day;
              const emotionColor = entry ? EMOTION_META[entry.dominant_emotion]?.color ?? "#94a3b8" : null;
              const isVoice = entry?.is_voice_memo;

              return (
                <motion.div key={day}
                  whileHover={{ scale: 1.06, zIndex: 10 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => entry && !playbackLoading && handleDayClick(day)}
                  className={cn("relative rounded-xl min-h-[56px] p-2 overflow-hidden border transition-colors",
                    entry ? (playbackLoading ? "cursor-wait" : "cursor-pointer") : "cursor-default")}
                  style={{
                    borderColor: isToday ? "rgba(205,189,255,0.5)" : entry ? `${emotionColor}30` : "rgba(255,255,255,0.05)",
                    backgroundColor: entry ? `${emotionColor}12` : isToday ? "rgba(205,189,255,0.06)" : "rgba(255,255,255,0.02)",
                    boxShadow: isToday ? "0 0 0 1.5px rgba(205,189,255,0.35), 0 0 16px rgba(205,189,255,0.12)" : "none",
                  }}>
                  <span className={`text-xs font-semibold leading-none ${isToday ? "text-primary" : entry ? "text-foreground/80" : "text-on-surface-variant/50"}`}>
                    {day}
                  </span>
                  {entry && (
                    <div className="absolute bottom-2 left-1/2 -translate-x-1/2">
                      {isVoice ? (
                        <div className="w-4 h-4 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: `${companion.color}30` }}>
                          <Mic className="w-2.5 h-2.5" style={{ color: companion.color }} />
                        </div>
                      ) : (
                        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                          transition={{ delay: i * 0.01, type: "spring", stiffness: 300 }}
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: emotionColor!, boxShadow: `0 0 8px ${emotionColor}, 0 0 14px ${emotionColor}60` }} />
                      )}
                    </div>
                  )}
                  {isToday && (
                    <motion.div className="absolute inset-0 rounded-xl border border-primary/30"
                      animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 2.5 }} />
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* ── Voice Memo Playback Modal ── */}
      <AnimatePresence>
        {playingEntry && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40" onClick={() => { setPlayingEntry(null); setInsights(null); setGoalsUpdated(false); }} />
            <motion.div
              key="playback-wrapper"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 flex items-center justify-center z-50 p-4 pointer-events-none"
            >
            <motion.div
              initial={{ scale: 0.92, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.93, y: 16 }}
              transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
              className="w-full max-w-lg glass-panel rounded-[28px] p-7 overflow-y-auto max-h-[90vh] pointer-events-auto"
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
                    style={{ background: `${companion.color}20`, border: `1.5px solid ${companion.color}40` }}>
                    {playingEntry.isVoice
                      ? <Mic className="w-5 h-5" style={{ color: companion.color }} />
                      : <BookOpen className="w-5 h-5" style={{ color: companion.color }} />}
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-foreground leading-tight">{playingEntry.title}</h3>
                    <p className="text-xs text-on-surface-variant capitalize">
                      {playingEntry.isVoice ? "Voice Memo" : "Journal Entry"} · {playingEntry.emotion}
                    </p>
                  </div>
                </div>
                <button onClick={() => { setPlayingEntry(null); setInsights(null); setGoalsUpdated(false); }}
                  className="w-8 h-8 rounded-full hover:bg-white/8 flex items-center justify-center text-on-surface-variant hover:text-foreground transition-colors shrink-0">
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Audio player or text preview */}
              {playingEntry.isVoice && playingEntry.audioUrl ? (
                <div className="rounded-2xl border p-4 mb-4" style={{ borderColor: `${companion.color}25`, background: `${companion.color}08` }}>
                  <audio src={playingEntry.audioUrl} controls autoPlay className="w-full" style={{ accentColor: companion.color }} />
                </div>
              ) : (
                <div className="rounded-2xl border p-4 mb-4 max-h-36 overflow-y-auto" style={{ borderColor: `${companion.color}25`, background: `${companion.color}08` }}>
                  <p className="text-sm leading-relaxed" style={{ color: "rgba(226,232,255,0.8)" }}>{playingEntry.text}</p>
                </div>
              )}

              {/* Action buttons */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <motion.button
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={handleViewInsights}
                  disabled={insightsLoading}
                  className="flex items-center justify-center gap-2 rounded-2xl py-3 px-4 text-sm font-semibold transition-all border disabled:opacity-60"
                  style={{ background: insights ? `${companion.color}18` : "rgba(255,255,255,0.04)", borderColor: `${companion.color}30`, color: companion.color }}>
                  {insightsLoading ? (
                    <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                      className="w-4 h-4 border-2 rounded-full inline-block" style={{ borderColor: `${companion.color}40`, borderTopColor: companion.color }} />
                  ) : (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.347.347a8 8 0 00-.923 1.335A4.978 4.978 0 0112 17a4.978 4.978 0 01-2.165-.468 8.004 8.004 0 00-.923-1.335l-.347-.347z" />
                    </svg>
                  )}
                  {insights ? "Insights" : "View Insights"}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                  onClick={handleUpdateGoals}
                  disabled={goalsUpdating || goalsUpdated}
                  className="flex items-center justify-center gap-2 rounded-2xl py-3 px-4 text-sm font-semibold transition-all border disabled:opacity-60"
                  style={{
                    background: goalsUpdated ? "rgba(74,222,128,0.12)" : "rgba(255,255,255,0.04)",
                    borderColor: goalsUpdated ? "rgba(74,222,128,0.3)" : "rgba(255,255,255,0.1)",
                    color: goalsUpdated ? "#4ade80" : "rgba(255,255,255,0.6)",
                  }}>
                  {goalsUpdating ? (
                    <motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                      className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full inline-block" />
                  ) : goalsUpdated ? (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  )}
                  {goalsUpdated ? "Goals Created!" : "Create Today's Goals"}
                </motion.button>
              </div>

              {/* Insights panel */}
              <AnimatePresence>
                {insights && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                    className="overflow-hidden">
                    <div className="rounded-2xl border p-5 space-y-4" style={{ borderColor: `${companion.color}20`, background: `${companion.color}06` }}>
                      {/* Show transcript for voice memos so user can verify what Whisper heard */}
                      {insights.transcript && (
                        <div className="rounded-xl p-3 border border-white/8 bg-white/[0.03]">
                          <p className="text-[10px] font-semibold uppercase tracking-wider text-white/35 mb-1.5">What I heard</p>
                          <p className="text-xs text-foreground/55 leading-relaxed italic">"{insights.transcript}"</p>
                        </div>
                      )}
                      <p className="text-sm text-foreground/85 leading-relaxed">{insights.insight}</p>

                      <div className="space-y-2">
                        <p className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: companion.color }}>Suggestions</p>
                        {insights.suggestions.map((s, i) => (
                          <div key={i} className="flex items-start gap-2.5">
                            <div className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ backgroundColor: companion.color }} />
                            <p className="text-sm text-foreground/70 leading-relaxed">{s}</p>
                          </div>
                        ))}
                      </div>

                      <div className="rounded-xl p-3 text-center" style={{ background: `${companion.color}12` }}>
                        <p className="text-sm italic" style={{ color: companion.color }}>"{insights.affirmation}"</p>
                      </div>

                      {/* Learn More button */}
                      <motion.button
                        whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                        onClick={handleLearnMore}
                        className="w-full flex items-center justify-center gap-2 rounded-2xl py-3 text-sm font-semibold transition-all border mt-1"
                        style={{ background: `${companion.color}15`, borderColor: `${companion.color}40`, color: companion.color }}
                      >
                        <MessageCircle className="w-4 h-4" />
                        Continue this in Chat with {companion.name}
                      </motion.button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {goalsUpdated && (
                <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-center text-green-400/70 mt-2">
                  2 goals created on your Goals page, tailored to today's emotional state.
                </motion.p>
              )}
            </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* ── New Entry Modal ── */}
      <AnimatePresence>
        {showModal && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={() => setShowModal(false)} />
              <motion.div
                key="entry-wrapper"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 flex items-center justify-center z-50 p-4 pointer-events-none"
              >
              <motion.div
                initial={{ scale: 0.92, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.93, y: 16 }}
                transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
                className="w-full max-w-lg glass-panel rounded-[28px] p-8 overflow-y-auto max-h-[90vh] pointer-events-auto"
              >
              <div className="absolute -top-10 right-0 w-32 h-32 rounded-full blur-[40px] pointer-events-none opacity-30"
                style={{ background: companion.color }} />

              <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center border"
                    style={{ background: `${companion.color}18`, borderColor: `${companion.color}35` }}>
                    <BookOpen className="w-4 h-4" style={{ color: companion.color }} />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">New Journal Entry</h3>
                </div>
                <button onClick={() => setShowModal(false)}
                  className="w-8 h-8 rounded-full hover:bg-white/8 flex items-center justify-center text-on-surface-variant hover:text-foreground transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 mb-5 p-1 rounded-xl bg-white/[0.04] border border-white/[0.06]">
                {([["write", "Write", PenLine], ["voice", "Voice Memo", Mic]] as const).map(([id, label, Icon]) => (
                  <button key={id} onClick={() => setActiveTab(id)}
                    className={cn("flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                      activeTab === id ? "text-foreground" : "text-on-surface-variant hover:text-foreground/70")}
                    style={activeTab === id ? { background: `${companion.color}20`, color: companion.color, boxShadow: `0 0 12px ${companion.color}30` } : {}}>
                    <Icon className="w-3.5 h-3.5" />{label}
                  </button>
                ))}
              </div>

              <AnimatePresence mode="wait">
                {/* ── Write Tab ── */}
                {activeTab === "write" && (
                  <motion.div key="write" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: 0.18 }} className="space-y-3">
                    <input ref={titleRef} type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)}
                      placeholder="Entry title…" className="input-glass pl-5 text-sm" />
                    <textarea value={newText} onChange={e => setNewText(e.target.value)}
                      placeholder="What's on your mind today? Write freely…" rows={5}
                      className="w-full bg-surface-container-high border border-white/10 rounded-2xl py-3.5 px-5 text-foreground placeholder:text-outline/60 text-sm focus:outline-none focus:border-primary/50 transition-all duration-200 resize-none" />
                    <button onClick={handleSaveWrite} disabled={isSaving || !newTitle.trim() || !newText.trim()}
                      className="w-full bg-primary-container hover:bg-primary-container/80 text-foreground font-semibold rounded-full py-3.5 transition-all duration-200 disabled:opacity-50 shadow-lg shadow-primary-container/20 hover:-translate-y-0.5 active:translate-y-0">
                      {isSaving ? "Saving…" : "Save Entry"}
                    </button>
                  </motion.div>
                )}

                {/* ── Voice Memo Tab ── */}
                {activeTab === "voice" && (
                  <motion.div key="voice" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }} transition={{ duration: 0.18 }} className="space-y-4">
                    <input type="text" value={voiceTitle} onChange={e => setVoiceTitle(e.target.value)}
                      placeholder="Memo title (optional)…" className="input-glass pl-5 text-sm" />

                    {/* Recorder UI */}
                    <div className="flex flex-col items-center gap-4 py-2">
                      <div className="relative flex items-center justify-center w-24 h-24">
                        {isRecording && (
                          <>
                            <motion.div className="absolute inset-0 rounded-full border-2"
                              style={{ borderColor: companion.color }}
                              animate={{ scale: [1, 1.35], opacity: [0.7, 0] }}
                              transition={{ duration: 0.9, repeat: Infinity, ease: "easeOut" }} />
                            <motion.div className="absolute inset-0 rounded-full border"
                              style={{ borderColor: companion.color }}
                              animate={{ scale: [1, 1.6], opacity: [0.4, 0] }}
                              transition={{ duration: 1.2, repeat: Infinity, ease: "easeOut", delay: 0.25 }} />
                          </>
                        )}
                        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                          onClick={toggleRecording}
                          className="relative w-20 h-20 rounded-full flex items-center justify-center z-10 transition-all duration-300"
                          style={{
                            background: isRecording
                              ? `linear-gradient(135deg, #ef4444cc, #dc2626aa)`
                              : audioDataUrl
                              ? `linear-gradient(135deg, ${companion.color}cc, ${companion.color}88)`
                              : "rgba(255,255,255,0.07)",
                            border: `2px solid ${isRecording ? "#ef4444" : audioDataUrl ? companion.color : "rgba(255,255,255,0.15)"}`,
                            boxShadow: isRecording ? "0 0 28px rgba(239,68,68,0.5)" : audioDataUrl ? `0 0 24px ${companion.color}50` : "none",
                          }}>
                          {isRecording
                            ? <Square className="w-7 h-7 text-white fill-white" />
                            : <Mic className="w-7 h-7 text-white/70" />
                          }
                        </motion.button>
                      </div>

                      {/* Timer / waveform bars */}
                      {isRecording && (
                        <div className="flex flex-col items-center gap-2">
                          <div className="flex items-center gap-0.5 h-7">
                            {Array.from({ length: 22 }).map((_, i) => (
                              <motion.div key={i} className="w-1 rounded-full" style={{ backgroundColor: companion.color }}
                                animate={{ height: [3, Math.random() * 22 + 3, 3] }}
                                transition={{ duration: 0.35 + Math.random() * 0.3, repeat: Infinity, ease: "easeInOut", delay: i * 0.04 }} />
                            ))}
                          </div>
                          <p className="text-xs font-mono tabular-nums" style={{ color: companion.color }}>
                            {formatTime(recordSecs)} / {formatTime(MAX_RECORD_SECS)}
                          </p>
                        </div>
                      )}

                      {!isRecording && !audioDataUrl && (
                        <p className="text-xs text-on-surface-variant text-center">
                          Tap the mic to start recording your voice memo
                        </p>
                      )}

                      {!isRecording && audioDataUrl && (
                        <p className="text-xs text-center" style={{ color: companion.color }}>
                          Recording ready · {formatTime(recordSecs)} · Tap mic to re-record
                        </p>
                      )}
                    </div>

                    {voiceError && <p className="text-xs text-red-400 text-center">{voiceError}</p>}

                    {/* Native audio player for preview */}
                    {audioDataUrl && !isRecording && (
                      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
                        className="w-full rounded-2xl border p-3" style={{ borderColor: `${companion.color}25`, background: `${companion.color}08` }}>
                        <p className="text-[11px] text-white/40 mb-2 text-center uppercase tracking-wider">Preview</p>
                        <audio ref={audioPlayerRef} src={audioDataUrl} controls
                          className="w-full h-10 rounded-xl" style={{ accentColor: companion.color }} />
                      </motion.div>
                    )}

                    <button onClick={handleSaveVoice} disabled={isSaving || !audioDataUrl}
                      className="w-full font-semibold rounded-full py-3.5 transition-all duration-200 disabled:opacity-40 hover:-translate-y-0.5 active:translate-y-0"
                      style={{
                        background: audioDataUrl ? `linear-gradient(135deg, ${companion.color}cc, ${companion.color}88)` : "rgba(255,255,255,0.06)",
                        color: audioDataUrl ? "white" : "rgba(255,255,255,0.3)",
                        boxShadow: audioDataUrl ? `0 4px 20px ${companion.color}40` : "none",
                      }}>
                      {isSaving ? "Saving…" : "Save Voice Memo"}
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
