# STAR Lab

A progressive web app for creating, reviewing, and managing your STAR (Situation, Task, Action, Result) interview examples. All data is stored in your browser — no account, no server, no setup required.

## Features

- **Create, edit, and delete** STAR examples with a clean card-based UI
- **AI-powered review** — get feedback on your STARs using OpenAI (bring your own API key)
- **Filter and search** — by competency, company, completeness, recency, tags, and full-text search
- **Manage competencies** — add, rename, or remove competencies from the sidebar
- **PWA support** — install as a desktop or tablet app, works offline
- **Data export/import** — download your data as JSON or CSV for backup or transfer
- **No backend** — runs entirely in your browser using localStorage

## What is the STAR Method?

- **Situation** — Set the scene. What was the context and what was at stake?
- **Task** — What was your specific responsibility — distinct from your team's?
- **Action** — What did *you* personally do? Be concrete and first-person.
- **Result** — What was the outcome? Quantify where possible.

## Getting Started

1. Click **+ Add New STAR** in the sidebar to create your first example.
2. Fill in all four sections. Save as *In Progress* until it's polished.
3. Use the filters to find the right example fast during interview prep.

## Competencies

The app ships with 12 default competencies tailored to **strategy and consulting roles**. Click **Manage** next to the Competency filter to edit, add, or remove competencies to match any role you're targeting.

## AI Review

- Open a STAR and click **Get AI Feedback** to get a coached review.
- Requires your own [OpenAI API key](https://platform.openai.com/api-keys). Enter it via the ⚙ Settings icon.
- Your key is stored only in your browser and sent directly to OpenAI — never to any server.

### Keeping your API key safe

Your key is stored in your browser's localStorage. This is convenient but not as secure as a system keychain. To limit your risk:

- **Create a separate key** — generate a dedicated API key just for STAR Lab at [platform.openai.com/api-keys](https://platform.openai.com/api-keys). If it's ever compromised, revoke it without affecting your other projects.
- **Set a spending limit** — in your OpenAI account under Billing → Limits, set a low monthly budget (e.g. $5). This caps the damage if the key leaks.
- **Restrict permissions** — when creating the key, limit it to only the Chat Completions endpoint and the models you use.
- **Revoke when not needed** — if you're done with AI reviews, delete the key from STAR Lab's Settings and revoke it in your OpenAI dashboard.
- **Avoid shared or public devices** — anyone with access to your browser profile or dev tools can read localStorage.
- **Watch your browser extensions** — extensions can read page data including localStorage. Consider using a minimal-extension profile.

## Export & Import

- **Export JSON** — full backup, re-importable on any device.
- **Export CSV** — for viewing in a spreadsheet.
- **Import JSON** — replaces all data. Export first as a backup.

## Install as an App

Installing STAR Lab gives your data the best chance of surviving browser updates and storage cleanup.

- **Chrome:** click the install icon in the address bar → Install.
- **Safari on Mac:** Share → Add to Dock.
- Once installed, the app opens in its own window and works offline.
- Even after installing, always keep a recent backup — clearing app/browser data will still erase your STARs.

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

## Get Help

Have a question or found a bug? Raise an issue on [GitHub](https://github.com/DirectingStrategy/career-stars/issues) or leave a comment on the blog post where you found this tool. The full source code is publicly available at [github.com/DirectingStrategy/career-stars](https://github.com/DirectingStrategy/career-stars).

## License

MIT
