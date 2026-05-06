import { apiClient } from "./client";
import type { Goal, ApiResponse } from "@/types";

export async function createGoal(payload: {
  title: string;
  description?: string;
  category?: string;
  target_date?: string;
  milestones?: string[];
}): Promise<Goal> {
  const { data } = await apiClient.post<ApiResponse<Goal>>("/goals/create", payload);
  return data.data;
}

export async function getGoals(status?: string): Promise<Goal[]> {
  const { data } = await apiClient.get<ApiResponse<Goal[]>>("/goals", { params: status ? { status } : {} });
  return data.data;
}

export async function updateGoal(id: string, updates: Partial<Goal>): Promise<Goal> {
  const { data } = await apiClient.put<ApiResponse<Goal>>(`/goals/${id}`, updates);
  return data.data;
}

export async function updateMilestone(goalId: string, milestoneId: string, completed: boolean): Promise<Goal> {
  const { data } = await apiClient.patch<ApiResponse<Goal>>(`/goals/${goalId}/milestone`, {
    milestone_id: milestoneId,
    completed,
  });
  return data.data;
}

export async function deleteGoal(id: string): Promise<void> {
  await apiClient.delete(`/goals/${id}`);
}

export async function generateEmotionGoals(emotion: string, memoTitle: string): Promise<Goal[]> {
  const { data } = await apiClient.post<ApiResponse<Goal[]>>("/goals/from-emotion", { emotion, memo_title: memoTitle });
  return data.data;
}
