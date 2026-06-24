import { NextRequest, NextResponse } from "next/server";

import { API_V1 } from "@/lib/api/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const res = await fetch(`${API_V1}/auth/resend-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  return NextResponse.json(await res.json(), { status: res.status });
}
