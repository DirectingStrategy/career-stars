"""
STAR Interview Prep — Flask Backend
Reads/writes star_examples.yaml, serves API + static frontend.
Run: python3 server.py
"""

import os
import shutil
import yaml
import requests as http_requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static")

YAML_PATH = os.path.join(os.path.dirname(__file__), "star_examples.yaml")
BACKUP_PATH = os.path.join(os.path.dirname(__file__), "star_examples.backup.yaml")

DEFAULT_DATA = {
    "metadata": {
        "created": "",
        "description": "STAR Interview Prep",
    },
    "competency_taxonomy": [
        {"name": "Strategic Analysis & Insight", "description": "Applying frameworks, synthesising data, and generating actionable insights"},
        {"name": "Stakeholder Management & Influence", "description": "Building alignment across senior leadership and driving buy-in"},
        {"name": "Problem Solving Under Ambiguity", "description": "Structuring ill-defined problems and making decisions with incomplete data"},
        {"name": "Communication", "description": "Distilling complex analysis into clear narratives for executive audiences"},
        {"name": "Delivering Results & Execution", "description": "Achieving targets, operational excellence, accountability frameworks"},
    ],
    "examples": [],
}

AI_REVIEW_PROMPT = """You are a job interview coach. Review this behavioural STAR summary for the competency "{primary_competency}".

Areas to consider when rating the review and identifying improvement opportunities are:
- Situation - Is context specific with clear stakes, or vague?
- Task - Is the candidate's responsibility distinct from the team's?
- Action - Are steps concrete and first-person ("I did X")? Flag "helped with" or "was involved in".
- Result - Are outcomes quantified with metrics and a clear before/after?
- Competency fit - Does it convincingly demonstrate {primary_competency}?
- Interview readiness - Could this be delivered in 2-3 minutes?


Provide a response in markdown with an overall rating and UP TO 3 improvement opportunities. You do not need to provide all 3 improvement opportunities if the STAR is strong and there aren't 3 material improvements.  Use the below format and nothing else:

**Overall** Strong / Needs Work / Weak — one sentence why.

**Improvement opportunities**
1. [highest-impact fix with a reframing idea or example addition]
2. [second fix with a reframing idea or example addition]
3. [third fix with a reframing idea or example addition]

Keep your entire response under 200 words. Be specific with your suggestions but make examples (versus facts) clear with "e.g.". Use markdown."""


def load_yaml():
    if not os.path.exists(YAML_PATH):
        save_yaml(DEFAULT_DATA, backup=False)
        return DEFAULT_DATA.copy()
    with open(YAML_PATH, "r") as f:
        return yaml.safe_load(f) or DEFAULT_DATA.copy()


def save_yaml(data, backup=True):
    if backup and os.path.exists(YAML_PATH):
        shutil.copy2(YAML_PATH, BACKUP_PATH)
    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False, width=120)


# ── Serve frontend ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── API: metadata (competencies, companies, tags) ──────────────────────────

@app.route("/api/meta")
def get_meta():
    data = load_yaml()
    examples = data.get("examples", [])
    taxonomy = data.get("competency_taxonomy", [])

    companies = sorted(set(e.get("company", "") for e in examples if e.get("company")))
    all_tags = set()
    for e in examples:
        all_tags.update(e.get("tags", []))

    return jsonify({
        "competencies": [t["name"] for t in taxonomy],
        "companies": companies,
        "tags": sorted(all_tags),
        "completeness_options": ["complete", "in_progress"],
    })


# ── API: list / filter stars ───────────────────────────────────────────────

@app.route("/api/stars")
def get_stars():
    data = load_yaml()
    examples = data.get("examples", [])

    competency = request.args.get("competency", "").strip()
    company = request.args.get("company", "").strip()
    completeness = request.args.get("completeness", "").strip()
    recency = request.args.get("recency", "").strip().lower()
    tags_param = request.args.get("tags", "").strip().lower()
    required_tags = [t.strip() for t in tags_param.split(",") if t.strip()] if tags_param else []
    q = request.args.get("q", "").strip().lower()

    filtered = []
    for e in examples:
        if competency and competency != e.get("primary_competency") and competency not in (e.get("secondary_competencies") or []):
            continue
        if company and e.get("company") != company:
            continue
        if completeness and e.get("completeness") != completeness:
            continue
        if recency and e.get("recency") != recency:
            continue
        if required_tags:
            example_tags = [t.lower() for t in e.get("tags", [])]
            if not all(rt in example_tags for rt in required_tags):
                continue
        if q:
            searchable = " ".join([
                str(e.get("title", "")),
                str(e.get("situation", "")),
                str(e.get("task", "")),
                str(e.get("action", "")),
                str(e.get("result", "")),
                str(e.get("company", "")),
                str(e.get("role", "")),
                " ".join(e.get("tags", [])),
            ]).lower()
            if q not in searchable:
                continue
        filtered.append(e)

    return jsonify({"examples": filtered, "total": len(examples), "filtered": len(filtered)})


