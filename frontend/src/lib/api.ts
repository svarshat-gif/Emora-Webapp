const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  // In a real app, you would retrieve the JWT token from localStorage/cookies
  const token = (typeof window !== "undefined" && typeof window.document !== "undefined") ? window.localStorage.getItem("access_token") : null;
  
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || "An error occurred");
  }
  return data;
}

export const chatAPI = {
  sendMessage: async (message: string, personality = "sera", sessionId?: string) => {
    return fetchAPI("/chat/message", {
      method: "POST",
      body: JSON.stringify({ message, session_id: sessionId, personality }),
    });
  },
  getHistory: async (sessionId: string) => {
    return fetchAPI(`/chat/sessions/${sessionId}/history`);
  }
};

export const journalAPI = {
  getCalendarData: async (year: number, month: number) => {
    return fetchAPI(`/journal/calendar?year=${year}&month=${month}`);
  },
  createEntry: async (title: string, text: string) => {
    return fetchAPI("/journal/create", {
      method: "POST",
      body: JSON.stringify({ title, text }),
    });
  }
};

export const goalsAPI = {
  getGoals: async () => fetchAPI("/goals/"),
  getRoutine: async () => fetchAPI("/routine/"),
  createGoal: async (title: string, description: string, milestones: string[]) =>
    fetchAPI("/goals/create", {
      method: "POST",
      body: JSON.stringify({ title, description, milestones }),
    }),
};

export const profileAPI = {
  getStreak: async () => fetchAPI("/profile/streak"),
};
