/**
 * Cloudflare Worker: Reverse Proxy & Router for CraftApps Suite
 * 
 * 1. App Subdomains:
 *    Maps photocraft.debarghaya.in, cadcraft.debarghaya.in, etc.
 *    directly to craftapps.web.app/photocraft/ without browser redirects.
 * 
 * 2. Portal App Subroute Redirects:
 *    apps.debarghaya.in/photocraft (or /photocraft/) redirects 301 to photocraft.debarghaya.in/
 * 
 * 3. Portal Dashboard Link Rewriting:
 *    On apps.debarghaya.in, dashboard app links
 *    are rewritten to point to their respective custom subdomains.
 */

const CRAFT_APPS = [
  'wordcraft',
  'photocraft',
  'vectorcraft',
  'cadcraft',
  'designcraft',
  'filmcraft',
  'effectcraft',
  'soundcraft',
  'lightcraft',
  'pdfcraft',
  'deckcraft',
  'gridcraft',
  'figcraft',
  'solidcraft',
  'fieldcraft',
  'materialcraft',
  'texturecraft',
  'craft-anything',
  'craftanything',
  'feildcraft',
  'anicraft',
  'pcbcraft',
  'mailcraft',
];

const APP_ALIASES = {
  'craftanything': 'craft-anything',
  'feildcraft': 'fieldcraft',
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetOrigin = "https://craftapps.web.app";
    const buildId = env?.BUILD_ID || "main";

    // Extract subdomain (e.g. "photocraft", "apps")
    const hostParts = url.hostname.split('.');
    const subdomain = hostParts[0].toLowerCase();
    const rootDomain = hostParts.length >= 2 ? hostParts.slice(1).join('.') : 'debarghaya.in';

    // 1. Direct App Subdomain (e.g. photocraft.debarghaya.in)
    // Silent reverse-proxy to craftapps.web.app/photocraft/ with no redirect
    if (CRAFT_APPS.includes(subdomain)) {
      const targetApp = APP_ALIASES[subdomain] || subdomain;

      // Font manifest: immediately return 200 with comment so browser does not 404 or make redundant upstream request
      if (url.pathname === '/fonts/manifest.txt' || url.pathname.endsWith('/fonts/manifest.txt')) {
        return new Response('# No served fonts\n', {
          status: 200,
          headers: {
            'Content-Type': 'text/plain; charset=utf-8',
            'Cache-Control': 'public, max-age=31536000, immutable',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      let targetPath = url.pathname;
      if (targetPath !== `/${targetApp}` && !targetPath.startsWith(`/${targetApp}/`)) {
        targetPath = `/${targetApp}` + (targetPath.startsWith('/') ? targetPath : `/${targetPath}`);
      }
      let response = await proxyUpstream(request, new URL(targetPath + url.search, targetOrigin), buildId);

      // Snippet resolution fallback: handle /app/snippets vs /snippets differences
      if (response.status === 404 && targetPath.includes('/snippets/')) {
        const altPath = targetPath.includes('/app/snippets/')
          ? targetPath.replace('/app/snippets/', '/snippets/')
          : targetPath.replace('/snippets/', '/app/snippets/');
        const altResp = await proxyUpstream(request, new URL(altPath + url.search, targetOrigin), buildId);
        if (altResp.ok) {
          response = altResp;
        }
      }

      // Favicon fallback: if /favicon.ico is requested and 404s, serve the app's SVG icon from /icons/${targetApp}.svg
      if (response.status === 404 && targetPath.endsWith('/favicon.ico')) {
        const iconResp = await proxyUpstream(request, new URL(`/icons/${targetApp}.svg`, targetOrigin), buildId);
        if (iconResp.ok) {
          response = iconResp;
        }
      }

      // Strip SRI integrity hashes and Cloudflare insights scripts from HTML to prevent browser false-positives on cached or proxied assets
      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("text/html")) {
        const rewriter = new HTMLRewriter()
          .on('head', {
            element(element) {
              element.append('<script>window.__cfBeacon = false;</script>', { html: true });
            }
          })
          .on('link[integrity]', {
            element(element) {
              element.removeAttribute('integrity');
            }
          })
          .on('script[integrity]', {
            element(element) {
              element.removeAttribute('integrity');
            }
          })
          .on('script', {
            element(element) {
              const src = element.getAttribute('src') || '';
              if (src.includes('cloudflareinsights') || src.includes('beacon.min.js')) {
                element.remove();
              }
            }
          });
        return rewriter.transform(response);
      }

      return response;
    }

    // 2. Portal Subroute Redirect (e.g. apps.debarghaya.in/photocraft -> photocraft.debarghaya.in/)
    const pathParts = url.pathname.split('/').filter(Boolean);
    const firstSegment = pathParts[0]?.toLowerCase();

    if (CRAFT_APPS.includes(firstSegment)) {
      const canonicalApp = APP_ALIASES[firstSegment] || firstSegment;
      const remainingSegments = pathParts.slice(1);
      const remainingPath = remainingSegments.length > 0 ? '/' + remainingSegments.join('/') : '/';
      const redirectUrl = `https://${canonicalApp}.${rootDomain}${remainingPath}${url.search}`;
      return Response.redirect(redirectUrl, 301);
    }

    // 3. Portal Root & Assets (e.g. apps.debarghaya.in/)
    const upstreamUrl = new URL(url.pathname + url.search, targetOrigin);
    const response = await proxyUpstream(request, upstreamUrl, buildId);

    // If serving HTML dashboard on a portal domain, rewrite app links to custom subdomains and strip SRI integrity tags
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("text/html")) {
      const rewriter = new HTMLRewriter()
        .on('head', {
          element(element) {
            element.append('<script>window.__cfBeacon = false;</script>', { html: true });
          }
        })
        .on('a.app-link[data-app]', {
          element(element) {
            const app = element.getAttribute('data-app');
            if (app && CRAFT_APPS.includes(app)) {
              element.setAttribute('href', `https://${app}.${rootDomain}/`);
            }
          }
        })
        .on('link[integrity]', {
          element(element) {
            element.removeAttribute('integrity');
          }
        })
        .on('script[integrity]', {
          element(element) {
            element.removeAttribute('integrity');
          }
        })
        .on('script', {
          element(element) {
            const src = element.getAttribute('src') || '';
            if (src.includes('cloudflareinsights') || src.includes('beacon.min.js')) {
              element.remove();
            }
          }
        });
      return rewriter.transform(response);
    }

    return response;
  }
};

async function proxyUpstream(request, upstreamUrl, buildId = "main") {
  const newHeaders = new Headers(request.headers);
  newHeaders.set("Host", "craftapps.web.app");
  newHeaders.set("X-Forwarded-Host", new URL(request.url).hostname);
  newHeaders.set("X-Forwarded-Proto", new URL(request.url).protocol.replace(':', ''));

  const isPartAsset = upstreamUrl.pathname.includes('.part-');
  const isStaticAsset = isPartAsset || /\.(wasm|js|png|jpg|jpeg|svg|css|woff2|ico|zip|txt)$/i.test(upstreamUrl.pathname);
  // Detect content-hashed assets (e.g. *-fc25e1aa1ee3b046.js, *-fc25e1aa1ee3b046_bg.wasm, or .part-*)
  const isContentHashed = isPartAsset || /[-._][a-f0-9]{8,32}[_.]/i.test(upstreamUrl.pathname);

  const fetchOptions = {
    method: request.method,
    headers: newHeaders,
    body: request.body,
    redirect: "follow",
  };

  // Cache static WebAssembly binaries, JS glue, and media assets at Cloudflare's Edge CDN.
  // The cache key is segmented by buildId so that when a new build is deployed,
  // Cloudflare's Edge CDN immediately fetches and caches the new build assets.
  if (isStaticAsset) {
    const cacheKey = `${upstreamUrl.origin}${upstreamUrl.pathname}?b=${buildId}`;
    fetchOptions.cf = {
      cacheEverything: true,
      cacheKey: cacheKey,
      cacheTtlByStatus: {
        "200-299": 31536000, // 1 year edge cache for active build assets
        "404": 0,            // Do NOT cache 404 responses
        "500-599": 0         // Do NOT cache 5xx server errors
      }
    };
  }

  const proxyRequest = new Request(upstreamUrl, fetchOptions);
  const response = await fetch(proxyRequest);

  const responseHeaders = new Headers(response.headers);
  responseHeaders.set("Access-Control-Allow-Origin", "*");
  responseHeaders.set("X-CraftApps-Build", buildId);

  // Ensure correct MIME types for WebAssembly, JavaScript, and binary parts
  if (upstreamUrl.pathname.endsWith(".wasm") && response.ok) {
    responseHeaders.set("Content-Type", "application/wasm");
  } else if (upstreamUrl.pathname.endsWith(".js") && response.ok) {
    responseHeaders.set("Content-Type", "text/javascript; charset=utf-8");
  } else if (isPartAsset && response.ok) {
    responseHeaders.set("Content-Type", "application/octet-stream");
  } else if (upstreamUrl.pathname.endsWith("parts.txt") && response.ok) {
    responseHeaders.set("Content-Type", "text/plain; charset=utf-8");
  }

  const rawContentType = (responseHeaders.get("Content-Type") || "").toLowerCase();
  const isHtml = rawContentType.includes("text/html") || upstreamUrl.pathname.endsWith(".html") || upstreamUrl.pathname.endsWith("/");

  if (isHtml) {
    // HTML is cached with conditional ETag revalidation.
    // Client browsers cache the HTML locally, but send a lightweight 304 revalidation check.
    // When a new build is pushed, the HTML updates and delivers new asset references.
    // Clear-Site-Data is explicitly omitted so client browsers retain cached assets across sessions.
    // no-transform strictly prevents Cloudflare Edge from injecting beacon.min.js or altering body.
    responseHeaders.set("Cache-Control", "public, no-cache, no-transform, must-revalidate");
  } else if (isContentHashed && response.ok) {
    // Content-hashed assets have unique fingerprints in their filenames (e.g. Trunk wasm/js hashes).
    // Safe to cache immutably in the browser for maximum performance until a new build references new hashes.
    responseHeaders.set("Cache-Control", "public, max-age=31536000, immutable");
  } else if (isStaticAsset && response.ok) {
    // Unhashed static assets (e.g. /icons/*.svg, favicon.ico) are cached locally and revalidated with ETag.
    responseHeaders.set("Cache-Control", "public, no-cache, must-revalidate");
  } else if (!response.ok) {
    responseHeaders.set("Cache-Control", "no-store, no-cache, must-revalidate");
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}
