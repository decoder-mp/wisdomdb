import { isAxiosError } from "axios";

type ValidationItem = {
  field?: string;
  message?: string;
};

export function getApiErrorMessage(
  error: unknown,
  fallbackMessage: string,
): string {
  if (!error) {
    return fallbackMessage;
  }

  if (isAxiosError(error)) {
    if (!error.response) {
      return "Cannot reach backend API. Make sure FastAPI is running on http://127.0.0.1:8000.";
    }

    const detail = error.response.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as ValidationItem;
      if (typeof first?.message === "string") {
        return first.message;
      }
    }

    if (typeof error.message === "string" && error.message.length > 0) {
      return error.message;
    }
  }

  return fallbackMessage;
}
