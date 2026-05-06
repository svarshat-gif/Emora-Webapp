export interface User {
  id: string;
  email: string;
  name: string;
  personality: "sera" | "motivator" | "rational" | "luna";
  bio?: string;
  avatar_url?: string;
  theme?: "dark" | "light" | "system";
  streak: number;
  total_entries: number;
  stats?: {
    journal_entries: number;
    goals_completed: number;
    chat_sessions: number;
    streak: number;
  };
  created_at: string;
}

export interface Emotion {
  dominant_emotion: "joy" | "sadness" | "anger" | "fear" | "disgust" | "surprise" | "neutral";
  confidence: number;
  all_emotions: Record<string, number>;
  color: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  emotion?: Emotion;
  created_at: string;
}

export interface ChatSession {
  id: string;
  personality: string;
  title: string;
  last_message?: string;
  created_at: string;
  updated_at: string;
}

export interface JournalEntry {
  id: string;
  user_id: string;
  title: string;
  text: string;
  emotion?: Emotion;
  created_at: string;
  updated_at: string;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  category: string;
  status: "active" | "completed" | "paused";
  progress: number;
  target_date?: string;
  milestones: Milestone[];
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: string;
  text: string;
  completed: boolean;
  order: number;
}

export interface RoutineTask {
  id: string;
  time: string;
  task: string;
  duration: string;
  category: string;
  completed: boolean;
}

export interface Routine {
  id: string;
  date: string;
  mood: string;
  tasks: {
    morning: RoutineTask[];
    afternoon: RoutineTask[];
    evening: RoutineTask[];
  };
  completion_rate: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  count?: number;
}

export type Personality = "sera" | "motivator" | "rational" | "luna";

export const EMOTION_COLORS: Record<string, string> = {
  joy: "#FFD700",
  sadness: "#4A90D9",
  anger: "#E74C3C",
  fear: "#9B59B6",
  disgust: "#27AE60",
  surprise: "#F39C12",
  neutral: "#95A5A6",
};

export const EMOTION_EMOJIS: Record<string, string> = {
  joy: "😊",
  sadness: "😢",
  anger: "😠",
  fear: "😨",
  disgust: "🤢",
  surprise: "😮",
  neutral: "😐",
};

export const PERSONALITY_INFO: Record<Personality, { name: string; description: string; icon: string }> = {
  sera:      { name: "Sera",  description: "Calm & empathetic therapist",  icon: "heart" },
  motivator: { name: "Blaze", description: "Energetic & uplifting coach",  icon: "zap"   },
  rational:  { name: "Nova",  description: "Logical & analytical guide",   icon: "brain" },
  luna:      { name: "Luna",  description: "Warm & supportive friend",     icon: "moon"  },
};
