// Deployed manually to the substack-feed Cloudflare Worker.
const FEED = "https://hazemhasan.substack.com/feed";
export default {
  async fetch() {
    const upstream = await fetch(FEED, {
      headers: {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9",
      },
      cf: { cacheEverything: true, cacheTtlByStatus: { "200-299": 1800, "300-599": -1 } },
    });
    const headers = new Headers({
      "content-type": upstream.headers.get("content-type") || "application/xml; charset=utf-8",
      "cache-control": upstream.ok ? "public, max-age=1800" : "no-store",
    });
    const retryAfter = upstream.headers.get("retry-after");
    if (retryAfter) headers.set("retry-after", retryAfter);
    return new Response(upstream.body, { status: upstream.status, headers });
  },
};
