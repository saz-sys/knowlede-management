import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const {
      data: { session },
      error: authError
    } = await supabase.auth.getSession();

    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // 自分の投稿を取得（コメント数とブックマーク数も含む）
    const { data: posts, error: fetchError } = await supabase
      .from("posts")
      .select(`
        id,
        title,
        url,
        summary,
        created_at,
        updated_at,
        post_tags(
          tag:tags(id, name)
        ),
        comments(count),
        bookmarks(count)
      `)
      .eq("author_id", session.user.id)
      .order("created_at", { ascending: false });

    if (fetchError) {
      console.error("Failed to fetch my posts:", fetchError);
      return NextResponse.json({ error: "Failed to fetch posts" }, { status: 500 });
    }

    // コメント数とブックマーク数を計算
    const postsWithCounts = posts?.map(post => ({
      ...post,
      _count: {
        comments: post.comments?.[0]?.count || 0,
        bookmarks: post.bookmarks?.[0]?.count || 0
      }
    })) || [];

    return NextResponse.json({ posts: postsWithCounts });
  } catch (error) {
    console.error("Unexpected error while fetching my posts:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
