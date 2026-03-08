# STAR Interview Prep

A lightweight local web app for creating, reviewing, and managing your STAR (Situation, Task, Action, Result) interview examples. All data is stored in a single YAML file — no database, no cloud, no account required.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python3 server.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

## Features

- **Create, edit, and delete** STAR examples with a clean card-based UI
- **Filter** by competency, company, completeness, recency, and tags
- **Full-text search** across all fields
- **Manage competencies** — add, rename, or remove competencies from the UI
- **Automatic backups** — a `.backup.yaml` is created before every save
- **No external dependencies** — runs locally with Flask and vanilla JavaScript

## Data File

Your examples live in `star_examples.yaml`. The file ships with 2 sample entries to get you started — feel free to delete them and add your own.

### Structure

```yaml
competency_taxonomy:
  - name: Strategic Analysis & Insight
    description: ...

examples:
  - id: star_001
    title: ...
    primary_competency: ...
    company: ...
    role: ...
    period: ...
    tags: [...]
    completeness: full | partial | draft
    recency: recent | old
    situation: ...
    task: ...
    action: ...
    result: ...
    key_metrics: [...]
    review_notes: ...
```

## Customising Competencies

The app ships with 10 competencies oriented toward strategy roles. You can customise them in two ways:

1. **Via the UI** — click "Manage Competencies" in the sidebar
2. **Directly in YAML** — edit the `competency_taxonomy` section in `star_examples.yaml`

## Configuration

The server defaults to `127.0.0.1:5001`. Override with environment variables:

```bash
HOST=0.0.0.0 PORT=8080 DEBUG=true python3 server.py
```

## License

MIT
