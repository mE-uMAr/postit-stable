/* Server-only helpers shared by the auth route handlers and the proxy. */

import type { NextResponse } from "next/server";

export const API_URL = process.env.API_URL || "http://localhost:8000";
export const API_V1 = `${API_URL}/api/v1`;

export const COOKIE_ACCESS = "pt_access";
export const COOKIE_REFRESH = "pt_refresh";
export const COOKIE_WS = "pt_ws";

const PROD = process.env.NODE_ENV === "production";

interface Tokens {
  access_token: string;
  refresh_token: string;
}

function baseCookie(maxAge: number) {
  return {
    httpOnly: true,
    secure: PROD,
    sameSite: "lax" as const,
    path: "/",
    maxAge,
  };
}

export function setSessionCookies(res: NextResponse, tokens: Tokens, workspaceId?: string): void {
  res.cookies.set(COOKIE_ACCESS, tokens.access_token, baseCookie(60 * 60)); // 1h envelope
  res.cookies.set(COOKIE_REFRESH, tokens.refresh_token, baseCookie(60 * 60 * 24 * 30));
  if (workspaceId) {
    res.cookies.set(COOKIE_WS, workspaceId, baseCookie(60 * 60 * 24 * 30));
  }
}

export function clearSessionCookies(res: NextResponse): void {
  for (const name of [COOKIE_ACCESS, COOKIE_REFRESH, COOKIE_WS]) {
    res.cookies.set(name, "", { ...baseCookie(0), maxAge: 0 });
  }
}

/** Fetch the caller's first workspace id to set as the active workspace cookie. */
export async function fetchPrimaryWorkspaceId(accessToken: string): Promise<string | undefined> {
  try {
    const res = await fetch(`${API_V1}/workspaces`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: "no-store",
    });
    if (!res.ok) return undefined;
    const list = (await res.json()) as { id: string }[];
    return list[0]?.id;
  } catch {
    return undefined;
  }
}

/** Decode (without verifying) a JWT payload - used only for UX gating in middleware. */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split(".")[1];
    const json = Buffer.from(part.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8");
    return JSON.parse(json);
  } catch {
    return null;
  }
}
