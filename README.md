# CraftApps Studio 🎨⚡

> **A high-performance, open-source creative and productivity suite powered by Rust and WebAssembly, unified under a single web portal and hosted on Firebase.**

![Rust](https://img.shields.io/badge/Language-Rust-dea584?style=flat-square&logo=rust&logoColor=white)
![WebAssembly](https://img.shields.io/badge/Technology-WebAssembly-654ff0?style=flat-square&logo=webassembly&logoColor=white)
![Firebase Hosting](https://img.shields.io/badge/Hosting-Firebase-ffca28?style=flat-square&logo=firebase&logoColor=black)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Client--Side-10b981?style=flat-square)
![License](https://img.shields.io/badge/License-MIT%20%2F%20Apache--2.0-3b82f6?style=flat-square)

---

## 🌟 Overview

**CraftApps Studio** brings desktop-grade creative and office software directly into your web browser without installation, accounts, or telemetry. Every application is compiled from pure Rust into WebAssembly, running client-side with native-level performance and hardware acceleration (WebGPU / WebGL).

This repository features:
- **An In-Portal On-Demand App Launcher:** Launch and run any application right inside the portal workspace.
- **Strictly On-Demand Lazy Loading:** No heavy WASM binaries (12–56 MB) are loaded at page visit; each app is only fetched when requested.
- **Active App Tab Switcher & Memory Release:** Run multiple apps side-by-side, switch tabs, and cleanly unload apps to reclaim browser memory.
- **Dedicated Sub-Routing:** Access applications via in-portal routes (`/#/photocraft`) or standalone endpoints (`/photocraft/`).
- **Firebase Hosting Integration:** Configured with trailing-slash normalization and WebAssembly headers for one-command deployment.

---

## 🚀 The CraftApps Suite

| Application | Sub-Route | Category | Equivalent Software | Core Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **PhotoCraft** | [`/photocraft/`](https://craftapps.web.app/photocraft/) | Design | **Adobe Photoshop** | Non-destructive layers, blend modes, adjustments, masks, GPU raster pipeline |
| **VectorCraft** | [`/vectorcraft/`](https://craftapps.web.app/vectorcraft/) | Design | **Adobe Illustrator** | Precision Bézier pen tool, boolean path ops, SVG vector design |
| **CADCraft** | [`/cadcraft/`](https://craftapps.web.app/cadcraft/) | Engineering | **Autodesk AutoCAD** | Command line, object snaps, layers, dimensions, hatches, DXF drafting |
| **DesignCraft** | [`/designcraft/`](https://craftapps.web.app/designcraft/) | Publishing | **Adobe InDesign** | Multi-page spreads, master page templating, linked text frames |
| **FilmCraft** | [`/filmcraft/`](https://craftapps.web.app/filmcraft/) | Video | **Adobe Premiere Pro** | Multi-track timeline, video cutting, transitions, color grading |
| **EffectCraft** | [`/effectcraft/`](https://craftapps.web.app/effectcraft/) | VFX | **Adobe After Effects** | Keyframe animation, visual effects compositing, audio worklets |
| **SoundCraft** | [`/soundcraft/`](https://craftapps.web.app/soundcraft/) | Audio | **Avid Pro Tools** | Digital Audio Workstation (DAW), multi-track recording & mixing, DSP |
| **LightCraft** | [`/lightcraft/`](https://craftapps.web.app/lightcraft/) | Photography | **Adobe Lightroom** | RAW development, tone curves, exposure grading, OPFS private storage |
| **PdfCraft** | [`/pdfcraft/`](https://craftapps.web.app/pdfcraft/) | Documents | **Adobe Acrobat** | Inspect, annotate, reorder, merge, split, form fill, and redact PDFs |
| **DeckCraft** | [`/deckcraft/`](https://craftapps.web.app/deckcraft/) | Productivity | **MS PowerPoint** | Slide deck creator, vector shapes, animations, presenter mode |
| **GridCraft** | [`/gridcraft/`](https://craftapps.web.app/gridcraft/) | Productivity | **Microsoft Excel** | Fast formula calculation engine, data grid, charts, local tables |
| **WordCraft** | [`/wordcraft/`](https://craftapps.web.app/wordcraft/) | Productivity | **Microsoft Word** | Rich text document design, typography styles, tables, citations |

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

This repository includes an automated workflow at [`.github/workflows/firebase-deploy.yml`](.github/workflows/firebase-deploy.yml) that automatically deploys to Firebase Hosting whenever you push to `main` (or trigger it manually via `workflow_dispatch`).

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

## 🔒 Privacy & Security

- **100% Client-Side:** Files you open, edit, or save remain in your browser's local memory or Origin Private File System (OPFS).
- **No Uploads:** Your media, documents, and CAD drawings never leave your computer.
- **Offline Capable:** Once cached by your browser, applications continue operating even when disconnected.

---

## 📄 License & Attribution

- Built on open-source Rust libraries and WebAssembly tooling.
- Core applications are licensed under **MIT** or **Apache-2.0**.
- Bundled UI fonts are governed by the **SIL Open Font License (OFL)**.
