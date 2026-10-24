#!/usr/bin/env python3
"""
Build Upstream CraftApp from Main Branch (WebAssembly/Web target)
Clones or uses a local checkout of storytold/{app}, compiles the web target using
upstream packaging scripts (packaging/web/package.sh), extracts the built assets into dist/{app},
and patches index.html with custom domain routing (debarghaya.in).
"""

import os
import sys
import argparse
import subprocess
import shutil
import zipfile
import tempfile
import re
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

# Upstream font reference commits mapped from official release workflows
APP_FONTS = {
    'cadcraft': ('3d9ab3a132ed0eff457e424226a435a901da30d3', False),
    'deckcraft': ('43913056ce82a3fdad0ef69f6b88d1dc922a8104', False),
    'designcraft': ('a71c20e30af613287c504f7e685ca8fad77752bc', True),
    'effectcraft': ('', False),
    'figcraft': ('43913056ce82a3fdad0ef69f6b88d1dc922a8104', True),
    'filmcraft': ('bfcbf714e45a3ea8e98f88ab2b7971372a576414', False),
    'gridcraft': ('abb83316d96aa59c1cf64784289e378fe9fa5695', False),
    'lightcraft': ('a71c20e30af613287c504f7e685ca8fad77752bc', True),
    'pdfcraft': ('3d9ab3a132ed0eff457e424226a435a901da30d3', False),
    'photocraft': ('abb83316d96aa59c1cf64784289e378fe9fa5695', False),
    'soundcraft': ('', False),
    'vectorcraft': ('a71c20e30af613287c504f7e685ca8fad77752bc', True),
    'wordcraft': ('8dcdacd5153e64560d109541a47d806f26f048c0', False),
}

ROOT_DIR = Path(__file__).resolve().parent.parent

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
        print(f"[{app_name}] index.html already patched with domain routing")
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

def find_extracted_root(extract_path):
    """Find the root directory containing index.html."""
    if (extract_path / "index.html").exists():
        return extract_path
    index_files = list(extract_path.glob("**/index.html"))
    if index_files:
        return index_files[0].parent
    child_dirs = [p for p in extract_path.iterdir() if p.is_dir()]
    if len(child_dirs) == 1:
        return child_dirs[0]
    return extract_path

def clean_dir(target_dir):
    def on_error(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    if target_dir.exists():
        for item in target_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, onerror=on_error)
            else:
                try:
                    item.unlink()
                except Exception:
                    pass
    else:
        target_dir.mkdir(parents=True, exist_ok=True)

def clone_repo(repo_url, target_path, branch="main", depth=1):
    print(f"Cloning {repo_url} (branch: {branch})...")
    cmd = ["git", "clone", "--branch", branch]
    if depth:
        cmd.extend(["--depth", str(depth)])
    cmd.extend([repo_url, str(target_path)])
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to clone {repo_url}")

def build_app(app_name, repo_path, fonts_dir=None, skip_build=False):
    package_sh = repo_path / "packaging" / "web" / "package.sh"
    if not package_sh.exists():
        raise FileNotFoundError(f"Missing packaging script: {package_sh}")

    env = os.environ.copy()
    env["CI"] = "true"

    font_ref, needs_web_fonts = APP_FONTS.get(app_name, ('', False))

    if fonts_dir and Path(fonts_dir).exists():
        env["CRAFT_FONTS_DIR"] = str(Path(fonts_dir).resolve())
        if needs_web_fonts:
            env["CRAFT_FONTS_REQUIRED"] = "1"
    elif "CRAFT_FONTS_DIR" in os.environ:
        env["CRAFT_FONTS_DIR"] = os.environ["CRAFT_FONTS_DIR"]
        if needs_web_fonts:
            env["CRAFT_FONTS_REQUIRED"] = "1"

    # Setup craft-i18n if requested by repo
    i18n_rev_file = repo_path / "craft-i18n.rev"
    i18n_dir = repo_path.parent / "craft-i18n"
    if i18n_rev_file.exists() and i18n_dir.exists():
        env["CRAFT_I18N_DIR"] = str(i18n_dir.resolve())
        env["CRAFT_I18N_REQUIRED"] = "1"

    cmd = ["bash", "packaging/web/package.sh"]
    if skip_build:
        cmd.append("--skip-build")

    print(f"[{app_name}] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(repo_path), env=env)
    if result.returncode != 0:
        raise RuntimeError(f"[{app_name}] Web build failed with exit code {result.returncode}")

def extract_and_install(app_name, repo_path, output_dir):
    out_path = Path(output_dir).resolve()
    clean_dir(out_path)

    # 1. Look for release zip in dist/release/*.zip or dist/*.zip
    zip_candidates = list((repo_path / "dist" / "release").glob("*.zip"))
    if not zip_candidates:
        zip_candidates = list((repo_path / "dist").glob("*.zip"))

    if zip_candidates:
        zip_file = zip_candidates[0]
        print(f"[{app_name}] Extracting packaged release artifact: {zip_file.name}")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with zipfile.ZipFile(zip_file, "r") as z:
                z.extractall(tmp_path)
            src_root = find_extracted_root(tmp_path)
            for item in src_root.iterdir():
                dst = out_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dst)
                else:
                    shutil.copy2(item, dst)
    else:
        # 2. Look for web-package directory
        web_package = repo_path / "target" / "web-package"
        if web_package.exists():
            pkg_dirs = [p for p in web_package.iterdir() if p.is_dir()]
            if pkg_dirs:
                src_root = pkg_dirs[0]
                print(f"[{app_name}] Copying from web-package directory: {src_root.name}")
                for item in src_root.iterdir():
                    dst = out_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst)
                    else:
                        shutil.copy2(item, dst)
            else:
                raise FileNotFoundError(f"[{app_name}] No output directory found inside {web_package}")
        else:
            raise FileNotFoundError(f"[{app_name}] Could not find built release zip or web-package directory")

    # Patch index.html with canonical & domain routing
    patch_index_html(out_path, app_name)
    print(f"[{app_name}] Successfully installed web application to {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Build Upstream CraftApp from Main Branch")
    parser.add_argument("--app", required=True, help="Application name (e.g. photocraft, cadcraft)")
    parser.add_argument("--repo-dir", help="Path to checked out upstream repository")
    parser.add_argument("--branch", default="main", help="Upstream branch to checkout (if cloning)")
    parser.add_argument("--output-dir", help="Target output directory for built web assets")
    parser.add_argument("--fonts-dir", help="Path to craft-fonts directory (if needed)")
    parser.add_argument("--skip-build", action="store_true", help="Skip compilation and package existing build")

    args = parser.parse_args()
    app_name = args.app.lower()

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = ROOT_DIR / "dist" / app_name

    cleanup_repo = False
    if args.repo_dir:
        repo_path = Path(args.repo_dir).resolve()
    else:
        temp_dir = tempfile.mkdtemp(prefix=f"craftapp-{app_name}-")
        repo_path = Path(temp_dir)
        cleanup_repo = True
        upstream_url = f"https://github.com/storytold/{app_name}.git"
        clone_repo(upstream_url, repo_path, branch=args.branch)

    try:
        build_app(app_name, repo_path, fonts_dir=args.fonts_dir, skip_build=args.skip_build)
        extract_and_install(app_name, repo_path, output_dir)
    finally:
        if cleanup_repo and repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == "__main__":
    main()
