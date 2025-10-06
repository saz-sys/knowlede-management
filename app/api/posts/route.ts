import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import type { CreatePostRequest } from "@/lib/types/posts";
import { sendPostNotification } from "@/lib/slack/notification";

export async function POST(request: NextRequest) {
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

    const body: CreatePostRequest = await request.json();
    const { title, url, content, summary, tags = [], notified_channels = [] } = body;

    if (!title?.trim() || !url?.trim()) {
      return NextResponse.json({ error: "Title and url are required" }, { status: 400 });
    }

    // URL重複チェック
    const { data: existingPost, error: checkError } = await supabase
      .from("posts")
      .select("id, title, author_email, created_at")
      .eq("url", url.trim())
      .single();

    if (checkError && checkError.code !== "PGRST116") {
      // PGRST116は「行が見つからない」エラー（重複なし）
      console.error("Error checking for duplicate URL:", checkError);
      return NextResponse.json({ error: "Failed to check for duplicate URL" }, { status: 500 });
    }

    if (existingPost) {
      // 重複URLが見つかった場合
      return NextResponse.json({
        error: "DUPLICATE_URL",
        message: "このURLは既に投稿されています",
        existingPost: {
          id: existingPost.id,
          title: existingPost.title,
          author_email: existingPost.author_email,
          created_at: existingPost.created_at
        }
      }, { status: 409 });
    }

    const { data: post, error: insertError } = await supabase
      .from("posts")
      .insert({
        author_id: session.user.id,
        author_email: session.user.email,
        title: title.trim(),
        url: url.trim(),
        content: content?.trim() ?? null,
        summary: summary?.trim() ?? null,
        notified_channels,
        metadata: { source: "manual" }
      })
      .select(
        "id, author_id, title, url, content, summary, notified_channels, metadata, created_at, updated_at"
      )
      .single();

    if (insertError || !post) {
      console.error("Failed to insert post", insertError);
      return NextResponse.json({ error: "Failed to create post" }, { status: 500 });
    }

    if (tags.length > 0) {
      const tagPayload = tags.map((tagName) => ({
        name: tagName,
        description: null
      }));

      const { data: upsertedTags, error: tagError } = await supabase
        .from("tags")
        .upsert(tagPayload, { onConflict: "name" })
        .select("id, name");

      if (tagError) {
        console.error("Tag upsert failed", tagError);
      } else if (upsertedTags) {
        const postTagsPayload = upsertedTags.map((tag) => ({
          post_id: post.id,
          tag_id: tag.id
        }));

        const { error: postTagsError } = await supabase.from("post_tags").upsert(postTagsPayload);
        if (postTagsError) {
          console.error("Post tags upsert failed", postTagsError);
        }
      }
    }

    // ユーザー投稿の場合のみSlack通知を送信（RSS投稿は除外）
    if (post.metadata?.source !== "rss") {
      try {
        // ユーザー情報を取得
        const { data: profile } = await supabase
          .from("profiles")
          .select("name, email")
          .eq("id", session.user.id)
          .single();

        await sendPostNotification({
          postId: post.id,
          title: post.title,
          url: post.url,
          authorName: profile?.name || session.user.user_metadata?.name || "Unknown",
          authorEmail: session.user.email || "",
          content: post.content || undefined
        });
      } catch (notificationError) {
        // Slack通知の失敗は投稿作成を阻害しない
        console.error("Failed to send post notification:", notificationError);
      }
    }

    return NextResponse.json({ post }, { status: 201 });
  } catch (error) {
    console.error("Unexpected error while creating post", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    const cookieStore = cookies();
    const supabase = createRouteHandlerClient({ cookies: () => cookieStore });

    const {
      data: { session },
      error: authError
    } = await supabase.auth.getSession();

    if (authError) {
      console.error("Auth error:", authError);
      return NextResponse.json({ error: "Authentication failed" }, { status: 401 });
    }

    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const tag = searchParams.get("tag");
    const source = searchParams.get("source");
    const page = parseInt(searchParams.get("page") || "1", 10);
    const limit = parseInt(searchParams.get("limit") || "10", 10);
    const offset = (page - 1) * limit;

    // まず基本的なクエリを構築
           let query = supabase
             .from("posts")
             .select(
               `
                 id,
                 author_email,
                 title,
                 url,
                 summary,
                 metadata,
                 created_at,
                 post_tags(tag:tags(name)),
                 comments(count),
                 bookmarks(count),
                 post_likes(count)
               `
             )
      .order("created_at", { ascending: false })
      .range(offset, offset + limit - 1);

    // フィルタ条件を適用
    if (tag) {
      // タグフィルタの場合は、post_tagsテーブルを経由してフィルタリング
      // まずタグIDを取得
      const { data: tagData, error: tagError } = await supabase
        .from("tags")
        .select("id")
        .eq("name", tag)
        .single();
      
      if (tagError) {
        console.error("Failed to find tag:", tagError);
        return NextResponse.json({ error: "Tag not found" }, { status: 404 });
      }
      
      // タグに関連する投稿IDを取得
      const { data: postTags, error: postTagsError } = await supabase
        .from("post_tags")
        .select("post_id")
        .eq("tag_id", tagData.id);
      
      if (postTagsError) {
        console.error("Failed to fetch post tags:", postTagsError);
        return NextResponse.json({ error: "Failed to fetch posts with tag" }, { status: 500 });
      }
      
      const postIds = postTags?.map(pt => pt.post_id) || [];
      if (postIds.length === 0) {
        return NextResponse.json({ 
          posts: [], 
          pagination: {
            page,
            limit,
            total: 0,
            totalPages: 0,
            hasMore: false
          }
        });
      }
      
      // 投稿IDでフィルタリング
      query = query.in("id", postIds);
    }

    if (source === "manual") {
      query = query.or("metadata->>source.is.null,metadata->>source.neq.rss");
    } else if (source === "rss") {
      query = query.eq("metadata->>source", "rss");
    }

    const { data: posts, error: fetchError } = await query;

    if (fetchError) {
      console.error("Failed to fetch posts", fetchError);
      return NextResponse.json({ error: "Failed to fetch posts" }, { status: 500 });
    }

    // 一時的にカウントクエリを無効化してテスト
    const hasMore = posts.length === limit;
    
    return NextResponse.json({ 
      posts, 
      pagination: {
        page,
        limit,
        total: posts.length,
        totalPages: page + (hasMore ? 1 : 0),
        hasMore
      }
    });
  } catch (error) {
    console.error("Unexpected error while fetching posts", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

