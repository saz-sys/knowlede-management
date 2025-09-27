import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import type { CreatePostRequest } from "@/lib/types/posts";

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

    const { data: post, error: insertError } = await supabase
      .from("posts")
      .insert({
        author_id: session.user.id,
        title: title.trim(),
        url: url.trim(),
        content: content?.trim() ?? null,
        summary: summary?.trim() ?? null,
        notified_channels
      })
      .select(
        "id, author_id, title, url, content, summary, notified_channels, created_at, updated_at"
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

    if (authError || !session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const tag = searchParams.get("tag");

    let query = supabase
      .from("posts")
      .select(
        "id, author_id, title, url, content, summary, notified_channels, created_at, updated_at, post_tags(tag:tags(id, name))"
      )
      .order("created_at", { ascending: false });

    if (tag) {
      query = query.contains("post_tags", [{ tag: { name: tag } }]);
    }

    const { data: posts, error: fetchError } = await query;

    if (fetchError) {
      console.error("Failed to fetch posts", fetchError);
      return NextResponse.json({ error: "Failed to fetch posts" }, { status: 500 });
    }

    return NextResponse.json({ posts });
  } catch (error) {
    console.error("Unexpected error while fetching posts", error);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}

