import { DOMParser } from "https://deno.land/x/deno_dom@v0.1.38/deno-dom-wasm.ts";

const REQUEST_TIMEOUT_MS = 5000;

async function fetchWithTimeout(url: string, init: RequestInit = {}, timeout = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

export async function fetchOpenGraphMetadata(url: string) {
  const response = await fetchWithTimeout(url, {
    headers: {
      "User-Agent":
        "Mozilla/5.0 (compatible; PdEKnowledgeBot/1.0; +https://example.com/bot)"
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch URL: ${response.status} ${response.statusText}`);
  }

  const html = await response.text();
  const doc = new DOMParser().parseFromString(html, "text/html");

  if (!doc) {
    return {};
  }

  const getMeta = (name: string) =>
    doc.querySelector(`meta[property="${name}"]`)?.getAttribute("content") ||
    doc.querySelector(`meta[name="${name}"]`)?.getAttribute("content") ||
    undefined;

  const title = getMeta("og:title") || doc.querySelector("title")?.textContent || undefined;
  const description =
    getMeta("og:description") ||
    doc.querySelector("meta[name=description]")?.getAttribute("content") ||
    undefined;
  const image = getMeta("og:image");

  return {
    title,
    description,
    image
  };
}

