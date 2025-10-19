import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { CreateCommentRequest } from "@/lib/types/comments";
import { sendCommentNotification } from "@/lib/slack/notification";

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

    // 投稿者にSlack通知を送信（非同期で実行）
    try {
      // 投稿情報と投稿者のプロフィール情報を取得
      const { data: post, error: postError } = await supabase
        .from("posts")
        .select(`
          title, 
          author_email,
          author_id
        `)
        .eq("id", post_id)
        .single();

      if (!postError && post) {
        // 投稿者のプロフィール情報を取得
        const { data: postAuthor, error: postAuthorError } = await supabase
          .from("profiles")
          .select("name, email")
          .eq("id", post.author_id)
          .single();

        // コメント投稿者の情報を取得
        const { data: commentAuthor, error: authorError } = await supabase
          .from("profiles")
          .select("name, email")
          .eq("id", session.user.id)
          .single();

        const authorName = commentAuthor?.name || commentAuthor?.email || "不明なユーザー";
        const postUrl = `${process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'}/posts/${post_id}`;

        // 返信コメントの場合、元のコメント投稿者の情報を取得
        let parentCommentAuthor = null;
        let parentCommentAuthorEmail = null;
        
        if (parent_id) {
          const { data: parentComment, error: parentCommentError } = await supabase
            .from("comments")
            .select("author_id")
            .eq("id", parent_id)
            .single();

          if (!parentCommentError && parentComment) {
            const { data: parentAuthor, error: parentAuthorError } = await supabase
              .from("profiles")
              .select("name, email")
              .eq("id", parentComment.author_id)
              .single();

            if (!parentAuthorError && parentAuthor) {
              parentCommentAuthor = parentAuthor.name || parentAuthor.email;
              parentCommentAuthorEmail = parentAuthor.email;
            }
          }
        }

        // Slack通知を送信（非同期で実行、エラーはログのみ）
        sendCommentNotification({
          postTitle: post.title,
          postUrl: postUrl,
          commentAuthor: authorName,
          commentContent: content,
          postAuthorEmail: post.author_email || "不明",
          postAuthorName: postAuthor?.name,
          isReply: !!parent_id,
          parentCommentAuthor: parentCommentAuthor,
          parentCommentAuthorEmail: parentCommentAuthorEmail
        }).catch(error => {
          console.error("Failed to send Slack notification:", error);
        });
      }
    } catch (notificationError) {
      console.error("Error preparing Slack notification:", notificationError);
      // 通知エラーはコメント作成を阻害しない
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

        // プロフィール情報を取得
        const authorIds = Array.from(new Set(comments?.map(c => c.author_id) || []));
    const { data: profiles, error: profilesError } = await supabase
      .from("profiles")
      .select("id, name, email")
      .in("id", authorIds);

    if (profilesError) {
      console.error("Profiles fetch error:", profilesError);
    }

    // プロフィール情報をマップに変換
    const profileMap = new Map();
    profiles?.forEach(profile => {
      profileMap.set(profile.id, profile);
    });

    // コメントにプロフィール情報を追加
    const commentsWithProfiles = comments?.map(comment => ({
      ...comment,
      author: profileMap.get(comment.author_id) || null
    })) || [];

    // 階層構造に変換
    const commentMap = new Map();
    const rootComments: any[] = [];

    commentsWithProfiles.forEach(comment => {
      (comment as any).replies = [];
      (comment as any).reply_count = 0;
      commentMap.set(comment.id, comment);
    });

    commentsWithProfiles.forEach(comment => {
      if (comment.parent_id) {
        const parent = commentMap.get(comment.parent_id);
        if (parent) {
          (parent as any).replies.push(comment);
          (parent as any).reply_count = ((parent as any).reply_count || 0) + 1;
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
