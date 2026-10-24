#!/usr/bin/env python3
"""
Check Upstream Main Branch Commits for CraftApps Suite
Queries the latest commit SHA of the main branch for each storytold repository,
compares against upstream-commits.json, and outputs which applications have new commits.
Supports checking single or multiple comma-separated applications.
"""

import os
import sys
import json
import re
import urllib.request
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
COMMITS_FILE = ROOT_DIR / "upstream-commits.json"

APP_METADATA = {
    'cadcraft': {'fonts_ref': '3d9ab3a132ed0eff457e424226a435a901da30d3', 'web_fonts': False},
    'deckcraft': {'fonts_ref': '43913056ce82a3fdad0ef69f6b88d1dc922a8104', 'web_fonts': False},
    'designcraft': {'fonts_ref': 'a71c20e30af613287c504f7e685ca8fad77752bc', 'web_fonts': True},
    'effectcraft': {'fonts_ref': '', 'web_fonts': False},
    'figcraft': {'fonts_ref': '43913056ce82a3fdad0ef69f6b88d1dc922a8104', 'web_fonts': True},
    'filmcraft': {'fonts_ref': 'bfcbf714e45a3ea8e98f88ab2b7971372a576414', 'web_fonts': False},
    'gridcraft': {'fonts_ref': 'abb83316d96aa59c1cf64784289e378fe9fa5695', 'web_fonts': False},
    'lightcraft': {'fonts_ref': 'a71c20e30af613287c504f7e685ca8fad77752bc', 'web_fonts': True},
    'pdfcraft': {'fonts_ref': '3d9ab3a132ed0eff457e424226a435a901da30d3', 'web_fonts': False},
    'photocraft': {'fonts_ref': 'abb83316d96aa59c1cf64784289e378fe9fa5695', 'web_fonts': False},
    'solidcraft': {'repo': 'tangency-labs/solidcraft', 'fonts_ref': '', 'web_fonts': False},
    'soundcraft': {'fonts_ref': '', 'web_fonts': False},
    'vectorcraft': {'fonts_ref': 'a71c20e30af613287c504f7e685ca8fad77752bc', 'web_fonts': True},
    'wordcraft': {'fonts_ref': '8dcdacd5153e64560d109541a47d806f26f048c0', 'web_fonts': False},
}

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "CraftApps-Commit-Checker",
        "Accept": "application/vnd.github.v3.sha"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def load_recorded_commits():
    if COMMITS_FILE.exists():
        try:
            with open(COMMITS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_recorded_commits(commits):
    with open(COMMITS_FILE, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=2, sort_keys=True)
        f.write("\n")

def fetch_latest_commit_sha(app_name, repo_slug=None, branch="main"):
    repo = repo_slug or f"storytold/{app_name}"
    url = f"https://api.github.com/repos/{repo}/commits/{branch}"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        print(f"[{app_name}] Failed to fetch latest commit for {branch}: {e}", file=sys.stderr)
        return None

def parse_target_apps(app_input):
    if not app_input:
        return "auto", list(APP_METADATA.keys())
    
    raw = app_input.strip().lower()
    if raw == "auto":
        return "auto", list(APP_METADATA.keys())
    if raw == "all":
        return "all", list(APP_METADATA.keys())
    
    tokens = [t.strip() for t in re.split(r'[, \t]+', raw) if t.strip()]
    valid = [t for t in tokens if t in APP_METADATA]
    if not valid:
        print(f"Warning: No recognized app names in '{app_input}'. Defaulting to 'auto'.", file=sys.stderr)
        return "auto", list(APP_METADATA.keys())
    return "custom", valid

def main():
    parser = argparse.ArgumentParser(description="Check for new upstream commits on main")
    parser.add_argument("--app", default="auto", help="App(s) to check/build: 'auto', 'all', a single app, or comma-separated list")
    parser.add_argument("--branch", default="main", help="Git branch to inspect (default: main)")
    parser.add_argument("--force", action="store_true", help="Force rebuild regardless of commit diff")
    parser.add_argument("--update-sha", nargs=2, metavar=("APP", "SHA"), help="Update recorded commit SHA for an app")
    args = parser.parse_args()

    if args.update_sha:
        app, sha = args.update_sha
        commits = load_recorded_commits()
        commits[app] = sha
        save_recorded_commits(commits)
        print(f"Recorded commit {sha[:10]} for {app}")
        return

    recorded_commits = load_recorded_commits()
    mode, apps_to_check = parse_target_apps(args.app)

    # Force rebuild if --force is passed OR if user manually listed specific app(s) or 'all'
    force_build = args.force or (mode in ("custom", "all"))

    matrix_items = []
    changed_apps_summary = []
    latest_shas = {}

    print(f"Inspecting branch '{args.branch}' across {len(apps_to_check)} application(s) (mode: {mode}, force: {force_build})...")

    for app in apps_to_check:
        meta = APP_METADATA[app]
        latest_sha = fetch_latest_commit_sha(app, repo_slug=meta.get("repo"), branch=args.branch)
        if not latest_sha:
            continue

        latest_shas[app] = latest_sha
        prev_sha = recorded_commits.get(app, "")

        has_new_commit = (latest_sha != prev_sha)

        if has_new_commit or force_build:
            matrix_items.append({
                "app": app,
                "repo": meta.get("repo", f"storytold/{app}"),
                "fonts_ref": meta["fonts_ref"],
                "web_fonts": meta["web_fonts"],
                "latest_sha": latest_sha
            })
            if has_new_commit:
                short_prev = prev_sha[:8] if prev_sha else "none"
                short_new = latest_sha[:8]
                changed_apps_summary.append(f"{app} ({short_prev} -> {short_new})")
                print(f"[{app}] NEW commit detected on {args.branch}: {short_prev} -> {short_new}")
            else:
                print(f"[{app}] Rebuilding (forced/manual): {latest_sha[:8]}")
        else:
            print(f"[{app}] Up to date on {args.branch} ({latest_sha[:8]})")

    has_changes = len(matrix_items) > 0
    matrix_output = json.dumps({"include": matrix_items})

    print(f"\nResult: {len(matrix_items)} application(s) queued for build.")

    # Write to GITHUB_OUTPUT if running inside GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"has_changes={'true' if has_changes else 'false'}\n")
            f.write(f"matrix={matrix_output}\n")
            f.write(f"count={len(matrix_items)}\n")
            f.write(f"summary={', '.join(changed_apps_summary) if changed_apps_summary else ', '.join(apps_to_check)}\n")
            f.write(f"latest_shas={json.dumps(latest_shas)}\n")

if __name__ == "__main__":
    main()
