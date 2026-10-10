#!/usr/bin/env python3
"""
Sync Upstream Releases for CraftApps Suite
Checks storytold/* repositories for new web releases, downloads and extracts them,
and patches index.html with debarghaya.in custom subdomain routing.
"""

import os
import sys
import json
import re
import urllib.request
import zipfile
import tempfile
import shutil
from pathlib import Path

APPS = [
    'cadcraft',
    'deckcraft',
    'designcraft',
    'effectcraft',
    'filmcraft',
    'gridcraft',
    'lightcraft',
    'pdfcraft',
    'photocraft',
    'soundcraft',
    'vectorcraft',
    'wordcraft'
]

ROOT_DIR = Path(__file__).resolve().parent.parent
VERSIONS_FILE = ROOT_DIR / "versions.json"

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "CraftApps-Upstream-Syncer",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def load_versions():
    if VERSIONS_FILE.exists():
        with open(VERSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_versions(versions):
    with open(VERSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(versions, f, indent=2, sort_keys=True)
        f.write("\n")

def fetch_latest_release(app_name):
    url = f"https://api.github.com/repos/storytold/{app_name}/releases/latest"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[{app_name}] Failed to fetch release metadata: {e}")
        return None

def find_web_asset(release_data, app_name):
    assets = release_data.get("assets", [])
    for asset in assets:
        name = asset.get("name", "")
        if f"{app_name}-web-" in name and name.endswith(".zip"):
            return asset
    # Fallback to any *-web-*.zip
    for asset in assets:
        name = asset.get("name", "")
        if "-web-" in name and name.endswith(".zip"):
            return asset
    return None

def patch_index_html(app_dir, app_name):
    index_path = app_dir / "index.html"
    if not index_path.exists():
        print(f"[{app_name}] Warning: index.html not found in {app_dir}")
        return

    content = index_path.read_text(encoding="utf-8")

    redirect_script = f"""  <script>
    if (location.hostname.endsWith('.web.app') || location.hostname.endsWith('.firebaseapp.com')) {{
      location.replace('https://{app_name}.debarghaya.in' + location.pathname.replace(/^\\/{app_name}/i, '') + location.search + location.hash);
    }}
  </script>
  <link rel="canonical" href="https://{app_name}.debarghaya.in/">"""

    # Check if redirect script is already present
    if f"{app_name}.debarghaya.in" in content and "location.replace" in content:
        print(f"[{app_name}] index.html redirect script already in place")
        return

    # Inject after <meta name="viewport" ...> or inside <head>
    viewport_match = re.search(r'(<meta[^>]*viewport[^>]*>)', content, re.IGNORECASE)
    if viewport_match:
        content = content[:viewport_match.end()] + "\n" + redirect_script + content[viewport_match.end():]
    else:
        head_match = re.search(r'(<head[^>]*>)', content, re.IGNORECASE)
        if head_match:
            content = content[:head_match.end()] + "\n" + redirect_script + content[head_match.end():]
        else:
            content = redirect_script + "\n" + content

    index_path.write_text(content, encoding="utf-8")
    print(f"[{app_name}] Successfully patched index.html with domain routing")

def update_app(app_name, download_url, target_dir):
    print(f"[{app_name}] Downloading {download_url}...")
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_zip_path = tmp_file.name

    try:
        req = urllib.request.Request(download_url, headers=get_headers())
        with urllib.request.urlopen(req) as response, open(tmp_zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        print(f"[{app_name}] Extracting to {target_dir}...")
        target_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
            # Extract files
            zip_ref.extractall(target_dir)

        # Patch index.html
        patch_index_html(target_dir, app_name)

    finally:
        if os.path.exists(tmp_zip_path):
            os.remove(tmp_zip_path)

def main():
    force = "--force" in sys.argv
    check_only = "--check-only" in sys.argv

    versions = load_versions()
    updated_apps = []

    print(f"Checking for updates across {len(APPS)} CraftApps...")

    for app in APPS:
        current_version = versions.get(app, "none")
        release_data = fetch_latest_release(app)
        if not release_data:
            continue

        latest_tag = release_data.get("tag_name")
        if not latest_tag:
            continue

        asset = find_web_asset(release_data, app)
        if not asset:
            print(f"[{app}] No web release asset found for tag {latest_tag}")
            continue

        if latest_tag != current_version or force:
            print(f"[{app}] Update available: {current_version} -> {latest_tag}")
            if not check_only:
                app_dir = ROOT_DIR / app
                update_app(app, asset["browser_download_url"], app_dir)
                versions[app] = latest_tag
                updated_apps.append(f"{app} ({latest_tag})")
        else:
            print(f"[{app}] Up to date: {latest_tag}")

    if updated_apps and not check_only:
        save_versions(versions)
        summary = ", ".join(updated_apps)
        print(f"\nCompleted updates: {summary}")
        
        # Write to GITHUB_OUTPUT if running in GitHub Actions
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write("updated=true\n")
                f.write(f"summary={summary}\n")
    else:
        print("\nAll applications are currently up to date.")
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write("updated=false\n")

if __name__ == "__main__":
    main()
