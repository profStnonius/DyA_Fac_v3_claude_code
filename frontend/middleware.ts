import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/callback"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const raw = request.cookies.get("cfdi-auth")?.value;
  let accessToken: string | null = null;

  if (raw) {
    try {
      const parsed = JSON.parse(decodeURIComponent(raw));
      accessToken = parsed?.state?.accessToken ?? null;
    } catch {
      // malformed cookie — treat as unauthenticated
    }
  }

  if (!accessToken) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.search = "";
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)"],
};
