// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.46.1";
import Parser from "https://esm.sh/rss-parser@3.13.0";

interface FeedConfig {
  id: string;
  name: string | null;
  url: string;
  tags: string[] | null;
  is_active: boolean;
  last_etag: string | null;
  last_modified: string | null;
}

interface FetchResult {
  inserted: number;
  skipped: number;
  errors: number;
  status: number;
}

interface FeedDownload {
  xml: string | null;
  etag: string | null;
  lastModified: string | null;
  status: number;
}

const REQUEST_TIMEOUT_MS = 10000;
const MAX_FEEDS_PER_RUN = 10;
const MAX_ITEMS_PER_FEED = 50;

function createSupabaseClient() {
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  
  return createClient(supabaseUrl, supabaseServiceKey);
}

const parser = new Parser();

type SupabaseClient = ReturnType<typeof createSupabaseClient>;

async function fetchFeeds(supabase: SupabaseClient, targetFeedId: string | null): Promise<FeedConfig[]> {
  if (targetFeedId) {
    const { data, error } = await supabase
      .from("rss_feeds")
      .select("id, name, url, tags, is_active, last_etag, last_modified")
      .eq("id", targetFeedId)
      .eq("is_active", true)
      .limit(1)
      .maybeSingle();

    if (error) {
      throw new Error(`Failed to fetch target feed: ${error.message}`);
    }

    return data ? [data as FeedConfig] : [];
  }

  // 1時間以内に更新されていないフィードを取得
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

  const { data, error } = await supabase
    .from("rss_feeds")
    .select("id, name, url, tags, is_active, last_etag, last_modified")
    .eq("is_active", true)
    .or(`last_fetched_at.is.null,last_fetched_at.lt.${oneHourAgo.toISOString()}`)
    .order("last_fetched_at", { ascending: true })
    .limit(MAX_FEEDS_PER_RUN);

  if (error) {
    throw new Error(`Failed to fetch rss_feeds: ${error.message}`);
  }

  return (data ?? []) as FeedConfig[];
}

