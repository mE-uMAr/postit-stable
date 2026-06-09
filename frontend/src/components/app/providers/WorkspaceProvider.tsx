"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api, ApiError } from "@/lib/api/client";
import type { ApiSubscription, ApiWorkspace } from "@/lib/api/types";

export type WorkspaceRole = "viewer" | "editor" | "admin" | "owner";

const RANK: Record<WorkspaceRole, number> = { viewer: 1, editor: 2, admin: 3, owner: 4 };

interface WorkspaceContextValue {
  workspace: ApiWorkspace | null;
  role: WorkspaceRole | null;
  planName: string | null;
  loading: boolean;
  /** True when there is genuinely no workspace yet (e.g. a fresh account). */
  empty: boolean;
  reload: () => Promise<void>;
  /** Role gate helpers - backend enforces too; these drive UI affordances. */
  atLeast: (role: WorkspaceRole) => boolean;
  canEdit: boolean;
  canManage: boolean;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspace, setWorkspace] = useState<ApiWorkspace | null>(null);
  const [planName, setPlanName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [empty, setEmpty] = useState(false);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const ws = await api.get<ApiWorkspace>("workspaces/current");
      setWorkspace(ws);
      setEmpty(false);
      // Plan name is best-effort; never block the shell on it.
      try {
        const sub = await api.get<ApiSubscription>("subscriptions/current");
        setPlanName(sub?.plan?.name ?? null);
      } catch {
        setPlanName(null);
      }
    } catch (err) {
      if (err instanceof ApiError && (err.code === "no_workspace" || err.status === 404)) {
        setWorkspace(null);
        setEmpty(true);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const role = (workspace?.role as WorkspaceRole | undefined) ?? null;

  const value = useMemo<WorkspaceContextValue>(() => {
    const atLeast = (min: WorkspaceRole) => (role ? RANK[role] >= RANK[min] : false);
    return {
      workspace,
      role,
      planName,
      loading,
      empty,
      reload,
      atLeast,
      canEdit: atLeast("editor"),
      canManage: atLeast("admin"),
    };
  }, [workspace, role, planName, loading, empty, reload]);

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace(): WorkspaceContextValue {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within a WorkspaceProvider");
  return ctx;
}
