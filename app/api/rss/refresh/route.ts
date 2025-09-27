import { NextRequest, NextResponse } from "next/server";
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export async function POST(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json().catch(() => ({}));
  const feedId = body.feed_id ?? request.nextUrl.searchParams.get("feed_id") ?? undefined;

  const { data, error } = await supabase.functions.invoke("rss-fetch", {
    body: feedId ? { feed_id: feedId } : {}
  });

  if (error) {
    console.error("Failed to invoke rss-fetch", error);
    return NextResponse.json({ error: "Failed to refresh RSS" }, { status: 500 });
  }

  return NextResponse.json({ result: data });
}
