import { apiClient } from "./client";
import type { JournalEntry, ApiResponse } from "@/types";

export async function createEntry(text: string, title?: string): Promise<JournalEntry> {
  const { data } = await apiClient.post<ApiResponse<JournalEntry>>("/journal/create", { text, title });
  return data.data;
}

export async function getEntries(limit = 20, offset = 0): Promise<JournalEntry[]> {
  const { data } = await apiClient.get<ApiResponse<JournalEntry[]>>("/journal/entries", { params: { limit, offset } });
  return data.data;
}

export async function getEntry(id: string): Promise<JournalEntry> {
  const { data } = await apiClient.get<ApiResponse<JournalEntry>>(`/journal/${id}`);
  return data.data;
}

export async function updateEntry(id: string, updates: { text?: string; title?: string }): Promise<JournalEntry> {
  const { data } = await apiClient.put<ApiResponse<JournalEntry>>(`/journal/${id}`, updates);
  return data.data;
}

export async function deleteEntry(id: string): Promise<void> {
  await apiClient.delete(`/journal/${id}`);
}

export interface DayEntry { id: string; dominant_emotion: string; color: string; title?: string; is_voice_memo?: boolean }

export async function getCalendarData(year: number, month: number): Promise<Record<string, DayEntry>> {
  const { data } = await apiClient.get("/journal/calendar", { params: { year, month } });
  return data.data ?? {};
}

export async function getInsights(): Promise<object> {
  const { data } = await apiClient.get("/journal/insights");
  return data.data;
}

export async function getEntryInsights(id: string): Promise<{ insight: string; suggestions: string[]; affirmation: string }> {
  const { data } = await apiClient.get(`/journal/${id}/insights`);
  return data.data;
}
