# CraftOS &mdash; Web Desktop Studio 🖥️🎨

> **A desktop-grade Web OS and creative workspace powered by Rust and WebAssembly, running 14 applications in floating resizable windows on Firebase.**

![Rust](https://img.shields.io/badge/Language-Rust-dea584?style=flat-square&logo=rust&logoColor=white)
![WebAssembly](https://img.shields.io/badge/Technology-WebAssembly-654ff0?style=flat-square&logo=webassembly&logoColor=white)
![Firebase Hosting](https://img.shields.io/badge/Hosting-Firebase-ffca28?style=flat-square&logo=firebase&logoColor=black)
![Desktop Environment](https://img.shields.io/badge/UI-Web%20Desktop%20OS-38bdf8?style=flat-square)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-10b981?style=flat-square)

---

## 🌟 Overview

**CraftOS** turns your web browser into a full-featured desktop environment with floating, draggable, and resizable application windows, a frosted-glass taskbar/dock, desktop icons, live system tray, and an application launcher.

Every creative application runs client-side with native-level performance and hardware acceleration (WebGPU / WebGL), compiled directly from pure Rust into WebAssembly.

---

## 🖥️ Desktop Features & Window Management

- **Multi-Window Desktop:** Run multiple applications side-by-side in floating, resizable windows.
- **Window Controls (Traffic Lights):**
  - 🔴 **Close (✕):** Completely unmounts the application from the DOM, instantly terminating the WebAssembly instance and freeing browser RAM and GPU memory.
  - 🟡 **Minimize (−):** Minimizes the application down to the taskbar.
  - 🟢 **Maximize (⤢):** Expands the application to occupy the full desktop screen.
- **Frosted-Glass Taskbar / Dock:**
  - **Start Menu ("CraftOS"):** Search and launch any of the 14 applications with keyboard navigation.
  - **Task Switcher:** Click running taskbar pills to focus, restore, or minimize windows.
  - **System Tray:** Live digital clock, active memory/process monitor, wallpaper switcher, and desktop fullscreen toggle.
- **Strictly On-Demand Lazy Loading (0 MB idle):** Zero heavy WebAssembly binaries (12–56 MB each) are loaded on startup. An application is only fetched when you open its window.
- **Desktop Personalization:** 4 built-in wallpapers (Deep Nebula, Midnight Aurora, Cyber Grid, Minimal Dark) and right-click desktop context menu.

| Application | Custom Subdomain (Cloudflare) | Firebase Route | Equivalent | Core Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **PhotoCraft** | [`photocraft.debarghaya.in`](https://photocraft.debarghaya.in/) | [`/photocraft/`](https://craftapps.web.app/photocraft/) | **Adobe Photoshop** | Layers, blend modes, adjustments, masks, GPU raster graphics |
| **VectorCraft** | [`vectorcraft.debarghaya.in`](https://vectorcraft.debarghaya.in/) | [`/vectorcraft/`](https://craftapps.web.app/vectorcraft/) | **Adobe Illustrator** | Bézier pen tool, boolean path ops, SVG vector design |
| **FigCraft** | [`figcraft.debarghaya.in`](https://figcraft.debarghaya.in/) | [`/figcraft/`](https://craftapps.web.app/figcraft/) | **Figma** | UI/UX design, interactive prototyping, vector components |
| **CADCraft** | [`cadcraft.debarghaya.in`](https://cadcraft.debarghaya.in/) | [`/cadcraft/`](https://craftapps.web.app/cadcraft/) | **Autodesk AutoCAD** | Command line, object snaps, layers, dimensions, DXF drawings |
| **DesignCraft** | [`designcraft.debarghaya.in`](https://designcraft.debarghaya.in/) | [`/designcraft/`](https://craftapps.web.app/designcraft/) | **Adobe InDesign** | Multi-page spreads, master page templating, linked text frames |
| **FilmCraft** | [`filmcraft.debarghaya.in`](https://filmcraft.debarghaya.in/) | [`/filmcraft/`](https://craftapps.web.app/filmcraft/) | **Adobe Premiere Pro** | Multi-track timeline, video cutting, transitions, color grading |
| **EffectCraft** | [`effectcraft.debarghaya.in`](https://effectcraft.debarghaya.in/) | [`/effectcraft/`](https://craftapps.web.app/effectcraft/) | **Adobe After Effects** | Keyframe animation, visual effects compositing, audio worklets |
| **SoundCraft** | [`soundcraft.debarghaya.in`](https://soundcraft.debarghaya.in/) | [`/soundcraft/`](https://craftapps.web.app/soundcraft/) | **Avid Pro Tools** | Digital Audio Workstation (DAW), multi-track mixing, DSP |
| **LightCraft** | [`lightcraft.debarghaya.in`](https://lightcraft.debarghaya.in/) | [`/lightcraft/`](https://craftapps.web.app/lightcraft/) | **Adobe Lightroom** | RAW development, tone curves, exposure grading, OPFS storage |
| **PdfCraft** | [`pdfcraft.debarghaya.in`](https://pdfcraft.debarghaya.in/) | [`/pdfcraft/`](https://craftapps.web.app/pdfcraft/) | **Adobe Acrobat** | Inspect, annotate, reorder, merge, split, form fill, redact |
| **DeckCraft** | [`deckcraft.debarghaya.in`](https://deckcraft.debarghaya.in/) | [`/deckcraft/`](https://craftapps.web.app/deckcraft/) | **MS PowerPoint** | Slide deck creator, vector shapes, animations, presenter mode |
| **GridCraft** | [`gridcraft.debarghaya.in`](https://gridcraft.debarghaya.in/) | [`/gridcraft/`](https://craftapps.web.app/gridcraft/) | **Microsoft Excel** | Fast formula calculation engine, data grid, charts |
| **WordCraft** | [`wordcraft.debarghaya.in`](https://wordcraft.debarghaya.in/) | [`/wordcraft/`](https://craftapps.web.app/wordcraft/) | **Microsoft Word** | Document design, typography styles, tables, citations |
| **SolidCraft** | [`solidcraft.debarghaya.in`](https://solidcraft.debarghaya.in/) | [`/solidcraft/`](https://craftapps.web.app/solidcraft/) | **SolidWorks** | Parametric 3D CAD, feature tree, constraints, B-Rep modeling, MCP |
| **CraftApps Portal** | [`apps.debarghaya.in`](https://apps.debarghaya.in/) | [`/`](https://craftapps.web.app/) | **App Launcher** | Central portal and creative application launcher |

---

## ⚡ In-Portal Launcher & Memory Architecture

### 1. Zero-Footprint Initial Load
At root `/`, the portal loads only the lightweight launcher shell (< 30 KB). **Zero WebAssembly binaries are requested upfront**, keeping initial load times instant and memory consumption at baseline.

### 2. On-Demand Mounting
Clicking **"Launch in Portal"** or navigating to `/#/<app>` dynamically mounts the requested application:
- Creates an isolated iframe container on demand.
- Displays an animated loader while WebAssembly initializes.
- Mounts with full hardware access (`clipboard`, `fullscreen`, `webgpu/webgl`, `audio`).

### 3. Multi-Session Tab Switcher & Clean Unload
- Launch multiple applications and switch between them using the top workspace tab bar.
- Clicking the **✕ Close** button or toolbar **"Close App"** removes the iframe from the DOM, instantly terminating the WebAssembly instance and freeing up RAM and GPU resources.

---

## 🏗️ Routing & Server Architecture

### 1. Dual-Routing Modes
- **In-Portal Router:** `https://craftapps.web.app/#/photocraft` loads the workspace and mounts PhotoCraft in-place.
- **Standalone Sub-Routes:** `https://craftapps.web.app/photocraft/` opens the standalone full-screen application.

### 2. Sub-Route Normalization (`trailingSlash: true`)
Configured in `firebase.json`:
- Visiting `/photocraft` (without trailing slash) cleanly 301-redirects to `/photocraft/`.
- Relative assets (`./photocraft-web-*.js` and `.wasm`) resolve accurately without broken paths.

### 3. WebAssembly MIME & Caching Headers
- `.wasm` files are served with `Content-Type: application/wasm` and long-term immutable caching (`max-age=31536000, immutable`).
- `index.html` files are configured with `Cache-Control: no-cache` for instant updates.
- Security headers enforce `X-Content-Type-Options: nosniff`.

---

## 💻 Local Testing & Preview

### Option A: Using Python (Recommended, Zero Setup)
```bash
python -m http.server 8080
```
Open **[http://localhost:8080](http://localhost:8080)** in your browser to test the portal launcher and apps locally.

### Option B: Using Firebase Local Emulator
```bash
npx firebase-tools emulators:start --only hosting
```

---

## ☁️ Firebase Hosting Deployment

### 1. Validate Deployment (Dry Run)
```bash
npx firebase-tools deploy --only hosting --dry-run
```

### 2. Deploy to Production
```bash
npx firebase-tools deploy --only hosting
```

Your live site will be accessible at:
👉 **`https://craftapps.web.app`**

---

## 🤖 Automated CI/CD (GitHub Actions)

This repository includes an automated workflow at [`.github/workflows/firebase-deploy.yml`](.github/workflows/firebase-deploy.yml) that updates the portal UI shell (`index.html`, `icons/**`, `firebase.json`) on Firebase Hosting when those files change, preserving the compiled WebAssembly applications from cache without downloading release zips.

### Setting up GitHub Secrets

Add one of the following secrets to your GitHub repository (**Settings ▸ Secrets and variables ▸ Actions ▸ New repository secret**):

- **Option A: Service Account (Recommended)**
  - Secret Name: `FIREBASE_SERVICE_ACCOUNT_CRAFTAPPS`
  - Value: The JSON key for your Google Cloud / Firebase service account with the **Firebase Hosting Admin** role.
  - To generate: In [Firebase Console](https://console.firebase.google.com/project/craftapps/settings/serviceaccounts/adminsdk) ▸ **Project Settings ▸ Service accounts** ▸ click **Generate new private key**.

- **Option B: Firebase CLI Token**
  - Secret Name: `FIREBASE_TOKEN`
  - Value: Run `npx firebase-tools login:ci` locally, authenticate in your browser, and copy the generated token.

---

## 🏗️ Build Upstream from Main & Deploy to Firebase

The primary deployment workflow at [`.github/workflows/build-from-main.yml`](.github/workflows/build-from-main.yml) monitors the `main` branch across all 14 upstream repositories (`storytold/*` and `tangency-labs/solidcraft`), compiling native WebAssembly applications directly from source and deploying to Firebase Hosting:

- **6-Hour Incremental Diff Check (`0 6,12,18 * * *`)**: Queries GitHub API for the latest commit SHA on `main`. If commits are unchanged, the check exits in seconds with zero runner minutes used. When new commits are found, only the modified apps are compiled in parallel and merged into the distribution.
- **24-Hour Full Clean Rebuild (`0 0 * * *`)**: Once every 24 hours at 00:00 UTC, the workflow purges all repository caches (`gh cache delete --all`), compiles all 14 applications cleanly from scratch, rebuilds `dist/`, and redeploys to Firebase.
- **Automated Commit Diff Tracking**: Tracks the latest built commit SHA for every repository in `upstream-commits.json`.
- **Granular Matrix Compilation**: Spawns parallel matrix runners only for apps requiring compilation, respecting app-specific font bundles and WebAssembly size budgets (50 MiB).
- **Web-Only Compilation**: Compiles WebAssembly and JS glue using Trunk and `wasm32-unknown-unknown` via `packaging/web/package.sh`.
- **Atomic Firebase Deployment**: Assembles built apps into `dist/` alongside root portal assets (`index.html` and icons), preserving custom subdomain routing and deploying the complete suite to Firebase Hosting.
- **Resilient Partial Deployments & GitHub Notifications**: If any app fails to compile from `main` (even during 24h clean rebuilds), the remaining successful applications are deployed to Firebase without interruption. Any failed application continues running its previous successful build on the website (without downloading external release zips), and GitHub triggers a failure notification with exact compiler logs so you are alerted immediately.

### Triggering via GitHub Actions UI
1. Go to **Actions** ▸ **Build Upstream from Main & Deploy to Firebase**.
2. Click **Run workflow**.
3. Options:
   - `app`: `auto` (default, checks for changes), `all` (all 14 apps), a single app (e.g. `solidcraft`), or a comma-separated list (e.g. `figcraft, photocraft, solidcraft`).
   - `branch`: Git branch to inspect and build (default `main`).
   - `force`: Force rebuild regardless of commit diff.
   - `clean_build`: Purge all caches and rebuild all 14 apps completely from scratch.
4. Click **Run workflow**.

### Triggering via GitHub CLI
```bash
# Check all upstream repos for new commits and build/deploy ONLY changed apps:
gh workflow run build-from-main.yml -f app=auto

# Force rebuild of a single app (e.g. solidcraft or figcraft):
gh workflow run build-from-main.yml -f app=solidcraft -f branch=main --raw-field force=true

# Force rebuild of multiple apps (e.g. figcraft and photocraft):
gh workflow run build-from-main.yml -f app="figcraft, photocraft" -f branch=main --raw-field force=true

# Force rebuild of all 14 apps from main in parallel and deploy:
gh workflow run build-from-main.yml -f app=all --raw-field force=true

# 24-hour style 100% clean rebuild: purge all caches and compile all 14 apps from scratch:
gh workflow run build-from-main.yml --raw-field clean_build=true
```

---

## 🔄 Legacy Upstream Release Sync

The backup workflow at [`.github/workflows/auto-update-upstream.yml`](.github/workflows/auto-update-upstream.yml) provides on-demand fallback downloading of official GitHub release archive zips via `workflow_dispatch` without compiling from source. Scheduled runs have been superseded by `build-from-main.yml`.

---

## 🔒 Privacy & Security

- **100% Client-Side:** Files you open, edit, or save remain in your browser's local memory or Origin Private File System (OPFS).
- **No Uploads:** Your media, documents, and CAD drawings never leave your computer.
- **Offline Capable:** Once cached by your browser, applications continue operating even when disconnected.

---

## 📄 License & Attribution

- Built on open-source Rust libraries and WebAssembly tooling.
- Core applications are licensed under **MIT** or **Apache-2.0**.
- Bundled UI fonts are governed by the **SIL Open Font License (OFL)**.
