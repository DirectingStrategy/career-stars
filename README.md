# STAR Lab

A progressive web app for creating, reviewing, and managing your STAR (Situation, Task, Action, Result) interview examples. All data is stored in your browser — no account, no server, no setup required.

## Features

- **Create, edit, and delete** STAR examples with a clean card-based UI
- **AI-powered review** — get feedback on your STARs using OpenAI or Anthropic (bring your own API key)
- **Filter and search** — by competency, company, completeness, recency, tags, and full-text search
- **Manage competencies** — add, rename, or remove competencies from the sidebar
- **PWA support** — install on your phone or desktop, works offline
- **Data export** — download your data as JSON for backup or transfer
- **No backend** — runs entirely in your browser using localStorage

## Live App

Hosted on Vercel — see the repo's About section for the link.

## Local Development

Serve the `static/` directory with any static file server:

```bash
# Python
python3 -m http.server 8000 -d static

# Node
npx serve static
```

Then open [http://localhost:8000](http://localhost:8000).

> Note: Service worker and PWA install require HTTPS, so these features only work on the deployed version or via `localhost`.

## Data Storage

All data lives in your browser's localStorage under the key `starApp`. The app ships with 12 default competencies and 2 sample STAR examples to get you started.

## Deployment

The app deploys as a static site on Vercel. Configuration is in `vercel.json` — it serves the `static/` directory and rewrites all routes to `index.html` for SPA navigation.

To deploy your own instance, connect this repo to Vercel and it will auto-deploy on every push.

## License

MIT
