import { NextRequest, NextResponse } from "next/server";

import { COOKIE_ACCESS, COOKIE_REFRESH, decodeJwtPayload } from "@/lib/api/server";

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const access = req.cookies.get(COOKIE_ACCESS)?.value;
  const refresh = req.cookies.get(COOKIE_REFRESH)?.value;
  const hasSession = Boolean(access || refresh);

  if (!hasSession) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  // Superuser gate for the admin section (defence in depth; API enforces too).
  if (pathname.startsWith("/admin") && access) {
    const payload = decodeJwtPayload(access);
    if (payload && payload.is_superuser !== true) {
      const url = req.nextUrl.clone();
      url.pathname = "/app/compose";
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/app/:path*", "/admin/:path*"],
};
