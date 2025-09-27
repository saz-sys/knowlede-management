// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.46.1";

const REQUEST_TIMEOUT_MS = 10000;

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

async function fetchWithTimeout(url: string, init: RequestInit = {}, timeout = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

Deno.serve(async (req) => {
  const start = Date.now();
  console.log("[rss-fetch] Handler invoked", {
    method: req.method,
    url: req.url
  });

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, reason: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" }
    });
  }

  const supabase = createSupabaseClient();

  try {
    const url = new URL(req.url);
    const bodyText = await req.text().catch(() => "{}");
    const body = bodyText ? JSON.parse(bodyText || "{}") : {};
    const feedId = body?.feed_id ?? url.searchParams.get("feed_id") ?? null;

    console.log("[rss-fetch] Resolving feed", { feedId });

    const query = supabase
      .from("rss_feeds")
      .select("id, name, url, last_fetched_at, last_etag, last_modified")
      .eq("is_active", true)
      .order("last_fetched_at", { ascending: true })
      .limit(1);

    if (feedId) {
      query.eq("id", feedId);
    }

    const { data, error } = await query.maybeSingle();

    if (error) {
      console.error("[rss-fetch] Failed to load feed", error);
      return new Response(
        JSON.stringify({ ok: false, error: "Failed to load feed", details: error.message }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    if (!data) {
      return new Response(
        JSON.stringify({ ok: true, message: "No active feed found", feedId }),
        {
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    console.log("[rss-fetch] Downloading feed", { feedId: data.id, url: data.url });

    const headers: Record<string, string> = {
      "User-Agent": "PdEKnowledgeBot/1.0 (+https://example.com/bot)",
      Accept: "application/rss+xml, application/xml;q=0.9, */*;q=0.8"
    };

    if (data.last_etag) {
      headers["If-None-Match"] = data.last_etag;
    }
    if (data.last_modified) {
      headers["If-Modified-Since"] = data.last_modified;
    }

    const downloadStart = Date.now();

    const response = await fetchWithTimeout(data.url, { headers });

    if (response.status === 304) {
      const duration = Date.now() - start;
      console.log("[rss-fetch] Feed not modified", { feedId: data.id, duration });
      return new Response(
        JSON.stringify({
          ok: true,
          duration,
          feed: data,
          download: {
            status: 304,
            reason: "Not Modified"
          }
        }),
        {
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    if (!response.ok) {
      console.error("[rss-fetch] Failed to download feed", { feedId: data.id, status: response.status });
      return new Response(
        JSON.stringify({
          ok: false,
          error: "Failed to download feed",
          details: `${response.status} ${response.statusText}`
        }),
        {
          status: 502,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    const xml = await response.text();
    const downloadDuration = Date.now() - downloadStart;

    console.log("[rss-fetch] Feed downloaded", {
      feedId: data.id,
      status: response.status,
      downloadDuration,
      length: xml.length
    });

    const duration = Date.now() - start;

    return new Response(
      JSON.stringify({
        ok: true,
        duration,
        feed: data,
        download: {
          status: response.status,
          duration: downloadDuration,
          length: xml.length,
          etag: response.headers.get("etag"),
          lastModified: response.headers.get("last-modified"),
          sample: xml.slice(0, 2000)
        }
      }),
      {
        headers: { "Content-Type": "application/json" }
      }
    );
  } catch (error) {
    console.error("[rss-fetch] Unexpected error", error);
    return new Response(
      JSON.stringify({ ok: false, error: "Unexpected error", details: String(error) }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
});