/**
 * Cloudflare Worker: Reverse Proxy for CraftApps
 * 
 * Maps wordcraft.debarghaya.in (and other craft subdomains) to craftapps.web.app
 * without any browser redirects (URL stays on your custom domain).
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

    // Detect app from subdomain (e.g. "wordcraft" from "wordcraft.debarghaya.in")
    const hostParts = url.hostname.split('.');
    const subdomain = hostParts[0].toLowerCase();

    // Determine target app: either matched subdomain or default to wordcraft
    const targetApp = CRAFT_APPS.includes(subdomain) ? subdomain : 'wordcraft';

    let targetPath = url.pathname;

    // Check if the path is already prefixed with "/<app>/" or equals "/<app>"
    // Note: requires trailing slash check so "/wordcraft-web-*.js" correctly becomes "/wordcraft/wordcraft-web-*.js"
    if (targetPath !== `/${targetApp}` && !targetPath.startsWith(`/${targetApp}/`)) {
      targetPath = `/${targetApp}` + (targetPath.startsWith('/') ? targetPath : `/${targetPath}`);
    }

    // Build the upstream destination URL
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
