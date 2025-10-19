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

    const { searchParams } = new URL(request.url);
    const isRead = searchParams.get("is_read");
    const postId = searchParams.get("post_id");

    let query = supabase
      .from("bookmarks")
      .select(`
        id,
        created_at,
        is_read,
        notes,
        posts (
          id,
          title,
          url,
          created_at,
          metadata
        )
      `)
      .eq("user_id", session.user.id)
      .order("created_at", { ascending: false });

    // フィルタリング
    if (isRead !== null) {
      query = query.eq("is_read", isRead === "true");
    }

    if (postId) {
      query = query.eq("post_id", postId);
    }

    const { data: bookmarks, error } = await query;

    if (error) {
      console.error("Bookmarks fetch error:", error);
      return NextResponse.json({ error: "Failed to fetch bookmarks" }, { status: 500 });
    }

    return NextResponse.json({ bookmarks });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { post_id, notes } = body;

    if (!post_id) {
      return NextResponse.json({ error: "post_id is required" }, { status: 400 });
    }

    // 投稿の存在確認
    const { data: post, error: postError } = await supabase
      .from("posts")
      .select("id")
      .eq("id", post_id)
      .single();

    if (postError || !post) {
      return NextResponse.json({ error: "Post not found" }, { status: 404 });
    }

    // ブックマーク作成
    const { data: bookmark, error: insertError } = await supabase
      .from("bookmarks")
      .insert({
        user_id: session.user.id,
        post_id,
        notes: notes || null
      })
      .select(`
        id,
        created_at,
        is_read,
        notes,
        posts (
          id,
          title,
          url
        )
      `)
      .single();

    if (insertError) {
      console.error("Bookmark creation error:", insertError);
      
      // 重複エラーの場合
      if (insertError.code === '23505') {
        return NextResponse.json({ error: "この投稿は既にブックマークされています" }, { status: 409 });
      }
      
      return NextResponse.json({ error: "Failed to create bookmark" }, { status: 500 });
    }

    return NextResponse.json({ bookmark }, { status: 201 });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const post_id = searchParams.get("post_id");

    if (!post_id) {
      return NextResponse.json({ error: "post_id is required" }, { status: 400 });
    }

    // ブックマーク削除
    const { error: deleteError } = await supabase
      .from("bookmarks")
      .delete()
      .eq("user_id", session.user.id)
      .eq("post_id", post_id);

    if (deleteError) {
      console.error("Bookmark deletion error:", deleteError);
      return NextResponse.json({ error: "Failed to delete bookmark" }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
