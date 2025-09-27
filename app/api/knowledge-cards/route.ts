import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { CreateKnowledgeCardRequest } from "@/lib/types/knowledge-cards";

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body: CreateKnowledgeCardRequest = await request.json();
    const { post_id, title, content, related_comment_ids } = body;

    // バリデーション
    if (!post_id || !title || !content) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
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

    // 関連コメントの存在確認
    if (related_comment_ids && related_comment_ids.length > 0) {
      const { data: comments, error: commentsError } = await supabase
        .from("comments")
        .select("id")
        .in("id", related_comment_ids)
        .eq("post_id", post_id);

      if (commentsError || !comments || comments.length !== related_comment_ids.length) {
        return NextResponse.json({ error: "Some related comments not found" }, { status: 400 });
      }
    }

    // ナレッジカード作成
    const { data: knowledgeCard, error: insertError } = await supabase
      .from("knowledge_cards")
      .insert({
        post_id,
        title,
        content,
        created_by: session.user.id,
        related_comments: related_comment_ids || []
      })
      .select(`
        id,
        post_id,
        title,
        content,
        created_by,
        created_at,
        updated_at,
        created_by_user:users(id, email, name)
      `)
      .single();

    if (insertError) {
      console.error("Knowledge card creation error:", insertError);
      return NextResponse.json({ error: "Failed to create knowledge card" }, { status: 500 });
    }

    return NextResponse.json({ knowledgeCard }, { status: 201 });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

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
    const post_id = searchParams.get("post_id");

    if (!post_id) {
      return NextResponse.json({ error: "post_id is required" }, { status: 400 });
    }

    // ナレッジカード取得
    const { data: knowledgeCards, error: cardsError } = await supabase
      .from("knowledge_cards")
      .select(`
        id,
        post_id,
        title,
        content,
        created_by,
        created_at,
        updated_at,
        created_by_user:users(id, email, name)
      `)
      .eq("post_id", post_id)
      .order("created_at", { ascending: false });

    if (cardsError) {
      console.error("Knowledge cards fetch error:", cardsError);
      return NextResponse.json({ error: "Failed to fetch knowledge cards" }, { status: 500 });
    }

    return NextResponse.json({ knowledgeCards });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
