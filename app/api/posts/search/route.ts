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

    const { searchParams } = new URL(request.url);
    const query = searchParams.get("q");
    const tag = searchParams.get("tag");
    const source = searchParams.get("source");
    const limit = parseInt(searchParams.get("limit") || "20");
    const offset = parseInt(searchParams.get("offset") || "0");

    if (!query || query.trim().length === 0) {
      return NextResponse.json({ error: "Search query is required" }, { status: 400 });
    }

    // 検索クエリを構築
    let supabaseQuery = supabase
      .from("posts")
      .select(`
        id,
        author_id,
        author_email,
        title,
        url,
        content,
        metadata,
        created_at,
        updated_at,
        post_tags(tag:tags(id, name)),
        comments(count),
        bookmarks(count),
        post_likes(count)
      `)
      .or(`title.ilike.%${query}%,content.ilike.%${query}%`)
      .order("created_at", { ascending: false })
      .range(offset, offset + limit - 1);

    // 追加フィルタ
    if (tag) {
      supabaseQuery = supabaseQuery.contains("post_tags", [{ tag: { name: tag } }]);
    }

    if (source === "manual") {
      supabaseQuery = supabaseQuery.or("metadata->>source.is.null,metadata->>source.neq.rss");
    } else if (source === "rss") {
      supabaseQuery = supabaseQuery.eq("metadata->>source", "rss");
    }

    const { data: posts, error: fetchError } = await supabaseQuery;

    if (fetchError) {
      console.error("Failed to search posts:", fetchError);
      return NextResponse.json({ error: "Failed to search posts" }, { status: 500 });
    }

    // 総件数を取得（ページネーション用）
    let countQuery = supabase
      .from("posts")
      .select("id", { count: "exact", head: true })
      .or(`title.ilike.%${query}%,content.ilike.%${query}%`);

    if (tag) {
      countQuery = countQuery.contains("post_tags", [{ tag: { name: tag } }]);
    }

    if (source === "manual") {
      countQuery = countQuery.or("metadata->>source.is.null,metadata->>source.neq.rss");
    } else if (source === "rss") {
      countQuery = countQuery.eq("metadata->>source", "rss");
    }

    const { count, error: countError } = await countQuery;

    if (countError) {
      console.error("Failed to get search count:", countError);
    }

    return NextResponse.json({ 
      posts: posts || [],
      total: count || 0,
      query: query,
      limit,
      offset
    });
  } catch (error) {
    console.error("Unexpected error while searching posts:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
