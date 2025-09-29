import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // ログインユーザーのブックマーク一覧を取得
    const { data: bookmarks, error: bookmarksError } = await supabase
      .from("bookmarks")
      .select("post_id")
      .eq("user_id", session.user.id);

    if (bookmarksError) {
      console.error("Bookmarks fetch error:", bookmarksError);
      return NextResponse.json({ error: "Failed to fetch bookmarks" }, { status: 500 });
    }

    // ブックマーク済みのpost_idのセットを返す
    const bookmarkedPostIds = new Set(bookmarks?.map(b => b.post_id) || []);

    return NextResponse.json({ bookmarkedPostIds: Array.from(bookmarkedPostIds) });

  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
