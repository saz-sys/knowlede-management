import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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

    const postId = params.id;
    const forceDelete = request.headers.get("X-Force-Delete") === "true";

    // 投稿の所有者を確認
    const { data: post, error: postError } = await supabase
      .from("posts")
      .select("id, author_id, title")
      .eq("id", postId)
      .single();

    if (postError || !post) {
      return NextResponse.json({ error: "Post not found" }, { status: 404 });
    }

    if (post.author_id !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // 強制削除でない場合は関連データの存在確認
    if (!forceDelete) {
      const { data: relatedData, error: relatedError } = await supabase
        .from("posts")
        .select(`
          comments(count),
          bookmarks(count)
        `)
        .eq("id", postId)
        .single();

      if (relatedError) {
        console.error("Failed to check related data:", relatedError);
        return NextResponse.json({ error: "Failed to check related data" }, { status: 500 });
      }

      const commentCount = relatedData?.comments?.[0]?.count || 0;
      const bookmarkCount = relatedData?.bookmarks?.[0]?.count || 0;

      // 関連データがある場合は警告メッセージを返す
      if (commentCount > 0 || bookmarkCount > 0) {
        return NextResponse.json({
          error: "HAS_RELATED_DATA",
          message: "この投稿には関連するデータがあります",
          details: {
            comments: commentCount,
            bookmarks: bookmarkCount
          }
        }, { status: 409 });
      }
    }

    // 投稿を削除（CASCADEで関連データも削除される）
    const { error: deleteError } = await supabase
      .from("posts")
      .delete()
      .eq("id", postId);

    if (deleteError) {
      console.error("Failed to delete post:", deleteError);
      return NextResponse.json({ error: "Failed to delete post" }, { status: 500 });
    }

    return NextResponse.json({ 
      message: forceDelete ? "投稿と関連データが削除されました" : "投稿が削除されました",
      deletedPost: {
        id: post.id,
        title: post.title
      }
    });
  } catch (error) {
    console.error("Unexpected error while deleting post:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
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

    const postId = params.id;
    const body = await request.json();
    const { title, url, content, summary, tags = [] } = body;

    if (!title?.trim() || !url?.trim()) {
      return NextResponse.json({ error: "Title and url are required" }, { status: 400 });
    }

    // 投稿の所有者を確認
    const { data: post, error: postError } = await supabase
      .from("posts")
      .select("id, author_id, url")
      .eq("id", postId)
      .single();

    if (postError || !post) {
      return NextResponse.json({ error: "Post not found" }, { status: 404 });
    }

    if (post.author_id !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // URLが変更された場合の重複チェック
    if (post.url !== url.trim()) {
      const { data: existingPost, error: checkError } = await supabase
        .from("posts")
        .select("id, title, author_email, created_at")
        .eq("url", url.trim())
        .neq("id", postId)
        .single();

      if (checkError && checkError.code !== "PGRST116") {
        console.error("Error checking for duplicate URL:", checkError);
        return NextResponse.json({ error: "Failed to check for duplicate URL" }, { status: 500 });
      }

      if (existingPost) {
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
    }

    // 投稿を更新
    const { data: updatedPost, error: updateError } = await supabase
      .from("posts")
      .update({
        title: title.trim(),
        url: url.trim(),
        content: content?.trim() ?? null,
        summary: summary?.trim() ?? null,
        updated_at: new Date().toISOString()
      })
      .eq("id", postId)
      .select("id, title, url, content, summary, updated_at")
      .single();

    if (updateError || !updatedPost) {
      console.error("Failed to update post:", updateError);
      return NextResponse.json({ error: "Failed to update post" }, { status: 500 });
    }

    // タグの更新
    if (tags.length > 0) {
      // 既存のタグを削除
      await supabase
        .from("post_tags")
        .delete()
        .eq("post_id", postId);

      // 新しいタグを追加
      const tagPayload = tags.map((tagName: string) => ({
        name: tagName,
        description: null
      }));

      const { data: upsertedTags, error: tagError } = await supabase
        .from("tags")
        .upsert(tagPayload, { onConflict: "name" })
        .select("id, name");

      if (tagError) {
        console.error("Tag upsert failed:", tagError);
      } else if (upsertedTags) {
        const postTagsPayload = upsertedTags.map((tag) => ({
          post_id: postId,
          tag_id: tag.id
        }));

        const { error: postTagsError } = await supabase.from("post_tags").upsert(postTagsPayload);
        if (postTagsError) {
          console.error("Post tags upsert failed:", postTagsError);
        }
      }
    }

    return NextResponse.json({ post: updatedPost });
  } catch (error) {
    console.error("Unexpected error while updating post:", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
