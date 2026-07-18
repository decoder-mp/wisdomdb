import { createContext, useContext, useMemo, useState } from "react";

function isTokenExpired(token: string) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1] ?? "")) as { exp?: number };
    if (!payload.exp) return false;
    return payload.exp * 1000 <= Date.now();
  } catch {
    return false;
  }
}

type AuthContextValue = {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => {
    const stored = localStorage.getItem("lore_access_token");
    if (!stored) return null;
    if (isTokenExpired(stored)) {
      localStorage.removeItem("lore_access_token");
      return null;
    }
    return stored;
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      isAuthenticated: Boolean(token),
      login: (nextToken: string) => {
        localStorage.setItem("lore_access_token", nextToken);
        localStorage.setItem("lore_session_started_at", new Date().toISOString());
        setToken(nextToken);
      },
      logout: () => {
        localStorage.removeItem("lore_access_token");
        localStorage.removeItem("lore_session_started_at");
        setToken(null);
      },
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