async function downloadFeed(feed: FeedConfig): Promise<FeedDownload> {
  const headers: Record<string, string> = {
    "User-Agent": "PdEKnowledgeBot/1.0 (+https://example.com/bot)"
  };

  if (feed.last_etag) {
    headers["If-None-Match"] = feed.last_etag;
  }

  if (feed.last_modified) {
    headers["If-Modified-Since"] = feed.last_modified;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(feed.url, {
      method: "GET",
      headers,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    const xml = response.status === 200 ? await response.text() : null;
    const etag = response.headers.get("etag");
    const lastModified = response.headers.get("last-modified");

    return {
      xml,
      etag,
      lastModified,
      status: response.status
    };
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

async function updateFeedHeaders(
  supabase: SupabaseClient,
  feedId: string,
  etag: string | null,
  lastModified: string | null
) {
  const { error } = await supabase
    .from("rss_feeds")
    .update({
      last_etag: etag,
      last_modified: lastModified,
      last_fetched_at: new Date().toISOString()
    })
    .eq("id", feedId);

  if (error) {
    console.error("[rss-fetch] Failed to update feed headers", error);
  }
}

async function processFeed(supabase: SupabaseClient, feed: FeedConfig): Promise<FetchResult> {
  const result: FetchResult = { inserted: 0, skipped: 0, errors: 0, status: 200 };
  console.log("[rss-fetch] Processing feed", { id: feed.id, url: feed.url });

  try {
    const download = await downloadFeed(feed);

    if (download.status === 304 || !download.xml) {
      console.log("[rss-fetch] No changes", { id: feed.id });
      await updateFeedHeaders(supabase, feed.id, download.etag, download.lastModified);
      result.status = 304;
      return result;
    }

    const parsed = await parser.parseString(download.xml);
    const items = (parsed.items ?? [])
      .filter((item) => item?.link && item?.title)
      .slice(0, MAX_ITEMS_PER_FEED);

    if (!items.length) {
      console.log("[rss-fetch] No valid items", { id: feed.id });
      await updateFeedHeaders(supabase, feed.id, download.etag, download.lastModified);
      return result;
    }

    const urls = items.map((item) => item.link as string);

    const { data: existing, error: existingError } = await supabase
      .from("posts")
      .select("url")
      .eq("metadata->>source", "rss")
      .eq("metadata->>feed_id", feed.id)
      .in("url", urls);

    if (existingError) {
      throw new Error(`Failed to check existing posts: ${existingError.message}`);
    }

    const existingUrls = new Set((existing ?? []).map((row) => row.url));
    const newItems = items.filter((item) => !existingUrls.has(item.link as string));

    if (!newItems.length) {
      console.log("[rss-fetch] All items already exist", { id: feed.id });
      result.skipped = items.length;
      await updateFeedHeaders(supabase, feed.id, download.etag, download.lastModified);
      return result;
    }

    const rows = newItems.map((item) => {
      const publishedAt = (item as Record<string, unknown>).isoDate ?? item.pubDate ?? null;

      return {
        author_id: feed.id,
        author_email: "rss@autogen",
        title: item.title as string,
        url: item.link as string,
        content: item.contentSnippet ?? null,
        metadata: {
          source: "rss",
          feed_id: feed.id,
          feed_name: feed.name,
          original_guid: item.guid ?? null,
          published_at: publishedAt,
          categories: Array.isArray(item.categories) ? item.categories : null
        }
      };
    });

    const { data: inserted, error: insertError } = await supabase
      .from("posts")
      .insert(rows)
      .select("id");

    if (insertError) {
      throw new Error(`Failed to insert posts: ${insertError.message}`);
    }

    // RSSフィードのnameとtagsをpostsのtagsに追加
    if (inserted && inserted.length > 0) {
      const postIds = inserted.map(row => row.id);
      const tagsToAdd = [];
      
      // RSSフィードのnameをタグとして追加
      if (feed.name) {
        tagsToAdd.push(feed.name);
      }
      
      // RSSフィードのtagsを追加
      if (feed.tags && Array.isArray(feed.tags)) {
        tagsToAdd.push(...feed.tags);
      }
      
      if (tagsToAdd.length > 0) {
        // タグを取得または作成
        const tagPromises = tagsToAdd.map(async (tagName) => {
          const { data: existingTag } = await supabase
            .from("tags")
            .select("id")
            .eq("name", tagName)
            .single();
          
          if (existingTag) {
            return existingTag.id;
          }
          
          const { data: newTag, error: tagError } = await supabase
            .from("tags")
            .insert({ name: tagName })
            .select("id")
            .single();
          
          if (tagError) {
            console.error(`Failed to create tag ${tagName}:`, tagError);
            return null;
          }
          
          return newTag.id;
        });
        
        const tagIds = (await Promise.all(tagPromises)).filter(Boolean);
        
        // 投稿とタグの関連を作成
        if (tagIds.length > 0) {
          const postTagRelations = [];
          for (const postId of postIds) {
            for (const tagId of tagIds) {
              postTagRelations.push({
                post_id: postId,
                tag_id: tagId
              });
            }
          }
          
          if (postTagRelations.length > 0) {
            const { error: relationError } = await supabase
              .from("post_tags")
              .insert(postTagRelations);
            
            if (relationError) {
              console.error("Failed to create post-tag relations:", relationError);
            }
          }
        }
      }
      
      result.inserted = inserted.length;
    }

    await updateFeedHeaders(supabase, feed.id, download.etag, download.lastModified);

    console.log("[rss-fetch] Feed processed", {
      id: feed.id,
      inserted: result.inserted,
      skipped: result.skipped
    });

    return result;
  } catch (error) {
    console.error("[rss-fetch] Failed to process feed", {
      id: feed.id,
      error: error
    });

    result.errors += 1;
    result.status = 500;
    return result;
  }
}

Deno.serve(async (req) => {
  const start = Date.now();
  console.log("[rss-fetch] Handler invoked", {
    method: req.method,
    url: req.url,
    headers: Object.fromEntries(req.headers.entries())
  });

  // GETリクエストも許可（cron実行時の互換性のため）
  if (req.method !== "POST" && req.method !== "GET") {
    return new Response(JSON.stringify({ ok: false, reason: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" }
    });
  }

  const supabase = createSupabaseClient();

  try {
    const url = new URL(req.url);
    let body = {};
    
    // POSTリクエストの場合のみボディを解析
    if (req.method === "POST") {
      try {
        const bodyText = await req.text();
        body = bodyText ? JSON.parse(bodyText) : {};
      } catch (error) {
        console.warn("[rss-fetch] Failed to parse request body", error);
      }
    }
    
    const feedId = body?.feed_id ?? url.searchParams.get("feed_id") ?? null;

    const feeds = await fetchFeeds(supabase, feedId);

    if (!feeds.length) {
      return new Response(
        JSON.stringify({ ok: true, message: "No active feeds" }),
        {
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    const results: Record<string, FetchResult> = {};

    for (const feed of feeds) {
      results[feed.id] = await processFeed(supabase, feed);
    }

    const duration = Date.now() - start;

    return new Response(
      JSON.stringify({
        ok: true,
        duration,
        feeds: feeds.map((feed) => ({ id: feed.id, url: feed.url })),
        results
      }),
      {
        headers: { "Content-Type": "application/json" }
      }
    );
  } catch (error) {
    console.error("[rss-fetch] Unexpected error", error);
    return new Response(
      JSON.stringify({ ok: false, error: error.message }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
});