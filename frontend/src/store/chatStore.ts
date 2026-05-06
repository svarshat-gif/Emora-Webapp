"use client";
import { create } from "zustand";
import type { ChatMessage, ChatSession, Personality } from "@/types";
import * as chatApi from "@/lib/api/chat";

interface ChatState {
  sessions: ChatSession[];
  messages: ChatMessage[];
  currentSessionId: string | null;
  personality: Personality;
  isLoading: boolean;
  isSending: boolean;
  setPersonality: (p: Personality) => void;
  loadSessions: () => Promise<void>;
  loadHistory: (sessionId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  newSession: () => void;
  deleteSession: (id: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  messages: [],
  currentSessionId: null,
  personality: "sera",
  isLoading: false,
  isSending: false,

  setPersonality: (personality) => set({ personality }),

  newSession: () => set({ currentSessionId: null, messages: [] }),

  loadSessions: async () => {
    set({ isLoading: true });
    try {
      const sessions = await chatApi.getSessions();
      set({ sessions });
    } finally {
      set({ isLoading: false });
    }
  },

  loadHistory: async (sessionId) => {
    set({ isLoading: true, currentSessionId: sessionId });
    try {
      const history = await chatApi.getSessionHistory(sessionId);
      const messages: ChatMessage[] = history.map((h: any) => ({
        id: h.id,
        session_id: sessionId,
        role: h.role,
        content: h.content,
        emotion: h.emotion,
        created_at: h.created_at,
      }));
      set({ messages });
    } finally {
      set({ isLoading: false });
    }
  },

  sendMessage: async (content) => {
    const { personality, currentSessionId, messages } = get();

    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: currentSessionId || "pending",
      role: "user",
      content,
      created_at: new Date().toISOString(),
    };
    set({ messages: [...messages, userMsg], isSending: true });

    try {
      const result = await chatApi.sendMessage(content, personality, currentSessionId || undefined);
      const aiMsg: ChatMessage = {
        id: result.message_id,
        session_id: result.session_id,
        role: "assistant",
        content: result.response,
        emotion: result.emotion as any,
        created_at: result.timestamp,
      };
      set((state) => ({
        messages: [...state.messages, aiMsg],
        currentSessionId: result.session_id,
      }));
      // Refresh sessions list
      chatApi.getSessions().then((sessions) => set({ sessions }));
    } finally {
      set({ isSending: false });
    }
  },

  deleteSession: async (id) => {
    await chatApi.deleteSession(id);
    const { currentSessionId } = get();
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== id),
      ...(currentSessionId === id ? { currentSessionId: null, messages: [] } : {}),
    }));
  },
}));
