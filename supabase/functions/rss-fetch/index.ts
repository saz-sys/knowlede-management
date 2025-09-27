// deno-lint-ignore-file no-explicit-any
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.46.1";
import Parser from "https://esm.sh/rss-parser@3.13.0";
import { fetchOpenGraphMetadata } from "../_shared/open-graph.ts";

interface FeedConfig {
  id: string;
  name: string | null;
  url: string;
  tags: string[] | null;
  is_active: boolean;
}

interface FetchResult {
  inserted: number;
  skipped: number;
  errors: number;
}

const parser = new Parser();

async function summarizeContent(content: string | undefined, length = 240) {
  if (!content) return null;
  const plain = content.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  return plain.slice(0, length) + (plain.length > length ? "…" : "");
}

function createSupabaseClient() {
  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

  if (!url || !serviceKey) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
  }

  return createClient(url, serviceKey, {
    auth: {
      persistSession: false
    }
  });
}

async function fetchFeeds(supabase: ReturnType<typeof createSupabaseClient>) {
  const { data, error } = await supabase
    .from("rss_feeds")
    .select("id, name, url, tags, is_active")
    .eq("is_active", true);

  if (error) {
    throw new Error(`Failed to fetch rss_feeds: ${error.message}`);
  }

  return (data ?? []) as FeedConfig[];
}

async function ensureTags(
  supabase: ReturnType<typeof createSupabaseClient>,
  tags: string[]
) {
  if (!tags.length) return [];

  const tagPayload = tags.map((tagName) => ({ name: tagName, description: null }));
  const { data, error } = await supabase
    .from("tags")
    .upsert(tagPayload, { onConflict: "name" })
    .select("id, name");

  if (error) {
    console.error("Tag upsert failed", error);
    return [];
  }

  return data ?? [];
}

async function linkPostTags(
  supabase: ReturnType<typeof createSupabaseClient>,
  postId: string,
  tagIds: string[]
) {
  if (!tagIds.length) return;

  const payload = tagIds.map((tagId) => ({ post_id: postId, tag_id: tagId }));
  const { error } = await supabase
    .from("post_tags")
    .upsert(payload, { onConflict: "post_id,tag_id" });

  if (error) {
    console.error("Failed to link post tags", error);
  }
}

async function processFeed(
  supabase: ReturnType<typeof createSupabaseClient>,
  feed: FeedConfig
): Promise<FetchResult> {
  const feedResult: FetchResult = { inserted: 0, skipped: 0, errors: 0 };

  try {
    const parsed = await parser.parseURL(feed.url);

    if (!parsed.items?.length) {
      return feedResult;
    }

    for (const item of parsed.items) {
      if (!item.link || !item.title) {
        feedResult.skipped += 1;
        continue;
      }

      const { data: existing, error: existingError } = await supabase
        .from("posts")
        .select("id")
        .ilike("url", item.link)
        .maybeSingle();

      if (existingError) {
        console.error("Failed checking existing post", existingError);
        feedResult.errors += 1;
        continue;
      }

      if (existing) {
        feedResult.skipped += 1;
        continue;
      }

      let summary = await summarizeContent(item.contentSnippet || item.content);
      let ogImage: string | undefined;

      if (!summary) {
        try {
          const og = await fetchOpenGraphMetadata(item.link);
          summary = og.description ?? null;
          ogImage = og.image;
        } catch (metaError) {
          console.warn("Failed to fetch OG metadata", metaError);
        }
      }

      const tagSuggestions = new Set<string>();
      feed.tags?.forEach((tag) => tagSuggestions.add(tag));
      if (Array.isArray(item.categories)) {
        item.categories
          .map((tag) => tag?.trim())
          .filter((tag): tag is string => !!tag && tag.length > 0)
          .forEach((tag) => tagSuggestions.add(tag));
      }

      const { data: post, error: postError } = await supabase
        .from("posts")
        .insert({
          author_id: feed.id,
          author_email: "rss@autogen",
          title: item.title,
          url: item.link,
          summary,
          content: item.contentSnippet || item.content || null,
          notified_channels: [],
          metadata: {
            source: "rss",
            og_image: ogImage ?? null,
            feed_id: feed.id,
            feed_name: feed.name
          }
        })
        .select("id")
        .single();

      if (postError || !post) {
        console.error("Failed to create post from RSS", postError);
        feedResult.errors += 1;
        continue;
      }

      const tags = Array.from(tagSuggestions);
      const upsertedTags = await ensureTags(supabase, tags);
      await linkPostTags(
        supabase,
        post.id,
        upsertedTags.map((tag) => tag.id)
      );

      feedResult.inserted += 1;
    }
  } catch (error) {
    console.error(`Failed to process feed ${feed.url}`, error);
    feedResult.errors += 1;
  }

  return feedResult;
}

export default async function handler(req: Request) {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const supabase = createSupabaseClient();

  try {
    const feeds = await fetchFeeds(supabase);

    if (!feeds.length) {
      return new Response(JSON.stringify({ message: "No active feeds" }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    const results: Record<string, FetchResult> = {};

    for (const feed of feeds) {
      results[feed.id] = await processFeed(supabase, feed);
    }

    return new Response(JSON.stringify({ results }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("RSS fetch failed", error);
    return new Response(
      JSON.stringify({ error: "RSS fetch failed", details: String(error) }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}

