import { NextRequest, NextResponse } from "next/server";
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import type { RssFeed } from "@/lib/types/rss";

function normalizeTags(tags?: string[]): string[] {
  if (!tags) return [];
  return Array.from(
    new Set(
      tags
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0)
    )
  );
}

export async function GET() {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { data, error } = await supabase
    .from("rss_feeds")
    .select("id, name, url, tags, is_active, last_fetched_at, created_at")
    .order("created_at", { ascending: false });

  if (error) {
    console.error("Failed to fetch rss_feeds", error);
    return NextResponse.json({ error: "Failed to fetch rss feeds" }, { status: 500 });
  }

  return NextResponse.json({ feeds: (data ?? []) as RssFeed[] });
}

export async function POST(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let body: { name?: string; url?: string; tags?: string[] };
  try {
    body = await request.json();
  } catch (error) {
    console.error("Failed to parse request body", error);
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const name = body.name?.trim();
  const url = body.url?.trim();
  const tags = normalizeTags(body.tags);

  if (!name || !url) {
    return NextResponse.json({ error: "name and url are required" }, { status: 400 });
  }

  const { data: existing, error: existingError } = await supabase
    .from("rss_feeds")
    .select("id")
    .ilike("url", url)
    .maybeSingle();

  if (existingError) {
    console.error("Failed to check existing feed", existingError);
    return NextResponse.json({ error: "Failed to validate feed" }, { status: 500 });
  }

  if (existing) {
    return NextResponse.json({ error: "Feed URL already exists" }, { status: 409 });
  }

  const { data: inserted, error: insertError } = await supabase
    .from("rss_feeds")
    .insert({
      name,
      url,
      tags,
      is_active: true
    })
    .select("id, name, url, tags, is_active, last_fetched_at, created_at")
    .single();

  if (insertError || !inserted) {
    console.error("Failed to insert feed", insertError);
    return NextResponse.json({ error: "Failed to create feed" }, { status: 500 });
  }

  return NextResponse.json({ feed: inserted as RssFeed }, { status: 201 });
}

export async function PATCH(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let body: { id?: string; name?: string; url?: string; tags?: string[]; is_active?: boolean };
  try {
    body = await request.json();
  } catch (error) {
    console.error("Failed to parse request body", error);
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.id) {
    return NextResponse.json({ error: "id is required" }, { status: 400 });
  }

  const updates: Record<string, unknown> = {};
  if (body.name !== undefined) updates.name = body.name.trim();
  if (body.url !== undefined) updates.url = body.url.trim();
  if (body.tags !== undefined) updates.tags = normalizeTags(body.tags);
  if (body.is_active !== undefined) updates.is_active = body.is_active;

  const { data, error } = await supabase
    .from("rss_feeds")
    .update(updates)
    .eq("id", body.id)
    .select("id, name, url, tags, is_active, last_fetched_at, created_at")
    .single();

  if (error || !data) {
    console.error("Failed to update feed", error);
    return NextResponse.json({ error: "Failed to update feed" }, { status: 500 });
  }

  return NextResponse.json({ feed: data as RssFeed });
}

export async function DELETE(request: NextRequest) {
  const cookieStore = cookies();
  const supabase = createRouteHandlerClient({ cookies: () => cookieStore });
  const {
    data: { session },
    error: authError
  } = await supabase.auth.getSession();

  if (authError || !session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const url = new URL(request.url);
  const feedId = url.searchParams.get("id");

  if (!feedId) {
    return NextResponse.json({ error: "id is required" }, { status: 400 });
  }

  // RSSフィードに関連するpostsも削除
  const { error: postsError } = await supabase
    .from("posts")
    .delete()
    .eq("metadata->>source", "rss")
    .eq("metadata->>feed_id", feedId);

  if (postsError) {
    console.error("Failed to delete related posts", postsError);
    return NextResponse.json({ error: "Failed to delete related posts" }, { status: 500 });
  }

  // RSSフィードを削除
  const { error: deleteError } = await supabase
    .from("rss_feeds")
    .delete()
    .eq("id", feedId);

  if (deleteError) {
    console.error("Failed to delete feed", deleteError);
    return NextResponse.json({ error: "Failed to delete feed" }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
