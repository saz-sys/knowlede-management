import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { AddReactionRequest, RemoveReactionRequest } from "@/lib/types/comments";

export async function POST(
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

    const body: AddReactionRequest = await request.json();
    const { emoji } = body;

    if (!emoji) {
      return NextResponse.json({ error: "Emoji is required" }, { status: 400 });
    }

    // コメントの存在確認
    const { data: comment, error: commentError } = await supabase
      .from("comments")
      .select("id, reactions")
      .eq("id", params.id)
      .single();

    if (commentError || !comment) {
      return NextResponse.json({ error: "Comment not found" }, { status: 404 });
    }

    // リアクション追加
    const currentReactions = comment.reactions || {};
    const emojiUsers = currentReactions[emoji] || [];
    
    if (!emojiUsers.includes(session.user.id)) {
      emojiUsers.push(session.user.id);
    }

    const updatedReactions = {
      ...currentReactions,
      [emoji]: emojiUsers
    };

    const { data: updatedComment, error: updateError } = await supabase
      .from("comments")
      .update({ reactions: updatedReactions })
      .eq("id", params.id)
      .select("reactions")
      .single();

    if (updateError) {
      console.error("Reaction update error:", updateError);
      return NextResponse.json({ error: "Failed to add reaction" }, { status: 500 });
    }

    return NextResponse.json({ reactions: updatedComment.reactions });
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

    const body: RemoveReactionRequest = await request.json();
    const { emoji } = body;

    if (!emoji) {
      return NextResponse.json({ error: "Emoji is required" }, { status: 400 });
    }

    // コメントの存在確認
    const { data: comment, error: commentError } = await supabase
      .from("comments")
      .select("id, reactions")
      .eq("id", params.id)
      .single();

    if (commentError || !comment) {
      return NextResponse.json({ error: "Comment not found" }, { status: 404 });
    }

    // リアクション削除
    const currentReactions = comment.reactions || {};
    const emojiUsers = currentReactions[emoji] || [];
    const filteredUsers = emojiUsers.filter(userId => userId !== session.user.id);

    const updatedReactions = {
      ...currentReactions,
      [emoji]: filteredUsers.length > 0 ? filteredUsers : undefined
    };

    // 空のリアクションを削除
    Object.keys(updatedReactions).forEach(emoji => {
      if (!updatedReactions[emoji] || updatedReactions[emoji].length === 0) {
        delete updatedReactions[emoji];
      }
    });

    const { data: updatedComment, error: updateError } = await supabase
      .from("comments")
      .update({ reactions: updatedReactions })
      .eq("id", params.id)
      .select("reactions")
      .single();

    if (updateError) {
      console.error("Reaction removal error:", updateError);
      return NextResponse.json({ error: "Failed to remove reaction" }, { status: 500 });
    }

    return NextResponse.json({ reactions: updatedComment.reactions });
  } catch (error) {
    console.error("Unexpected error:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
