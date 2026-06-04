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

  // Resolve the superuser claim from whichever token cookie is present. Both the
  // access and refresh tokens carry it, so the gate survives access-token expiry.
  const payload = decodeJwtPayload(access || refresh || "");
  const isSuperuser = payload?.is_superuser === true;

  // Strict separation of the two user types (defence in depth — the API enforces
  // role on every route too):
  //  • the admin console is superuser-only;
  //  • superusers live in the admin console and never use the workspace app.
  if (pathname.startsWith("/admin") && !isSuperuser) {
    const url = req.nextUrl.clone();
    url.pathname = "/app/compose";
    return NextResponse.redirect(url);
  }
  if (pathname.startsWith("/app") && isSuperuser) {
    const url = req.nextUrl.clone();
    url.pathname = "/admin";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/app/:path*", "/admin/:path*"],
};
