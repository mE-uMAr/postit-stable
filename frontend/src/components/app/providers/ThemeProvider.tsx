"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type Theme = "light" | "dark";
type ThemeUpdater = Theme | ((prev: Theme) => Theme);

interface ThemeContextValue {
  theme: Theme;
  setTheme: (updater: ThemeUpdater) => void;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("light");

  // Sync from localStorage on mount (the no-flash script in the layout has
  // already applied the right attribute to <html>; this keeps React in step).
  useEffect(() => {
    try {
      const stored = localStorage.getItem("postit-theme");
      if (stored === "dark" || stored === "light") setThemeState(stored);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("postit-theme", theme);
    } catch {
      /* ignore */
    }
  }, [theme]);

  const setTheme = (updater: ThemeUpdater) =>
    setThemeState((prev) => (typeof updater === "function" ? updater(prev) : updater));
  const toggle = () => setThemeState((t) => (t === "dark" ? "light" : "dark"));

  return <ThemeContext.Provider value={{ theme, setTheme, toggle }}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within a ThemeProvider");
  return ctx;
}
