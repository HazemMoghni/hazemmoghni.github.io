// Cloudflare Worker — relays the Substack RSS feed so it can be fetched from
// IPs that Substack/Cloudflare blocks (e.g. GitHub Actions runners).
//
// Deploy (free):
//   1. dash.cloudflare.com → Workers & Pages → Create → Worker → name it
//      (e.g. "substack-feed") → Deploy.
//   2. Edit code → replace with this file → Deploy.
//   3. Copy the URL (https://substack-feed.<your-subdomain>.workers.dev) and set it
//      as FEED_URL in .github/workflows/update-writing.yml.
//
// It only ever fetches this one feed, so it is not an open proxy.

const FEED = "https://hazemhasan.substack.com/feed";

export default {
  async fetch() {
    const upstream = await fetch(FEED, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9",
      },
      // cache at Cloudflare's edge for 30 min to be gentle on Substack
      cf: { cacheTtl: 1800, cacheEverything: true },
    });
    return new Response(upstream.body, {
      status: upstream.status,
      headers: {
        "content-type": "application/xml; charset=utf-8",
        "cache-control": "public, max-age=1800",
      },
    });
  },
};
