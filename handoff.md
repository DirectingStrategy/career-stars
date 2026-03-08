# STAR Interview Prep — Handoff

## What This App Does

A single-page web app for managing behavioural interview examples in STAR format (Situation, Task, Action, Result). Users create, edit, filter, and review STAR cards, with optional AI-powered feedback via OpenAI or Anthropic APIs.

## Tech Stack

| Layer | Detail |
|-------|--------|
| Backend | Flask (Python 3), no database — reads/writes `star_examples.yaml` |
| Frontend | Vanilla JS + CSS in a single `static/index.html` (~1,400 lines) |
| AI | Proxy endpoint on Flask calls OpenAI or Anthropic; API key stored in `localStorage` |
| Markdown | `marked.js` via CDN for rendering AI review notes and STAR content |
| Dev server | `python3 server.py` on port 5001 (config in `.claude/launch.json`) |

## File Map

```
server.py                 — Flask backend: all API routes + AI review proxy
static/index.html         — Full frontend: HTML, CSS, JS in one file
star_examples.yaml        — Data store (YAML)
star_examples.backup.yaml — Auto-backup before each write
requirements.txt          — flask, pyyaml, requests
.claude/launch.json       — Dev server config for Claude Code preview
```

## Key API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/api/meta` | Competencies, companies, tags for filter dropdowns |
| GET | `/api/stars?competency=&company=&q=...` | List/filter STAR examples |
| POST | `/api/stars` | Create new STAR |
| PUT | `/api/stars/<id>` | Update a STAR |
| DELETE | `/api/stars/<id>` | Delete a STAR |
| POST | `/api/ai-review/<id>` | AI feedback (body: `{api_key, provider, model}`) |
| GET/POST/PUT/DELETE | `/api/competencies[/<idx>]` | CRUD for competency taxonomy |

## Frontend Architecture

- **Sidebar**: Filters (competency, company, completeness, recency, tags, free-text search) + "New STAR" / "Settings" buttons
- **Main area**: Card grid showing STAR summaries with competency badge and status pill
- **Modal**: Opens for create/edit/view. Three modes controlled by `openModal(star, mode)`:
  - `"edit"` — form fields for all STAR data
  - `"view"` — read-only with markdown rendering + "Get AI Feedback" button
  - `"new"` — blank form for creation
- **Settings overlay**: Provider/model/API-key config stored in `localStorage`
- **Competency Manager**: Inline CRUD for the competency taxonomy (accessed via sidebar link)

## AI Review Feature

- User configures provider (OpenAI/Anthropic), model, and API key in Settings
- "Get AI Feedback" button in view mode sends STAR content to `/api/ai-review/<id>`
- Flask proxies to the chosen LLM API using the user's key
- Response is saved to `review_notes` field and rendered as markdown
- Prompt is in `AI_REVIEW_PROMPT` constant (`server.py` line 33–53) — produces an **Overall** verdict + **Top 3 improvement opportunities**, capped at 200 words

## Data Model (per STAR example in YAML)

```yaml
- id: star_001
  title: "..."
  primary_competency: "Strategic Analysis & Insight"
  secondary_competencies: ["Communication & Storytelling"]
  company: "Acme Corp"
  role: "Senior Analyst"
  period: "2024"
  tags: [growth, m&a]
  recency: recent          # recent | old
  completeness: complete   # complete | in_progress
  situation: "..."
  task: "..."
  action: "..."
  result: "..."
  key_metrics: ["Metric 1", "Metric 2"]
  review_notes: "..."      # AI feedback or manual notes (markdown)
  source: "manual entry"
```

## Running the App

```bash
pip install -r requirements.txt
python3 server.py
# Open http://localhost:5001
```

## Known Limitations / Areas for Improvement

- **Single-file frontend**: `index.html` is ~1,400 lines. Could benefit from splitting into components if it grows further.
- **No auth**: API keys are stored in `localStorage` and sent per-request. Fine for local use only.
- **YAML storage**: Works for small datasets but won't scale to hundreds of examples.
- **No undo/versioning**: Only one `.backup.yaml` is kept (overwritten on each save).
- **No tests**: No unit or integration tests exist yet.
- **No mobile optimisation**: Layout is desktop-first with a fixed sidebar.
- **AI feedback overwrites**: Running AI review replaces any existing `review_notes` rather than appending.
- **Competency taxonomy is user-customisable** but the default set is strategy-focused — may need updating for other roles.

## Deployment & Distribution Strategy

### Target audience hurdles

Strategy professionals and peers who are not familiar with terminals face several barriers running a local Flask app:

1. **Python not installed** — many corporate Windows laptops don't ship with Python; installing requires IT/admin approval
2. **Terminal intimidation** — `pip install` and `python3 server.py` are unfamiliar; debugging errors (wrong version, port conflicts) is a blocker
3. **Corporate device restrictions** — MDM policies may block software installs, pip packages, or localhost servers; some orgs lock down the terminal entirely
4. **No persistent app experience** — no desktop icon, must remember to open terminal and run the command, closing the terminal stops the app

### Options explored

| Approach | Effort | Verdict |
|----------|--------|---------|
| **Static HTML + localStorage** | Medium | Removes all hurdles — just open a `.html` file. No server needed. |
| **Hosted PWA** | Low | Recommended. Users visit a URL, click "Install". Works on corporate devices. |
| **Capacitor (mobile wrapper)** | Medium | Optional phase 2. Wraps existing web code for Google Play ($25) / iOS App Store ($99/yr). |
| **Electron / Tauri (desktop app)** | High | Overkill. Large downloads, signing certificates needed, corporate security may block. |

### Chosen approach: Hosted PWA

**How it works:**
- Host a single HTML file on free static hosting (Vercel, Netlify, GitHub Pages)
- Users visit the HTTPS URL and click "Install" — app installs to desktop/home screen
- Opens in a standalone window (no browser chrome), behaves like a native app
- Automatic updates — push a change to the hosted files, users get it on next open

**Data persistence:**
- All data stored in browser `localStorage` / `IndexedDB` — never leaves the user's device
- Export/import JSON buttons for backup and cross-device transfer
- Print via browser's built-in print dialog (with a print stylesheet)
- Auto-save to a real file via File System Access API (Chrome/Edge); localStorage fallback for Safari/Firefox

**PWA requirements (to add):**
- `manifest.json` — app name, icons (192px + 512px), display mode, theme colour
- `sw.js` — service worker with fetch handler for offline caching
- HTTPS hosting (provided free by Vercel/Netlify/GitHub Pages)

**Corporate device compatibility:**
- No admin rights needed — it's just a website
- Works through most MDM policies
- Chrome, Edge, Safari, Firefox all support PWA installation

**Costs:** $0 on free hosting tiers. Optional $10–15/yr for a custom domain.

### Status

PWA conversion has **not yet started**. The current app is a Flask-served SPA. Converting to PWA involves:
1. Replacing Flask API calls with localStorage read/write in the frontend
2. Bundling sample data into the HTML
3. Adding `manifest.json` and `sw.js`
4. Adding export/import/print functionality
5. Deploying to static hosting
