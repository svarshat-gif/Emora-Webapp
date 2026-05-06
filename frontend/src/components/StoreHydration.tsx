"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import { setTokens } from "@/lib/api/client";

export function StoreHydration() {
  useEffect(() => {
    useAuthStore.persist.rehydrate();
    // Sync localStorage tokens → cookies so middleware can read them
    const access = localStorage.getItem("access_token");
    const refresh = localStorage.getItem("refresh_token");
    if (access && refresh) setTokens(access, refresh);
  }, []);

  return null;
}
