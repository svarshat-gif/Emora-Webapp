"use client";
import { useChatStore } from "@/store/chatStore";

export function useChat() {
  const store = useChatStore();
  return store;
}
