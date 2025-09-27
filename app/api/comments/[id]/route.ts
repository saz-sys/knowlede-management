import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { UpdateCommentRequest, AddReactionRequest, RemoveReactionRequest } from "@/lib/types/comments";

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body: UpdateCommentRequest = await request.json();
    const { content } = body;

    if (!content) {
      return NextResponse.json({ error: "Content is required" }, { status: 400 });
    }

    // コメントの存在確認と権限チェック
    const { data: comment, error } = await supabase
      .from("comments")
      .select(
        `id, post_id, author_id, parent_id, content, reactions, created_at, updated_at`
      )
      .eq("id", params.id)
      .eq("author_id", session.user.id)
      .single();

    if (error || !comment) {
      return NextResponse.json({ error: "Comment not found" }, { status: 404 });
    }

    if (comment.author_id !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // コメント更新
    const { data: updatedComment, error: updateError } = await supabase
      .from("comments")
      .update({
        content,
        updated_at: new Date().toISOString()
      })
      .eq("id", params.id)
      .select(`
        id,
        post_id,
        author_id,
        parent_id,
        content,
        reactions,
        created_at,
        updated_at,
        author:users(id, email, name)
      `)
      .single();

    if (updateError) {
      console.error("Comment update error:", updateError);
      return NextResponse.json({ error: "Failed to update comment" }, { status: 500 });
    }

    return NextResponse.json({ comment: updatedComment });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    // 認証チェック
    const { data: { session }, error: authError } = await supabase.auth.getSession();
    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // コメントの存在確認と権限チェック
    const { data: comment, error: commentError } = await supabase
      .from("comments")
      .select("id, author_id")
      .eq("id", params.id)
      .single();

    if (commentError || !comment) {
      return NextResponse.json({ error: "Comment not found" }, { status: 404 });
    }

    if (comment.author_id !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // コメント削除
    const { error: deleteError } = await supabase
      .from("comments")
      .delete()
      .eq("id", params.id);

    if (deleteError) {
      console.error("Comment deletion error:", deleteError);
      return NextResponse.json({ error: "Failed to delete comment" }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