# ── API: create a new star ─────────────────────────────────────────────────

@app.route("/api/stars", methods=["POST"])
def create_star():
    data = load_yaml()
    examples = data.get("examples", [])

    existing_nums = []
    for e in examples:
        eid = e.get("id", "")
        if eid.startswith("star_"):
            try:
                existing_nums.append(int(eid.split("_")[1]))
            except ValueError:
                pass
    next_num = max(existing_nums, default=0) + 1
    new_id = f"star_{next_num:03d}"

    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No data provided"}), 400

    new_star = {
        "id": new_id,
        "title": payload.get("title", "Untitled"),
        "primary_competency": payload.get("primary_competency", ""),
        "secondary_competencies": payload.get("secondary_competencies", []),
        "company": payload.get("company", ""),
        "role": payload.get("role", ""),
        "period": payload.get("period", ""),
        "tags": payload.get("tags", []),
        "recency": payload.get("recency", "old"),
        "completeness": payload.get("completeness", "in_progress"),
        "situation": payload.get("situation", ""),
        "task": payload.get("task", ""),
        "action": payload.get("action", ""),
        "result": payload.get("result", ""),
        "key_metrics": payload.get("key_metrics", []),
        "review_notes": payload.get("review_notes", ""),
        "source": payload.get("source", "manual entry"),
    }

    data["examples"].append(new_star)
    save_yaml(data)

    return jsonify({"status": "created", "example": new_star}), 201


# ── API: update a single star ──────────────────────────────────────────────

@app.route("/api/stars/<star_id>", methods=["PUT"])
def update_star(star_id):
    data = load_yaml()
    examples = data.get("examples", [])

    target = None
    target_idx = None
    for i, e in enumerate(examples):
        if e.get("id") == star_id:
            target = e
            target_idx = i
            break

    if target is None:
        return jsonify({"error": f"STAR {star_id} not found"}), 404

    updates = request.get_json()
    if not updates:
        return jsonify({"error": "No data provided"}), 400

    editable_fields = [
        "title", "primary_competency", "secondary_competencies",
        "company", "role", "period", "tags", "recency", "completeness",
        "situation", "task", "action", "result",
        "key_metrics", "review_notes", "source",
    ]
    for field in editable_fields:
        if field in updates:
            target[field] = updates[field]

    if target.get("completeness") == "complete" and target.get("title", "").startswith("DRAFT — "):
        target["title"] = target["title"].replace("DRAFT — ", "")

    data["examples"][target_idx] = target
    save_yaml(data)

    return jsonify({"status": "saved", "example": target})


# ── API: delete a star ─────────────────────────────────────────────────────

@app.route("/api/stars/<star_id>", methods=["DELETE"])
def delete_star(star_id):
    data = load_yaml()
    examples = data.get("examples", [])

    target_idx = None
    for i, e in enumerate(examples):
        if e.get("id") == star_id:
            target_idx = i
            break

    if target_idx is None:
        return jsonify({"error": f"STAR {star_id} not found"}), 404

    removed = examples.pop(target_idx)
    save_yaml(data)

    return jsonify({"status": "deleted", "id": removed.get("id")})


# ── API: AI review ────────────────────────────────────────────────────────

@app.route("/api/ai-review/<star_id>", methods=["POST"])
def ai_review(star_id):
    data = load_yaml()
    examples = data.get("examples", [])

    target = None
    for e in examples:
        if e.get("id") == star_id:
            target = e
            break

    if target is None:
        return jsonify({"error": f"STAR {star_id} not found"}), 404

    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No data provided"}), 400

    api_key = payload.get("api_key", "").strip()
    provider = payload.get("provider", "openai").strip().lower()
    model = payload.get("model", "").strip()

    if not api_key:
        return jsonify({"error": "API key is required. Open Settings to configure it."}), 400

    star_content = (
        f"Title: {target.get('title', '')}\n"
        f"Primary Competency: {target.get('primary_competency', '')}\n"
        f"Secondary Competencies: {', '.join(target.get('secondary_competencies', []))}\n"
        f"Company: {target.get('company', '')}\n"
        f"Role: {target.get('role', '')}\n"
        f"\nSITUATION:\n{target.get('situation', '(empty)')}\n"
        f"\nTASK:\n{target.get('task', '(empty)')}\n"
        f"\nACTION:\n{target.get('action', '(empty)')}\n"
        f"\nRESULT:\n{target.get('result', '(empty)')}\n"
        f"\nKEY METRICS:\n{chr(10).join(target.get('key_metrics', [])) or '(none)'}"
    )

    system_prompt = AI_REVIEW_PROMPT.format(
        primary_competency=target.get("primary_competency", "Unknown")
    )

    try:
        if provider == "anthropic":
            review_text = _call_anthropic(api_key, model or "claude-sonnet-4-20250514", system_prompt, star_content)
        else:
            review_text = _call_openai(api_key, model or "gpt-4o-mini", system_prompt, star_content)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 502

    # Save review into the STAR's review_notes
    for e in data.get("examples", []):
        if e.get("id") == star_id:
            e["review_notes"] = review_text
            break
    save_yaml(data)

    return jsonify({"status": "ok", "review_notes": review_text})


