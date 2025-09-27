import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { CreateCommentRequest } from "@/lib/types/comments";

export async function POST(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body: CreateCommentRequest = await request.json();
    const { post_id, parent_id, content } = body;

    // バリデーション
    if (!post_id || !content) {
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

    // 親コメントの存在確認（返信の場合）
    if (parent_id) {
      const { data: parentComment, error: parentError } = await supabase
        .from("comments")
        .select("id")
        .eq("id", parent_id)
        .eq("post_id", post_id)
        .single();

      if (parentError || !parentComment) {
        return NextResponse.json({ error: "Parent comment not found" }, { status: 404 });
      }
    }

    // コメント作成
    const { data: comment, error: insertError } = await supabase
      .from("comments")
      .insert({
        post_id,
        author_id: session.user.id,
        parent_id: parent_id || null,
        content,
        reactions: {}
      })
      .select(`
        id,
        post_id,
        author_id,
        parent_id,
        content,
        reactions,
        created_at,
        updated_at
      `)
      .single();

    if (insertError) {
      console.error("Comment creation error:", insertError);
      return NextResponse.json({ error: "Failed to create comment" }, { status: 500 });
    }

    return NextResponse.json({ comment }, { status: 201 });
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

    // コメント取得（階層構造）
    const { data: comments, error: commentsError } = await supabase
      .from("comments")
      .select(`
        id,
        post_id,
        author_id,
        parent_id,
        content,
        reactions,
        created_at,
        updated_at
      `)
      .eq("post_id", post_id)
      .order("created_at", { ascending: true });

    if (commentsError) {
      console.error("Comments fetch error:", commentsError);
      return NextResponse.json({ error: "Failed to fetch comments" }, { status: 500 });
    }

    // 階層構造に変換
    const commentMap = new Map();
    const rootComments: any[] = [];

    comments?.forEach(comment => {
      comment.replies = [];
      comment.reply_count = 0;
      commentMap.set(comment.id, comment);
    });

    comments?.forEach(comment => {
      if (comment.parent_id) {
        const parent = commentMap.get(comment.parent_id);
        if (parent) {
          parent.replies.push(comment);
          parent.reply_count = (parent.reply_count || 0) + 1;
        }
      } else {
        rootComments.push(comment);
      }
    });

    return NextResponse.json({ comments: rootComments });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
