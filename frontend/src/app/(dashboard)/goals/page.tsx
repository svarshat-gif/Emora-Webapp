"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Circle, Target, Trophy, Plus, Sparkles, ChevronDown, ChevronUp, X, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { getGoals, createGoal } from "@/lib/api/goals";
import { getTodayRoutine, updateTask } from "@/lib/api/routine";
import { useAuthStore } from "@/store/authStore";
import { getCompanion } from "@/lib/companions";
import { cn } from "@/lib/utils";
import type { Goal, Routine, RoutineTask } from "@/types";

const GOAL_COLORS = ["#a78bfa", "#22d3ee", "#f472b6", "#fb923c", "#4ade80", "#60a5fa"];
const CATEGORY_LABELS: Record<string, string> = {
  mental_health: "Mental Health", physical: "Physical", social: "Social",
  career: "Career", personal: "Personal", spiritual: "Spiritual",
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.4, ease: [0.22, 1, 0.36, 1] } }),
};

type RoutineBlock = { label: string; tasks: RoutineTask[] };

function flattenRoutine(routine: Routine): RoutineBlock[] {
  return [
    { label: "Morning", tasks: routine.tasks.morning || [] },
    { label: "Afternoon", tasks: routine.tasks.afternoon || [] },
    { label: "Evening", tasks: routine.tasks.evening || [] },
  ].filter(b => b.tasks.length > 0);
}

