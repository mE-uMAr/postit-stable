"use client";

import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "./client";

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  setData: (value: T | null) => void;
}

/** Minimal fetch-on-mount hook. Pass `null` as the path to skip fetching. */
export function useApi<T>(path: string | null): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(path !== null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (path === null) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setData(await api.get<T>(path));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load.");
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, loading, error, reload: load, setData };
}

export function errorMessage(e: unknown): string {
  return e instanceof ApiError ? e.message : "Something went wrong.";
}
