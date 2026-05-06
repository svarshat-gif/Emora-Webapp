/** Extracts a human-readable message from an Axios or generic error. */
export function extractApiError(err: unknown, fallback = "Something went wrong. Please try again."): string {
  if (err && typeof err === "object") {
    // Axios error with a response from the server
    if ("response" in err) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = (err as any).response;
      const data = res?.data;
      const status = res?.status;

      // Field-level validation errors
      const detail: string | undefined = data?.details?.[0]?.message;
      if (detail) return detail.replace(/^Value error,\s*/i, "");

      if (data?.message) return data.message;

      // HTTP 401 with no body — wrong credentials
      if (status === 401) return fallback;
    }

    // Axios network error (no response received — server unreachable)
    if ("code" in err && (err as any).code === "ERR_NETWORK") {
      return "Cannot reach the server. Make sure the backend is running on port 8000.";
    }
  }
  if (err instanceof Error && err.message !== "Network Error") return err.message;
  if (err instanceof Error && err.message === "Network Error") {
    return "Cannot reach the server. Make sure the backend is running on port 8000.";
  }
  return fallback;
}
