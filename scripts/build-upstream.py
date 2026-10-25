#!/usr/bin/env python3
"""
Build Upstream CraftApp from Main Branch (WebAssembly/Web target)
Clones or uses a local checkout of storytold/{app}, compiles the web target using
upstream packaging scripts (packaging/web/package.sh), extracts the built assets into dist/{app},
and patches index.html with custom domain routing (debarghaya.in).
Bakes git commit provenance directly into Cargo.toml and WebAssembly binaries.
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
import datetime
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
    'solidcraft',
    'soundcraft',
    'vectorcraft',
    'wordcraft'
]

APP_REPOS = {
    'solidcraft': 'tangency-labs/solidcraft'
}

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
    'solidcraft': ('', False),
    'soundcraft': ('', False),
    'vectorcraft': ('a71c20e30af613287c504f7e685ca8fad77752bc', True),
    'wordcraft': ('8dcdacd5153e64560d109541a47d806f26f048c0', False),
}

ROOT_DIR = Path(__file__).resolve().parent.parent

def patch_index_html(target_dir, app_name):
    """
    Patch index.html with subdomain redirection guard and canonical links.
    """
    index_path = target_dir / "index.html"
    if not index_path.exists():
        print(f"Warning: {index_path} not found for patching")
        return

    content = index_path.read_text(encoding="utf-8")

    redirect_script = f"""
    <!-- CraftApps Domain Router & Redirection Guard -->
    <script>
      (function() {{
        var host = window.location.hostname;
        var path = window.location.pathname;
        if (host === "{app_name}.debarghaya.in" && path.indexOf("/{app_name}") === 0) {{
          var newPath = path.substring("/{app_name}".length) || "/";
          window.location.replace("https://{app_name}.debarghaya.in" + newPath + window.location.search + window.location.hash);
        }}
      }})();
    </script>
    """

    canonical_tag = f'<link rel="canonical" href="https://{app_name}.debarghaya.in/" />'

    if "CraftApps Domain Router" not in content:
        if "<head>" in content:
            content = content.replace("<head>", f"<head>\n{redirect_script}\n    {canonical_tag}")
        elif "<HEAD>" in content:
            content = content.replace("<HEAD>", f"<HEAD>\n{redirect_script}\n    {canonical_tag}")
        else:
            content = f"{redirect_script}\n{canonical_tag}\n" + content
        index_path.write_text(content, encoding="utf-8")
        print(f"[{app_name}] Patched index.html with domain routing guard")

def find_extracted_root(temp_dir):
    """Find directory containing index.html after extraction."""
    if (temp_dir / "index.html").exists():
        return temp_dir
    for p in temp_dir.rglob("index.html"):
        return p.parent
    return temp_dir

def clean_dir(target_dir):
    """Empty target directory while preserving the folder itself."""
    def on_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

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

def inject_commit_version(repo_path, commit_sha, app_name):
    """
    Bake commit SHA into Cargo.toml version metadata so that env!("CARGO_PKG_VERSION")
    in Rust WebAssembly binaries automatically displays the commit version in the About dialog.
    """
    sha = commit_sha
    if not sha:
        try:
            res = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "HEAD"], capture_output=True, text=True)
            if res.returncode == 0:
                sha = res.stdout.strip()
        except Exception:
            pass

    if not sha:
        return "", ""

    short_sha = sha[:7]
    cargo_toml = repo_path / "Cargo.toml"
    new_ver = ""
    if cargo_toml.exists():
        content = cargo_toml.read_text(encoding="utf-8")
        pattern = r'(\[(?:workspace\.)?package\][\s\S]*?version\s*=\s*")([^"\+]+)(")'
        match = re.search(pattern, content)
        if match:
            base_ver = match.group(2).strip()
            new_ver = f"{base_ver}+git.{short_sha}"
            content = re.sub(pattern, rf'\g<1>{new_ver}\g<3>', content, count=1)
            cargo_toml.write_text(content, encoding="utf-8")
            print(f"[{app_name}] Injected commit version into Cargo.toml: {new_ver} (for wasm About dialog)")

    return sha, new_ver

def build_app(app_name, repo_path, fonts_dir=None, skip_build=False, commit_sha=None):
    package_sh = repo_path / "packaging" / "web" / "package.sh"
    if not package_sh.exists():
        raise FileNotFoundError(f"Missing packaging script: {package_sh}")

    # Inject commit SHA into Cargo.toml so WebAssembly About dialog renders commit version
    sha, new_ver = inject_commit_version(repo_path, commit_sha, app_name)

    env = os.environ.copy()
    env["CI"] = "true"
    # Allow larger WebAssembly binaries for Firebase Hosting (default Cloudflare limit is 24 MiB)
    env["FIGCRAFT_WASM_MAX_BYTES"] = "52428800"
    env["PHOTOCRAFT_WEB_MAX_FILE_BYTES"] = "52428800"

    # Bake commit SHA provenance into environment variables
    app_upper = app_name.upper()
    if sha:
        env[f"{app_upper}_BUILD_SHA"] = sha
        env[f"{app_upper}_BUILD_DATE"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        if new_ver:
            env[f"{app_upper}_VERSION"] = new_ver
        env["BUILD_SHA"] = sha
        env["GIT_SHA"] = sha

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
    parser.add_argument("--commit-sha", help="Commit SHA of upstream main to bake into version/About dialog")
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
        repo_slug = APP_REPOS.get(app_name, f"storytold/{app_name}")
        upstream_url = f"https://github.com/{repo_slug}.git"
        clone_repo(upstream_url, repo_path, branch=args.branch)

    try:
        build_app(app_name, repo_path, fonts_dir=args.fonts_dir, skip_build=args.skip_build, commit_sha=args.commit_sha)
        extract_and_install(app_name, repo_path, output_dir)
    finally:
        if cleanup_repo and repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)

if __name__ == "__main__":
    main()
