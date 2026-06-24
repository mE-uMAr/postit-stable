import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { API_V1, COOKIE_ACCESS, COOKIE_WS } from "@/lib/api/server";

// Multipart publish: forwards the post's media files (streamed to the platforms,
// never stored) plus the auth/workspace headers. The JSON proxy can't carry
// binary bodies, so this is a dedicated route.
export async function POST(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const store = await cookies();
  const access = store.get(COOKIE_ACCESS)?.value;
  const ws = store.get(COOKIE_WS)?.value;

  const headers: Record<string, string> = {};
  if (access) headers["Authorization"] = `Bearer ${access}`;
  if (ws) headers["X-Workspace-Id"] = ws;

  const form = await req.formData();
  const res = await fetch(`${API_V1}/posts/${id}/publish`, {
    method: "POST",
    headers,
    body: form,
    cache: "no-store",
  });
  return NextResponse.json(await res.json().catch(() => ({})), { status: res.status });
}