def _call_openai(api_key, model, system_prompt, user_content):
    resp = http_requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code != 200:
        body = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
        err_msg = body.get("error", {}).get("message", resp.text[:300])
        raise Exception(f"OpenAI API error ({resp.status_code}): {err_msg}")
    return resp.json()["choices"][0]["message"]["content"]


def _call_anthropic(api_key, model, system_prompt, user_content):
    resp = http_requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_content}],
        },
        timeout=60,
    )
    if resp.status_code != 200:
        body = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
        err_msg = body.get("error", {}).get("message", resp.text[:300])
        raise Exception(f"Anthropic API error ({resp.status_code}): {err_msg}")
    return resp.json()["content"][0]["text"]


# ── API: competency CRUD ──────────────────────────────────────────────────

@app.route("/api/competencies")
def list_competencies():
    data = load_yaml()
    taxonomy = data.get("competency_taxonomy", [])
    return jsonify({"competencies": taxonomy})


@app.route("/api/competencies", methods=["POST"])
def create_competency():
    data = load_yaml()
    taxonomy = data.get("competency_taxonomy", [])

    payload = request.get_json()
    if not payload or not payload.get("name", "").strip():
        return jsonify({"error": "Name is required"}), 400

    name = payload["name"].strip()
    if any(c["name"] == name for c in taxonomy):
        return jsonify({"error": f"Competency '{name}' already exists"}), 409

    new_comp = {
        "name": name,
        "description": payload.get("description", "").strip(),
    }
    taxonomy.append(new_comp)
    data["competency_taxonomy"] = taxonomy
    save_yaml(data)

    return jsonify({"status": "created", "competency": new_comp}), 201


@app.route("/api/competencies/<int:idx>", methods=["PUT"])
def update_competency(idx):
    data = load_yaml()
    taxonomy = data.get("competency_taxonomy", [])

    if idx < 0 or idx >= len(taxonomy):
        return jsonify({"error": "Competency not found"}), 404

    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No data provided"}), 400

    old_name = taxonomy[idx]["name"]
    new_name = payload.get("name", old_name).strip()

    if new_name != old_name and any(c["name"] == new_name for c in taxonomy):
        return jsonify({"error": f"Competency '{new_name}' already exists"}), 409

    taxonomy[idx]["name"] = new_name
    if "description" in payload:
        taxonomy[idx]["description"] = payload["description"].strip()

    # Rename in all examples that reference the old name
    if new_name != old_name:
        for e in data.get("examples", []):
            if e.get("primary_competency") == old_name:
                e["primary_competency"] = new_name
            sec = e.get("secondary_competencies", [])
            e["secondary_competencies"] = [new_name if s == old_name else s for s in sec]

    data["competency_taxonomy"] = taxonomy
    save_yaml(data)

    return jsonify({"status": "saved", "competency": taxonomy[idx]})


@app.route("/api/competencies/<int:idx>", methods=["DELETE"])
def delete_competency(idx):
    data = load_yaml()
    taxonomy = data.get("competency_taxonomy", [])

    if idx < 0 or idx >= len(taxonomy):
        return jsonify({"error": "Competency not found"}), 404

    name = taxonomy[idx]["name"]

    # Check if any examples reference this competency
    for e in data.get("examples", []):
        if e.get("primary_competency") == name:
            return jsonify({"error": f"Cannot delete: used as primary competency in '{e.get('title', e.get('id'))}'. Reassign it first."}), 409
        if name in e.get("secondary_competencies", []):
            return jsonify({"error": f"Cannot delete: used as secondary competency in '{e.get('title', e.get('id'))}'. Remove it first."}), 409

    removed = taxonomy.pop(idx)
    data["competency_taxonomy"] = taxonomy
    save_yaml(data)

    return jsonify({"status": "deleted", "name": removed["name"]})


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5001"))
    debug = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")
    print(f"YAML: {YAML_PATH}")
    print(f"Open http://localhost:{port}")
    app.run(host=host, port=port, debug=debug)
