import { apiClient } from "./client";
import type { ChatMessage, ChatSession, ApiResponse } from "@/types";

export interface SendMessageResponse {
  session_id: string;
  message_id: string;
  response: string;
  emotion: object;
  personality: string;
  timestamp: string;
}

export async function sendMessage(message: string, personality: string, sessionId?: string): Promise<SendMessageResponse> {
  const { data } = await apiClient.post<ApiResponse<SendMessageResponse>>("/chat/message", {
    message,
    personality,
    session_id: sessionId,
  });
  return data.data;
}

export async function getSessions(): Promise<ChatSession[]> {
  const { data } = await apiClient.get<ApiResponse<ChatSession[]>>("/chat/sessions");
  return data.data;
}

export async function getSessionHistory(sessionId: string): Promise<ChatMessage[]> {
  const { data } = await apiClient.get<ApiResponse<ChatMessage[]>>(`/chat/sessions/${sessionId}/history`);
  return data.data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/chat/sessions/${sessionId}`);
}
