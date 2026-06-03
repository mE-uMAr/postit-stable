import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { API_V1, COOKIE_REFRESH, clearSessionCookies } from "@/lib/api/server";

export async function POST() {
  const store = await cookies();
  const refresh = store.get(COOKIE_REFRESH)?.value;
  if (refresh) {
    try {
      await fetch(`${API_V1}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
        cache: "no-store",
      });
    } catch {
      /* best-effort */
    }
  }
  const out = NextResponse.json({ message: "ok" });
  clearSessionCookies(out);
  return out;
}
