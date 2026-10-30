# CraftOS &mdash; Web Desktop Studio 🖥️🎨

> **A desktop-grade Web OS and creative workspace powered by Rust and WebAssembly, running 14 creative applications in floating resizable windows on Firebase Hosting and Cloudflare Workers.**

![Rust](https://img.shields.io/badge/Language-Rust-dea584?style=flat-square&logo=rust&logoColor=white)
![WebAssembly](https://img.shields.io/badge/Technology-WebAssembly-654ff0?style=flat-square&logo=webassembly&logoColor=white)
![Firebase Hosting](https://img.shields.io/badge/Hosting-Firebase-ffca28?style=flat-square&logo=firebase&logoColor=black)
![Cloudflare](https://img.shields.io/badge/Edge%20Router-Cloudflare%20Workers-f38020?style=flat-square&logo=cloudflare&logoColor=white)
![CodeRabbit](https://img.shields.io/badge/Code%20Review-CodeRabbit%20AI-ff6b6b?style=flat-square)
![Desktop Environment](https://img.shields.io/badge/UI-Web%20Desktop%20OS-38bdf8?style=flat-square)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-10b981?style=flat-square)

---

## 🌟 Overview

**CraftOS** turns your web browser into a full-featured desktop environment with floating, draggable, and resizable application windows, a frosted-glass taskbar/dock, desktop icons, live system tray, and an application launcher.

Every application in the suite is compiled directly from upstream source repositories (`storytold/*` and `tangency-labs/*`) into high-performance **WebAssembly** with native-level hardware acceleration (WebGPU / WebGL).

---

## 🖥️ Desktop Features & Window Architecture

- **Multi-Window Desktop OS:** Run multiple creative applications side-by-side in floating, resizable windows with active z-index stacking.
- **Window Controls (Traffic Lights):**
  - 🔴 **Close (✕):** Completely unmounts the application from the DOM, instantly terminating the WebAssembly instance and freeing browser RAM and GPU memory.
  - 🟡 **Minimize (−):** Minimizes the application down to the taskbar pill.
  - 🟢 **Maximize (⤢):** Expands the application to occupy the full desktop screen.
- **Frosted-Glass Taskbar / Dock:**
  - **Start Menu ("CraftOS"):** Search and launch any of the 16 applications with instant keyboard filtering.
  - **Task Switcher:** Click running taskbar pills to focus, restore, or minimize windows.
  - **System Tray:** Live digital clock, active memory/process monitor, wallpaper switcher, and desktop fullscreen toggle.
- **Strictly On-Demand Lazy Loading (0 MB idle):** Zero heavy WebAssembly binaries (12–56 MB each) are loaded on startup. An application is only fetched when you open its window.
- **Desktop Personalization:** 4 built-in wallpapers (Deep Nebula, Midnight Aurora, Cyber Grid, Minimal Dark) and right-click desktop context menu.

---

## 🎨 Application Suite & Routing Matrix

| Application | Custom Subdomain (Cloudflare) | Firebase Route | Upstream Repository | Equivalent | Core Capabilities |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PhotoCraft** | [`photocraft.debarghaya.in`](https://photocraft.debarghaya.in/) | [`/photocraft/`](https://craftapps.web.app/photocraft/) | [`storytold/photocraft`](https://github.com/storytold/photocraft) | **Adobe Photoshop** | Layers, blend modes, adjustments, masks, GPU raster graphics |
| **VectorCraft** | [`vectorcraft.debarghaya.in`](https://vectorcraft.debarghaya.in/) | [`/vectorcraft/`](https://craftapps.web.app/vectorcraft/) | [`storytold/vectorcraft`](https://github.com/storytold/vectorcraft) | **Adobe Illustrator** | Bézier pen tool, boolean path ops, SVG vector design |
| **FigCraft** | [`figcraft.debarghaya.in`](https://figcraft.debarghaya.in/) | [`/figcraft/`](https://craftapps.web.app/figcraft/) | [`storytold/figcraft`](https://github.com/storytold/figcraft) | **Figma** | UI/UX design, interactive prototyping, vector components |
| **CADCraft** | [`cadcraft.debarghaya.in`](https://cadcraft.debarghaya.in/) | [`/cadcraft/`](https://craftapps.web.app/cadcraft/) | [`storytold/cadcraft`](https://github.com/storytold/cadcraft) | **Autodesk AutoCAD** | Command line, object snaps, layers, dimensions, DXF drawings |
| **DesignCraft** | [`designcraft.debarghaya.in`](https://designcraft.debarghaya.in/) | [`/designcraft/`](https://craftapps.web.app/designcraft/) | [`storytold/designcraft`](https://github.com/storytold/designcraft) | **Adobe InDesign** | Multi-page spreads, master page templating, linked text frames |
| **FilmCraft** | [`filmcraft.debarghaya.in`](https://filmcraft.debarghaya.in/) | [`/filmcraft/`](https://craftapps.web.app/filmcraft/) | [`storytold/filmcraft`](https://github.com/storytold/filmcraft) | **Adobe Premiere Pro** | Multi-track timeline, video cutting, transitions, color grading |
| **EffectCraft** | [`effectcraft.debarghaya.in`](https://effectcraft.debarghaya.in/) | [`/effectcraft/`](https://craftapps.web.app/effectcraft/) | [`storytold/effectcraft`](https://github.com/storytold/effectcraft) | **Adobe After Effects** | Keyframe animation, visual effects compositing, audio worklets |
| **SoundCraft** | [`soundcraft.debarghaya.in`](https://soundcraft.debarghaya.in/) | [`/soundcraft/`](https://craftapps.web.app/soundcraft/) | [`storytold/soundcraft`](https://github.com/storytold/soundcraft) | **Avid Pro Tools** | Digital Audio Workstation (DAW), multi-track mixing, DSP |
| **LightCraft** | [`lightcraft.debarghaya.in`](https://lightcraft.debarghaya.in/) | [`/lightcraft/`](https://craftapps.web.app/lightcraft/) | [`storytold/lightcraft`](https://github.com/storytold/lightcraft) | **Adobe Lightroom** | RAW development, tone curves, exposure grading, OPFS storage |
| **PdfCraft** | [`pdfcraft.debarghaya.in`](https://pdfcraft.debarghaya.in/) | [`/pdfcraft/`](https://craftapps.web.app/pdfcraft/) | [`storytold/pdfcraft`](https://github.com/storytold/pdfcraft) | **Adobe Acrobat** | Inspect, annotate, reorder, merge, split, form fill, redact |
| **DeckCraft** | [`deckcraft.debarghaya.in`](https://deckcraft.debarghaya.in/) | [`/deckcraft/`](https://craftapps.web.app/deckcraft/) | [`storytold/deckcraft`](https://github.com/storytold/deckcraft) | **MS PowerPoint** | Slide deck creator, vector shapes, animations, presenter mode |
| **GridCraft** | [`gridcraft.debarghaya.in`](https://gridcraft.debarghaya.in/) | [`/gridcraft/`](https://craftapps.web.app/gridcraft/) | [`storytold/gridcraft`](https://github.com/storytold/gridcraft) | **Microsoft Excel** | Fast formula calculation engine, data grid, charts |
| **WordCraft** | [`wordcraft.debarghaya.in`](https://wordcraft.debarghaya.in/) | [`/wordcraft/`](https://craftapps.web.app/wordcraft/) | [`storytold/wordcraft`](https://github.com/storytold/wordcraft) | **Microsoft Word** | Document design, typography styles, tables, citations |
| **SolidCraft** | [`solidcraft.debarghaya.in`](https://solidcraft.debarghaya.in/) | [`/solidcraft/`](https://craftapps.web.app/solidcraft/) | [`tangency-labs/solidcraft`](https://github.com/tangency-labs/solidcraft) | **SolidWorks** | Parametric 3D CAD, feature tree, constraints, B-Rep modeling |
| **FieldCraft** | [`fieldcraft.debarghaya.in`](https://fieldcraft.debarghaya.in/) | [`/fieldcraft/`](https://craftapps.web.app/fieldcraft/) | [`tangency-labs/fieldcraft`](https://github.com/tangency-labs/fieldcraft) | **ANSYS / Abaqus** | Multiphysics CAE, finite element analysis (FEA), hex/tet meshing, CFD |
| **PCBCraft** | [`pcbcraft.debarghaya.in`](https://pcbcraft.debarghaya.in/) | [`/pcbcraft/`](https://craftapps.web.app/pcbcraft/) | [`tangency-labs/pcbcraft`](https://github.com/tangency-labs/pcbcraft) | **KiCad / Altium** | EDA schematic capture, interactive PCB layout routing, library authoring |
| **CraftOS Portal** | [`apps.debarghaya.in`](https://apps.debarghaya.in/) | [`/`](https://craftapps.web.app/) | &mdash; | **Web Desktop OS** | Central desktop workspace and application launcher |

---

## ⚡ In-Portal Launcher & Memory Architecture

### 1. Zero-Footprint Initial Load
At root `/`, the portal loads only the lightweight launcher shell (< 30 KB). **Zero WebAssembly binaries are requested upfront**, keeping initial load times instantaneous and memory consumption at baseline.

### 2. Isolated On-Demand Mounting
Clicking an application icon or launching from the Start Menu mounts the requested application:
- Creates an isolated iframe container on demand.
- Displays an animated loader while WebAssembly initializes.
- Mounts with explicit hardware feature policies (`clipboard-read; clipboard-write; webgpu; cross-origin-isolated; fullscreen`).

### 3. Multi-Session Task Management & Memory Termination
- Launch multiple applications and switch between them using the frosted taskbar.
- Clicking the **✕ Close** button removes the iframe container completely from the DOM, instantly terminating the WebAssembly instance and freeing all allocated WebAssembly heap and WebGL/WebGPU context memory.

---

## 🏗️ Routing & Edge Infrastructure

### 1. Dual-Routing Modes
- **In-Portal Desktop OS:** `https://craftapps.web.app/#/photocraft` loads the CraftOS workspace and mounts PhotoCraft in a floating window.
- **Standalone Sub-Routes:** `https://craftapps.web.app/photocraft/` opens the standalone full-screen application.

### 2. Cloudflare Worker Reverse Proxy (`cloudflare/worker.js`)
Configured in [`cloudflare/wrangler.toml`](cloudflare/wrangler.toml):
- Custom subdomains (`*.debarghaya.in`) silently proxy to `craftapps.web.app/<app>/` with zero URL redirection.
- Sub-route normalizations cleanly 301-redirect `/photocraft` to `/photocraft/`.
- Edge headers enforce CORS and security policies.

### 3. WebAssembly MIME & Caching Headers (`firebase.json`)
- `.wasm` files are served with `Content-Type: application/wasm` and long-term immutable caching (`public, max-age=31536000, immutable`).
- `index.html` files are configured with `Cache-Control: no-cache` for instant portal and launcher updates.
- Security headers enforce `X-Content-Type-Options: nosniff`.
- Production deployment ignores all development scripts, compiler build caches, and metadata.

---

## 🤖 Automated CI/CD Workflows (GitHub Actions)

The deployment pipeline is partitioned into purpose-built workflows under `.github/workflows/`:

```
.github/workflows/
├── build-from-main.yml       # PRIMARY: Source compiler & deployer (6h diff check + 24h clean rebuild)
├── firebase-deploy.yml       # PORTAL: Deploys portal UI changes only (never downloads release zips)
├── cloudflare-deploy.yml     # EDGE: Deploys Cloudflare Worker router when cloudflare/** changes
└── auto-update-upstream.yml  # BACKUP: Legacy manual release sync fallback (scheduled cron disabled)
```

### 1. Build Upstream from Main & Deploy to Firebase ([`build-from-main.yml`](.github/workflows/build-from-main.yml))
The primary production pipeline compiles native WebAssembly applications directly from upstream git branches (`main`) and deploys to Firebase Hosting:

- **6-Hour Incremental Diff Check (`0 6,12,18 * * *`)**:
  - Queries the GitHub API for latest commit SHAs on `main` across all 14 repositories.
  - If no new commits exist, the check exits in seconds with **zero runner minutes** consumed.
  - When changes appear, only the modified applications are compiled in parallel.
- **24-Hour Full Clean Rebuild (`0 0 * * *`)**:
  - Once every 24 hours at 00:00 UTC, the workflow purges compiler build caches (`v0-rust-*`) and recompiles all 14 applications from source completely from scratch.
  - The persistent web distribution cache (`craftapps-dist-*`) is **protected and preserved**.
- **Resilient Partial Deployments & Zero Release Downloads**:
  - Build matrix operates with `fail-fast: false`.
  - If any application fails to compile from `main`, the remaining successful applications are deployed to Firebase without interruption.
  - **Failed applications continue running their previous successful build** already on the live website (zero downloads from external release zips).
  - Failed apps keep their previous commit SHA in `upstream-commits.json`, so the next 6-hour schedule automatically retries compiling them.
- **Native GitHub Failure Notifications**:
  - If any application fails to compile, the workflow posts an `::error` annotation and concludes with a failure status.
  - GitHub automatically triggers an email, web, and mobile push notification with direct links to the diagnostic compiler logs.
- **Web-Only Compilation**:
  - Compiles WebAssembly and JS glue using Trunk CLI and `wasm32-unknown-unknown` via upstream `packaging/web/package.sh`.
  - Enforces WebAssembly size budgets (`FIGCRAFT_WASM_MAX_BYTES=52428800` and `PHOTOCRAFT_WEB_MAX_FILE_BYTES=52428800`).

#### Triggering via GitHub Actions UI
1. Go to **Actions** ▸ **Build Upstream from Main & Deploy to Firebase**.
2. Click **Run workflow**.
3. Options:
   - `app`: `auto` (checks for changes), `all` (all 16 apps), a single app (e.g. `solidcraft`), or a comma-separated list (e.g. `figcraft, photocraft, solidcraft`).
   - `branch`: Git branch to inspect and build (default `main`).
   - `force`: Force rebuild regardless of commit diff.
   - `clean_build`: Purge compiler caches and rebuild all 16 apps from scratch.
4. Click **Run workflow**.

#### Triggering via GitHub CLI
```bash
# Check all upstream repos for new commits and build/deploy ONLY changed apps:
gh workflow run build-from-main.yml -f app=auto

# Force rebuild of a single app (e.g. solidcraft or figcraft):
gh workflow run build-from-main.yml -f app=solidcraft -f branch=main --raw-field force=true

# Force rebuild of multiple selected apps:
gh workflow run build-from-main.yml -f app="figcraft, photocraft" -f branch=main --raw-field force=true

# Force rebuild of all 16 apps from main in parallel and deploy:
gh workflow run build-from-main.yml -f app=all --raw-field force=true

# 24-hour style clean rebuild (purge compiler caches and recompile all 14 apps from scratch):
gh workflow run build-from-main.yml --raw-field clean_build=true
```

### 2. Deploy Portal Shell to Firebase ([`firebase-deploy.yml`](.github/workflows/firebase-deploy.yml))
- Triggered **only** when portal UI files change (`index.html`, `icons/**`, or `firebase.json`).
- Commits to scripts, configs, workflows, or documentation **do not trigger this workflow**.
- Restores the persistent web distribution cache (`craftapps-dist-`) and deploys the updated portal shell with zero release zip downloads.

### 3. Deploy Cloudflare Proxy ([`cloudflare-deploy.yml`](.github/workflows/cloudflare-deploy.yml))
- Triggered on changes to `cloudflare/**` to deploy the edge worker router via Wrangler.

### 4. Legacy Upstream Release Sync ([`auto-update-upstream.yml`](.github/workflows/auto-update-upstream.yml))
- Scheduled runs have been superseded by `build-from-main.yml`.
- Kept strictly as a manual `workflow_dispatch` fallback.

---

## 🐇 Code Quality & Code Review ([`.coderabbit.yaml`](.coderabbit.yaml))

This repository enforces automated AI code reviews via [CodeRabbit](https://coderabbit.ai) with a custom [`.coderabbit.yaml`](.coderabbit.yaml) configuration adhering to CodeRabbit Schema v2:

- **Standard-Library-Only Python (`scripts/**`)**: Strict enforcement of Python 3.11+ stdlib modules (`urllib.request`, `json`, `argparse`, `pathlib`, `subprocess`, `re`, `shutil`). Third-party dependencies (`requests`, `pydantic`) are banned.
- **Zero Binary Bloat in Git**: Pre-commit verification preventing binaries (`.wasm`, `.zip`, `.tar.gz`) or `dist/` folders from being tracked.
- **CI/CD Resilience (`.github/workflows/**`)**: Verifies `fail-fast: false`, non-blocking deployment logic, shell variable quoting, and cache protection.
- **Portal Memory Safety (`index.html`)**: Verifies 0 MB idle load, iframe unmounting on window close, and sandbox permissions.
- **Integrated Linters**: `actionlint` (workflows), `shellcheck` (scripts), `ruff` (python), `yamllint` (yaml), `gitleaks` (secrets), `markdownlint`, and `htmlhint`.

---

## 📁 Repository Structure

```
craftapps/
├── .github/
│   └── workflows/
│       ├── build-from-main.yml       # Source compilation & deployment pipeline
│       ├── firebase-deploy.yml       # Portal UI shell deployer
│       ├── cloudflare-deploy.yml     # Cloudflare edge worker deployer
│       └── auto-update-upstream.yml  # Legacy manual release syncer
├── cloudflare/
│   ├── worker.js                     # Subdomain reverse proxy & URL router
│   └── wrangler.toml                 # Cloudflare Worker configuration
├── icons/                            # High-resolution 256x256 application icons
│   ├── cadcraft.png
│   ├── photocraft.png
│   ├── solidcraft.png
│   └── ...                           # (14 application icons)
├── scripts/
│   ├── build-upstream.py             # Compiles WebAssembly apps via packaging scripts
│   ├── check-upstream-commits.py     # Detects upstream main commits & generates matrix
│   └── sync-upstream.py              # Legacy fallback release extractor
├── .coderabbit.yaml                  # Custom CodeRabbit AI code review configuration
├── firebase.json                     # Firebase Hosting routes, headers & MIME configuration
├── index.html                        # CraftOS Web Desktop UI & window manager
├── upstream-commits.json             # Tracked commit SHAs for all 14 upstream repos
├── versions.json                     # Fallback version metadata
└── README.md                         # Project documentation
```

---

## 💻 Local Testing & Preview

### Option A: Using Python (Recommended, Zero Setup)
```bash
python -m http.server 8080
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to test the CraftOS window manager and portal locally.

### Option B: Using Firebase Local Emulator
```bash
npx firebase-tools emulators:start --only hosting
```

---

## ☁️ Setting Up GitHub Secrets

To enable deployments, configure the following secrets under **Settings ▸ Secrets and variables ▸ Actions ▸ New repository secret**:

| Secret Name | Purpose | How to Generate |
| :--- | :--- | :--- |
| `FIREBASE_SERVICE_ACCOUNT_CRAFTAPPS` | Firebase Hosting deployments | [Firebase Console](https://console.firebase.google.com/project/craftapps/settings/serviceaccounts/adminsdk) ▸ **Project Settings ▸ Service accounts** ▸ Generate new private key |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Worker deployment | [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens) ▸ Create Token with **Workers Scripts:Edit** permissions |
| `GITHUB_TOKEN` | GitHub API checks & cache access | Provided automatically by GitHub Actions |

---

## 🔒 Privacy & Security

- **100% Client-Side:** Files you open, edit, or create remain in your browser's local memory or Origin Private File System (OPFS).
- **No Uploads:** Your media, documents, and CAD drawings never leave your machine.
- **Offline Capable:** Once cached by your browser, applications continue operating even when disconnected from the internet.

---

## 📄 License & Attribution

- Built on open-source Rust libraries and WebAssembly tooling.
- Core applications are licensed under **MIT** or **Apache-2.0** by their respective upstream authors ([storytold](https://github.com/storytold) and [tangency-labs](https://github.com/tangency-labs)).
- Bundled UI fonts are governed by the **SIL Open Font License (OFL)**.
