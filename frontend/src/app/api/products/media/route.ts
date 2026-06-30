import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { API_V1, COOKIE_ACCESS, COOKIE_WS } from "@/lib/api/server";

// Binary passthrough for imported product media (images/video). The generic JSON
// proxy reads responses as text, which corrupts binary, so this dedicated route
// streams the bytes through with the auth/workspace headers attached.
export async function GET(req: NextRequest) {
  const url = req.nextUrl.searchParams.get("url");
  if (!url) return NextResponse.json({ error: { message: "Missing url" } }, { status: 400 });

  const store = await cookies();
  const access = store.get(COOKIE_ACCESS)?.value;
  const ws = store.get(COOKIE_WS)?.value;

  const headers: Record<string, string> = {};
  if (access) headers["Authorization"] = `Bearer ${access}`;
  if (ws) headers["X-Workspace-Id"] = ws;

  const res = await fetch(`${API_V1}/products/media?url=${encodeURIComponent(url)}`, {
    headers,
    cache: "no-store",
  });

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    return new NextResponse(text || JSON.stringify({ error: { message: "Media fetch failed" } }), {
      status: res.status || 502,
      headers: { "Content-Type": res.headers.get("content-type") || "application/json" },
    });
  }

  return new NextResponse(res.body, {
    status: 200,
    headers: { "Content-Type": res.headers.get("content-type") || "application/octet-stream" },
  });
}
