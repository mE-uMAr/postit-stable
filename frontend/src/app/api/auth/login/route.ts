import { NextRequest, NextResponse } from "next/server";

import { API_V1, fetchPrimaryWorkspaceId, setSessionCookies } from "@/lib/api/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const res = await fetch(`${API_V1}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }
  const wsId = await fetchPrimaryWorkspaceId(data.tokens.access_token);
  const out = NextResponse.json({ user: data.user });
  setSessionCookies(out, data.tokens, wsId);
  return out;
}
