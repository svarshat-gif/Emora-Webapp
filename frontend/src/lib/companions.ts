export const COMPANIONS = {
  sera: {
    name: "Sera",
    title: "Calm & Empathetic",
    description: "A gentle therapist who meets you where you are",
    color: "#a78bfa",
    glow: "rgba(167,139,250,0.5)",
    glowSoft: "rgba(167,139,250,0.2)",
    gradient: "from-violet-400 via-purple-500 to-violet-700",
    borderClass: "border-violet-400/30",
    bgClass: "bg-violet-400/10",
    textClass: "text-violet-300",
    greeting: (name: string) =>
      `Hi ${name}. I'm here with you. How are you feeling today?`,
  },
  motivator: {
    name: "Blaze",
    title: "Energetic & Uplifting",
    description: "Your personal coach who builds confidence",
    color: "#fb923c",
    glow: "rgba(251,146,60,0.5)",
    glowSoft: "rgba(251,146,60,0.2)",
    gradient: "from-amber-400 via-orange-500 to-red-500",
    borderClass: "border-amber-400/30",
    bgClass: "bg-amber-400/10",
    textClass: "text-amber-300",
    greeting: (name: string) =>
      `Hey ${name}! Ready to make today incredible? What's on your mind?`,
  },
  rational: {
    name: "Nova",
    title: "Logical & Analytical",
    description: "A clear-headed guide for structured thinking",
    color: "#22d3ee",
    glow: "rgba(34,211,238,0.5)",
    glowSoft: "rgba(34,211,238,0.2)",
    gradient: "from-cyan-400 via-teal-500 to-blue-600",
    borderClass: "border-cyan-400/30",
    bgClass: "bg-cyan-400/10",
    textClass: "text-cyan-300",
    greeting: (name: string) =>
      `Hello ${name}. Let's take a clear look at what's on your mind today.`,
  },
  luna: {
    name: "Luna",
    title: "Warm & Supportive",
    description: "A warm best friend who truly gets you",
    color: "#f472b6",
    glow: "rgba(244,114,182,0.5)",
    glowSoft: "rgba(244,114,182,0.2)",
    gradient: "from-pink-400 via-rose-500 to-pink-600",
    borderClass: "border-pink-400/30",
    bgClass: "bg-pink-400/10",
    textClass: "text-pink-300",
    greeting: (name: string) =>
      `Hey ${name}! So happy you're here. How's your heart today?`,
  },
} as const;

export type CompanionKey = keyof typeof COMPANIONS;

export function getCompanion(personality?: string | null) {
  const key = (personality ?? "sera") as CompanionKey;
  return COMPANIONS[key] ?? COMPANIONS.sera;
}
