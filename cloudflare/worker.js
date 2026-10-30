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
  'pcbcraft'
];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetOrigin = "https://craftapps.web.app";

    // Extract subdomain (e.g. "photocraft", "apps")
    const hostParts = url.hostname.split('.');
    const subdomain = hostParts[0].toLowerCase();
    const rootDomain = hostParts.length >= 2 ? hostParts.slice(1).join('.') : 'debarghaya.in';

    // 1. Direct App Subdomain (e.g. photocraft.debarghaya.in)
    // Silent reverse-proxy to craftapps.web.app/photocraft/ with no redirect
    if (CRAFT_APPS.includes(subdomain)) {
      const targetApp = subdomain;
      let targetPath = url.pathname;
      if (targetPath !== `/${targetApp}` && !targetPath.startsWith(`/${targetApp}/`)) {
        targetPath = `/${targetApp}` + (targetPath.startsWith('/') ? targetPath : `/${targetPath}`);
      }
      return proxyUpstream(request, new URL(targetPath + url.search, targetOrigin));
    }

    // 2. Portal Subroute Redirect (e.g. apps.debarghaya.in/photocraft -> photocraft.debarghaya.in/)
    const pathParts = url.pathname.split('/').filter(Boolean);
    const firstSegment = pathParts[0]?.toLowerCase();

    if (CRAFT_APPS.includes(firstSegment)) {
      const remainingSegments = pathParts.slice(1);
      const remainingPath = remainingSegments.length > 0 ? '/' + remainingSegments.join('/') : '/';
      const redirectUrl = `https://${firstSegment}.${rootDomain}${remainingPath}${url.search}`;
      return Response.redirect(redirectUrl, 301);
    }

    // 3. Portal Root & Assets (e.g. apps.debarghaya.in/)
    const upstreamUrl = new URL(url.pathname + url.search, targetOrigin);
    const response = await proxyUpstream(request, upstreamUrl);

    // If serving HTML dashboard on a portal domain, rewrite app links to custom subdomains
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("text/html")) {
      const rewriter = new HTMLRewriter().on('a.app-link[data-app]', {
        element(element) {
          const app = element.getAttribute('data-app');
          if (app && CRAFT_APPS.includes(app)) {
            element.setAttribute('href', `https://${app}.${rootDomain}/`);
          }
        }
      });
      return rewriter.transform(response);
    }

    return response;
  }
};

async function proxyUpstream(request, upstreamUrl) {
  const newHeaders = new Headers(request.headers);
  newHeaders.set("Host", "craftapps.web.app");
  newHeaders.set("X-Forwarded-Host", new URL(request.url).hostname);
  newHeaders.set("X-Forwarded-Proto", new URL(request.url).protocol.replace(':', ''));

  const isStaticAsset = /\.(wasm|js|png|jpg|jpeg|svg|css|woff2|ico|zip)$/i.test(upstreamUrl.pathname);

  const fetchOptions = {
    method: request.method,
    headers: newHeaders,
    body: request.body,
    redirect: "follow",
  };

  // Cache static WebAssembly binaries, JS glue, and media assets at Cloudflare's Edge CDN.
  // This drastically reduces Firebase Hosting download bandwidth quota by serving static assets from edge cache.
  if (isStaticAsset) {
    fetchOptions.cf = {
      cacheEverything: true,
      cacheTtl: 31536000, // 1 year edge cache
    };
  }

  const proxyRequest = new Request(upstreamUrl, fetchOptions);
  const response = await fetch(proxyRequest);

  const responseHeaders = new Headers(response.headers);
  responseHeaders.set("Access-Control-Allow-Origin", "*");

  if (isStaticAsset) {
    responseHeaders.set("Cache-Control", "public, max-age=31536000, immutable");
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders
  });
}
