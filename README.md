# STAR Lab

A progressive web app for creating, reviewing, and managing your STAR (Situation, Task, Action, Result) interview examples. All data is stored in your browser — no account, no server, no setup required.

## Features

- **Create, edit, and delete** STAR examples with a clean card-based UI
- **AI-powered review** — get feedback on your STARs using OpenAI (bring your own API key)
- **Filter and search** — by competency, company, completeness, recency, tags, and full-text search
- **Manage competencies** — add, rename, or remove competencies from the sidebar
- **PWA support** — install as a desktop or tablet app, works offline
- **Data export** — download your data as JSON for backup or transfer
- **No backend** — runs entirely in your browser using localStorage

## Live App

Hosted on Vercel — see the repo's About section for the link.

## Data Storage

All data lives in your browser's localStorage under the key `starApp`. The app ships with 12 default competencies and 2 sample STAR examples to get you started.

## Data Persistence & Backup

Your data lives only in your browser. It will persist between sessions, but can be lost if you clear browser data — even if the app is installed as a PWA.

**To protect your data:**
- Export your STARs regularly using the Export JSON feature
- Install the app for improved storage durability
- The app reminds you to back up every 2 days

There is no cloud sync or server-side storage — this is by design to keep your data private.

## Deployment

The app deploys as a static site on Vercel. Configuration is in `vercel.json` — it serves the `static/` directory and rewrites all routes to `index.html` for SPA navigation.

To deploy your own instance, connect this repo to Vercel and it will auto-deploy on every push.

## License

MIT
