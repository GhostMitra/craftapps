/**
 * Cloudflare Worker: Reverse Proxy for CraftApps Suite
 * 
 * Maps all craft subdomains (photocraft.debarghaya.in, cadcraft.debarghaya.in, etc.)
 * directly to craftapps.web.app without any browser redirects.
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
  'gridcraft'
];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const targetOrigin = "https://craftapps.web.app";

    // Extract subdomain (e.g., "photocraft" from "photocraft.debarghaya.in")
    const hostParts = url.hostname.split('.');
    const subdomain = hostParts[0].toLowerCase();

    let targetPath = url.pathname;

    // If the subdomain matches any craft application, route into that application's directory
    if (CRAFT_APPS.includes(subdomain)) {
      const targetApp = subdomain;
      if (targetPath !== `/${targetApp}` && !targetPath.startsWith(`/${targetApp}/`)) {
        targetPath = `/${targetApp}` + (targetPath.startsWith('/') ? targetPath : `/${targetPath}`);
      }
    }

    // Build upstream target URL
    const upstreamUrl = new URL(targetPath + url.search, targetOrigin);

    // Rewrite headers: Firebase Hosting requires Host: craftapps.web.app
    const newHeaders = new Headers(request.headers);
    newHeaders.set("Host", "craftapps.web.app");
    newHeaders.set("X-Forwarded-Host", url.hostname);
    newHeaders.set("X-Forwarded-Proto", url.protocol.replace(':', ''));

    const proxyRequest = new Request(upstreamUrl, {
      method: request.method,
      headers: newHeaders,
      body: request.body,
      redirect: "follow"
    });

    const response = await fetch(proxyRequest);

    // Return response preserving all headers, WASM content types, and caching
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set("Access-Control-Allow-Origin", "*");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders
    });
  }
};
