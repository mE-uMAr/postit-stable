import { NextRequest, NextResponse } from "next/server";

import { API_V1, fetchPrimaryWorkspaceId, setSessionCookies } from "@/lib/api/server";

// Verify the signup OTP; on success the backend returns tokens and we establish
// the session cookies (same as login).
export async function POST(req: NextRequest) {
  const body = await req.json();
  const res = await fetch(`${API_V1}/auth/verify-otp`, {
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