export default function GoalsPage() {
  const { user } = useAuthStore();
  const companion = getCompanion(user?.personality);

  const [goals, setGoals]         = useState<Goal[]>([]);
  const [routine, setRoutine]     = useState<Routine | null>(null);
  const [loading, setLoading]     = useState(true);
  const [expandedGoal, setExpandedGoal] = useState<string | null>(null);

  // New goal modal
  const [showNewGoal, setShowNewGoal]   = useState(false);
  const [newTitle, setNewTitle]         = useState("");
  const [newDesc, setNewDesc]           = useState("");
  const [newCategory, setNewCategory]   = useState("personal");
  const [savingGoal, setSavingGoal]     = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [goalsData, routineData] = await Promise.all([
          getGoals("active").catch(() => [] as Goal[]),
          getTodayRoutine().catch(() => null),
        ]);
        setGoals(goalsData);
        setRoutine(routineData);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleToggleTask = async (taskId: string) => {
    if (!routine) return;
    const allTasks = [...(routine.tasks.morning || []), ...(routine.tasks.afternoon || []), ...(routine.tasks.evening || [])];
    const task = allTasks.find(t => t.id === taskId);
    if (!task) return;
    try {
      const updated = await updateTask(routine.id, taskId, !task.completed);
      setRoutine(updated);
    } catch { /* ignore */ }
  };

  const handleCreateGoal = async () => {
    if (!newTitle.trim()) return;
    setSavingGoal(true);
    try {
      const goal = await createGoal({ title: newTitle, description: newDesc, category: newCategory });
      setGoals(prev => [goal, ...prev]);
      setShowNewGoal(false);
      setNewTitle(""); setNewDesc(""); setNewCategory("personal");
    } catch { /* ignore */ }
    finally { setSavingGoal(false); }
  };

  const allTasks = routine ? [
    ...(routine.tasks.morning || []),
    ...(routine.tasks.afternoon || []),
    ...(routine.tasks.evening || []),
  ] : [];
  const completedCount = allTasks.filter(t => t.completed).length;
  const completionPct  = allTasks.length ? Math.round((completedCount / allTasks.length) * 100) : 0;
  const blocks = routine ? flattenRoutine(routine) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-on-surface-variant" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">

      {/* ── Header ── */}
      <motion.div custom={0} variants={fadeUp} initial="hidden" animate="show" className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: companion.color }}>
          Growth & Habits
        </p>
        <h1 className="text-3xl font-bold text-white">Goals & Routine</h1>
        <p className="text-white/40 text-sm mt-1">Small consistent actions create meaningful change.</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-5">

        {/* ── Daily Routine ── */}
        <motion.div custom={1} variants={fadeUp} initial="hidden" animate="show" className="md:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4" style={{ color: companion.color }} />
              <h2 className="text-sm font-semibold text-white">Today&apos;s Routine</h2>
            </div>
            {routine && (
              <span className="text-xs font-medium px-2.5 py-1 rounded-full"
                style={{ background: `${companion.color}15`, color: companion.color }}>
                {completedCount}/{allTasks.length} done
              </span>
            )}
          </div>

          {routine ? (
            <>
              {/* Progress bar */}
              <div className="h-1 rounded-full bg-white/[0.06] overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${completionPct}%` }}
                  transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                  className="h-full rounded-full"
                  style={{ background: `linear-gradient(90deg, ${companion.color}, ${companion.color}80)` }}
                />
              </div>

              {/* Tasks grouped by block */}
              <div className="space-y-3">
                {blocks.map(block => (
                  <div key={block.label} className="rounded-2xl border overflow-hidden divide-y"
                    style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.02)" }}>
                    <div className="px-5 py-2.5">
                      <p className="text-[10px] font-semibold uppercase tracking-wider text-white/30">{block.label}</p>
                    </div>
                    {block.tasks.map((task) => (
                      <motion.div
                        key={task.id}
                        className="flex items-center gap-4 px-5 py-3.5 cursor-pointer group transition-colors hover:bg-white/[0.03]"
                        style={{ borderColor: "rgba(255,255,255,0.04)" }}
                        onClick={() => handleToggleTask(task.id)}
                      >
                        <motion.div whileTap={{ scale: 0.85 }} className="shrink-0">
                          {task.completed ? (
                            <CheckCircle2 className="w-5 h-5" style={{ color: companion.color }} />
                          ) : (
                            <Circle className="w-5 h-5 text-white/20 group-hover:text-white/40 transition-colors" />
                          )}
                        </motion.div>
                        <div className="flex-1 min-w-0">
                          <p className={cn("text-sm transition-all truncate", task.completed ? "line-through text-white/25" : "text-white/75")}>
                            {task.task}
                          </p>
                          {task.time && (
                            <p className="text-[11px] text-white/30 mt-0.5">{task.time} · {task.duration}</p>
                          )}
                        </div>
                        {task.completed && (
                          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
                            style={{ background: `${companion.color}18`, color: companion.color }}>
                            Done
                          </motion.div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="rounded-2xl border p-8 text-center"
              style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.02)" }}>
              <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
                style={{ background: `${companion.color}15` }}>
                <Target className="w-6 h-6" style={{ color: companion.color }} />
              </div>
              <p className="text-sm font-medium text-white/60 mb-1">No routine for today yet</p>
              <p className="text-xs text-white/30">Ask {companion.name} in Chat to create a daily routine for you</p>
            </div>
          )}
        </motion.div>

        {/* ── Goals ── */}
        <motion.div custom={2} variants={fadeUp} initial="hidden" animate="show" className="md:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-semibold text-white">Active Goals</h2>
            </div>
            <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
              onClick={() => setShowNewGoal(true)}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-white/40 hover:text-white/80 hover:bg-white/[0.08] transition-all">
              <Plus className="w-4 h-4" />
            </motion.button>
          </div>

          {goals.length > 0 ? (
            <div className="space-y-3">
              {goals.map((goal, i) => {
                const color = GOAL_COLORS[i % GOAL_COLORS.length];
                const isExpanded = expandedGoal === goal.id;
                const milestones = goal.milestones || [];
                const doneMilestones = milestones.filter(m => m.completed).length;

                return (
                  <motion.div key={goal.id} layout
                    className="rounded-2xl border overflow-hidden"
                    style={{ background: `${color}08`, borderColor: `${color}20` }}>
                    <div className="p-4">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <h3 className="text-sm font-semibold text-white leading-tight flex-1">{goal.title}</h3>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-xs font-bold" style={{ color }}>{goal.progress}%</span>
                          {milestones.length > 0 && (
                            <button onClick={() => setExpandedGoal(isExpanded ? null : goal.id)}
                              className="text-white/30 hover:text-white/60 transition-colors">
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </button>
                          )}
                        </div>
                      </div>
                      {goal.description && (
                        <p className="text-[11px] text-white/35 mb-3 leading-tight line-clamp-2">{goal.description}</p>
                      )}
                      {goal.category && (
                        <p className="text-[10px] font-medium mb-2" style={{ color: `${color}99` }}>
                          {CATEGORY_LABELS[goal.category] ?? goal.category}
                        </p>
                      )}
                      <div className="h-1 rounded-full bg-white/[0.06] overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${goal.progress}%` }}
                          transition={{ duration: 1, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                          className="h-full rounded-full"
                          style={{ background: color, boxShadow: `0 0 8px ${color}80` }}
                        />
                      </div>
                      {milestones.length > 0 && (
                        <p className="text-[10px] text-white/25 mt-2">{doneMilestones}/{milestones.length} milestones</p>
                      )}
                    </div>

                    <AnimatePresence>
                      {isExpanded && milestones.length > 0 && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}
                          className="overflow-hidden border-t px-4 pb-4"
                          style={{ borderColor: `${color}18` }}>
                          <p className="text-[10px] font-semibold uppercase tracking-wider mt-3 mb-2" style={{ color: `${color}80` }}>Milestones</p>
                          <div className="space-y-2">
                            {milestones.map(m => (
                              <div key={m.id} className="flex items-start gap-2">
                                {m.completed
                                  ? <CheckCircle2 className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color }} />
                                  : <div className="w-3.5 h-3.5 mt-0.5 rounded-full border shrink-0" style={{ borderColor: `${color}50` }} />
                                }
                                <p className={cn("text-xs leading-tight", m.completed ? "text-white/30 line-through" : "text-white/60")}>{m.text}</p>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="rounded-2xl border p-6 text-center space-y-2"
              style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.02)" }}>
              <Trophy className="w-8 h-8 text-amber-400/40 mx-auto" />
              <p className="text-sm text-white/50">No active goals yet</p>
              <p className="text-xs text-white/25">Tap + to add one, or ask {companion.name} to create a schedule for you</p>
            </div>
          )}

          {/* Companion nudge */}
          <div className="rounded-2xl p-4 border" style={{ background: `${companion.color}07`, borderColor: `${companion.color}18` }}>
            <div className="flex items-center gap-2 mb-1.5">
              <Sparkles className="w-3.5 h-3.5" style={{ color: companion.color }} />
              <span className="text-[10px] font-semibold uppercase tracking-widest" style={{ color: companion.color }}>
                {companion.name} says
              </span>
            </div>
            <p className="text-xs text-white/45 leading-relaxed">
              Every small step counts. You&apos;re building something meaningful, one day at a time.
            </p>
          </div>
        </motion.div>
      </div>

      {/* ── New Goal Modal ── */}
      <AnimatePresence>
        {showNewGoal && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={() => setShowNewGoal(false)} />
            <motion.div
              initial={{ opacity: 0, scale: 0.92, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.93, y: 16 }} transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              className="fixed inset-x-4 bottom-4 md:inset-auto md:left-1/2 md:-translate-x-1/2 md:top-1/2 md:-translate-y-1/2 md:w-full md:max-w-md glass-panel rounded-[28px] p-7 z-50">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-base font-semibold text-foreground">New Goal</h3>
                <button onClick={() => setShowNewGoal(false)}
                  className="w-8 h-8 rounded-full hover:bg-white/8 flex items-center justify-center text-on-surface-variant hover:text-foreground transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-3">
                <input type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)}
                  placeholder="Goal title…" className="input-glass pl-5 text-sm" autoFocus />
                <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)}
                  placeholder="Description (optional)…" rows={3}
                  className="w-full bg-surface-container-high border border-white/10 rounded-2xl py-3.5 px-5 text-foreground placeholder:text-outline/60 text-sm focus:outline-none focus:border-primary/50 transition-all duration-200 resize-none" />
                <select value={newCategory} onChange={e => setNewCategory(e.target.value)}
                  className="w-full bg-surface-container-high border border-white/10 rounded-2xl py-3.5 px-5 text-foreground text-sm focus:outline-none focus:border-primary/50 transition-all duration-200 appearance-none">
                  {Object.entries(CATEGORY_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
                <button onClick={handleCreateGoal} disabled={savingGoal || !newTitle.trim()}
                  className="w-full bg-primary-container hover:bg-primary-container/80 text-foreground font-semibold rounded-full py-3.5 transition-all duration-200 disabled:opacity-50 shadow-lg shadow-primary-container/20 hover:-translate-y-0.5 active:translate-y-0">
                  {savingGoal ? "Saving…" : "Create Goal"}
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
