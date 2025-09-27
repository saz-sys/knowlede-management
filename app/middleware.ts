import { NextResponse, type NextRequest } from "next/server";
import { createMiddlewareClient } from "@supabase/auth-helpers-nextjs";

const PUBLIC_PATHS = ["/", "/login", "/_next", "/api/public"];

const isPublicPath = (pathname: string) =>
  PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(path));

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // パブリックパスは認証チェックをスキップ
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  const res = NextResponse.next();
  const supabase = createMiddlewareClient({ req: request, res });

  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
