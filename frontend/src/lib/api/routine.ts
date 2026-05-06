import { apiClient } from "./client";
import type { Routine, ApiResponse } from "@/types";

export async function generateRoutine(goals?: string[], currentMood?: string): Promise<Routine> {
  const { data } = await apiClient.post<ApiResponse<Routine>>("/routine/generate", {
    goals,
    current_mood: currentMood || "neutral",
  });
  return data.data;
}

export async function getTodayRoutine(): Promise<Routine | null> {
  const { data } = await apiClient.get<ApiResponse<Routine | null>>("/routine/today");
  return data.data;
}

export async function updateTask(routineId: string, taskId: string, completed: boolean): Promise<Routine> {
  const { data } = await apiClient.patch<ApiResponse<Routine>>(`/routine/${routineId}/task`, {
    task_id: taskId,
    completed,
  });
  return data.data;
}
