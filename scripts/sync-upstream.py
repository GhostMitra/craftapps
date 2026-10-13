#!/usr/bin/env python3
"""
Sync Upstream Releases for CraftApps Suite
Downloads official WebAssembly web releases directly from storytold/* repositories,
extracts and flattens them into the dist/ directory, and patches index.html
with custom subdomain routing (debarghaya.in).

All built assets live exclusively in dist/ (git-ignored) for zero repo bloat.
"""

import os
import sys
import json
import re
import urllib.request
import zipfile
import tempfile
import shutil
import stat
from pathlib import Path

APPS = [
    'cadcraft',
    'deckcraft',
    'designcraft',
    'effectcraft',
    'figcraft',
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
DIST_DIR = ROOT_DIR / "dist"
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

    if f"{app_name}.debarghaya.in" in content and "location.replace" in content:
        return

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

def remove_path(path):
    if not path.exists():
        return
    if path.is_dir():
        def on_error(func, p, exc_info):
            try:
                os.chmod(p, stat.S_IWRITE)
                func(p)
            except Exception:
                pass
        shutil.rmtree(path, onerror=on_error)
    else:
        try:
            path.unlink()
        except PermissionError:
            os.chmod(path, stat.S_IWRITE)
            path.unlink()

def clean_dir(target_dir):
    if target_dir.exists():
        for item in target_dir.iterdir():
            remove_path(item)
    else:
        target_dir.mkdir(parents=True, exist_ok=True)

def find_extracted_root(extract_path):
    """Find the root directory inside the extracted zip containing the web app files."""
    if (extract_path / "index.html").exists():
        return extract_path
    index_files = list(extract_path.glob("**/index.html"))
    if index_files:
        return index_files[0].parent
    child_dirs = [p for p in extract_path.iterdir() if p.is_dir()]
    if len(child_dirs) == 1:
        return child_dirs[0]
    return extract_path

def download_and_extract_app(app_name, download_url, target_dir):
    print(f"[{app_name}] Downloading {download_url}...")
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_zip_path = tmp_file.name

    try:
        req = urllib.request.Request(download_url, headers=get_headers())
        with urllib.request.urlopen(req) as response, open(tmp_zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        print(f"[{app_name}] Extracting archive to temporary directory...")
        with tempfile.TemporaryDirectory() as extract_dir:
            extract_path = Path(extract_dir)
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            src_dir = find_extracted_root(extract_path)
            clean_dir(target_dir)

            for item in src_dir.iterdir():
                dst = target_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)

        # Patch index.html
        patch_index_html(target_dir, app_name)
        print(f"[{app_name}] Extracted and installed into {target_dir.relative_to(ROOT_DIR)}")

    finally:
        if os.path.exists(tmp_zip_path):
            os.remove(tmp_zip_path)

def prepare_portal():
    """Ensure dist directory exists and copies root portal landing page & icons."""
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    portal_index = ROOT_DIR / "index.html"
    if portal_index.exists():
        shutil.copy2(portal_index, DIST_DIR / "index.html")
        print("[portal] Installed root index.html to dist/index.html")

    icons_src = ROOT_DIR / "icons"
    if icons_src.exists():
        icons_dst = DIST_DIR / "icons"
        if icons_dst.exists():
            shutil.rmtree(icons_dst)
        shutil.copytree(icons_src, icons_dst)
        print("[portal] Installed icons to dist/icons/")

def main():
    force = "--force" in sys.argv
    check_only = "--check-only" in sys.argv
    specific_app = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and arg in APPS:
            specific_app = arg

    prepare_portal()
    versions = load_versions()
    updated_apps = []

    target_apps = [specific_app] if specific_app else APPS
    print(f"Checking updates for {len(target_apps)} CraftApps (output: dist/)...")

    for app in target_apps:
        app_dist_dir = DIST_DIR / app
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

        # If dist folder doesn't exist yet, we must download even if version matched
        needs_download = (latest_tag != current_version) or force or (not (app_dist_dir / "index.html").exists())

        if needs_download:
            print(f"[{app}] Updating to {latest_tag}...")
            if not check_only:
                download_and_extract_app(app, asset["browser_download_url"], app_dist_dir)
                versions[app] = latest_tag
                updated_apps.append(f"{app} ({latest_tag})")
        else:
            print(f"[{app}] Up to date: {latest_tag}")

    if updated_apps and not check_only:
        save_versions(versions)
        summary = ", ".join(updated_apps)
        print(f"\nCompleted sync: {summary}")
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write("updated=true\n")
                f.write(f"summary={summary}\n")
    else:
        print("\nAll applications ready in dist/.")
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write("updated=false\n")

if __name__ == "__main__":
    main()
