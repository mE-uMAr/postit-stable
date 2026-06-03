import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { API_V1, COOKIE_ACCESS, COOKIE_REFRESH, COOKIE_WS, setSessionCookies } from "@/lib/api/server";

async function handle(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const store = await cookies();
  let access = store.get(COOKIE_ACCESS)?.value;
  const refresh = store.get(COOKIE_REFRESH)?.value;
  const ws = store.get(COOKIE_WS)?.value;

  const target = `${API_V1}/${path.join("/")}${req.nextUrl.search}`;
  const method = req.method;
  const hasBody = !["GET", "HEAD"].includes(method);
  const bodyText = hasBody ? await req.text() : undefined;

  const buildHeaders = (token?: string) => {
    const h: Record<string, string> = {};
    const ct = req.headers.get("content-type");
    if (ct) h["Content-Type"] = ct;
    if (token) h["Authorization"] = `Bearer ${token}`;
    if (ws) h["X-Workspace-Id"] = ws;
    return h;
  };

  let backendRes = await fetch(target, {
    method,
    headers: buildHeaders(access),
    body: bodyText,
    cache: "no-store",
  });

  // Transparent refresh-and-retry once on expiry.
  let rotated: { access_token: string; refresh_token: string } | null = null;
  if (backendRes.status === 401 && refresh) {
    const r = await fetch(`${API_V1}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
      cache: "no-store",
    });
    if (r.ok) {
      rotated = await r.json();
      access = rotated!.access_token;
      backendRes = await fetch(target, {
        method,
        headers: buildHeaders(access),
        body: bodyText,
        cache: "no-store",
      });
    }
  }

  const text = await backendRes.text();
  const out = new NextResponse(text, {
    status: backendRes.status,
    headers: { "Content-Type": backendRes.headers.get("content-type") || "application/json" },
  });
  if (rotated) setSessionCookies(out, rotated, ws);
  return out;
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
