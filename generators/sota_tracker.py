"""
CORTEX — SOTA Tracker
Maintains a State-of-the-Art benchmark table.
"""

import os
import json
from datetime import datetime
from core.utils import read_file, write_file


SOTA_FILE = "SOTA.md"
SOTA_DATA_FILE = "logs/sota.json"

SOTA_HEADER = """# 📊 State of the Art Tracker

Benchmarks and records tracked by CORTEX. Updated whenever a new SOTA result is detected.

> Last updated: {date}

---

| Task | Dataset | Model | Score | Paper | Date |
|:-----|:--------|:------|:------|:------|:-----|
"""


def update_sota(ai_engine, todays_content, topic, persona_prompt):
    """
    Check today's content for any new SOTA benchmark results.
    Update SOTA.md if found.
    """

    prompt = f"""Analyze the following research content from today's {topic['full_name']} coverage.
Identify any mentions of state-of-the-art (SOTA) benchmark results.

CONTENT:
{todays_content[:3000]}

For each SOTA result found, extract:
1. "task": The specific task (e.g., "Image Classification", "Machine Translation")
2. "dataset": The benchmark dataset (e.g., "ImageNet", "WMT14")
3. "model": The model name
4. "score": The metric and value (e.g., "95.3% top-1 accuracy")
5. "paper": ArXiv ID or paper title
6. "date": When the result was published (YYYY-MM or YYYY-MM-DD)

Return a JSON object: {{"sota_entries": [...]}}
If no SOTA results are found, return {{"sota_entries": []}}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=False,
    )

    if not result or not isinstance(result, dict):
        return []

    entries = result.get("sota_entries", [])
    if not entries:
        return []

    # Load existing data
    existing = _load_sota_data()

    # Add new entries (dedup by task+dataset)
    new_entries = []
    existing_keys = {(e["task"], e["dataset"]) for e in existing}
    for entry in entries:
        key = (entry.get("task", ""), entry.get("dataset", ""))
        if key not in existing_keys and key[0] and key[1]:
            existing.append(entry)
            new_entries.append(entry)
            existing_keys.add(key)

    if new_entries:
        _save_sota_data(existing)
        _regenerate_sota_md(existing)
        print(f"  [SOTA] Added {len(new_entries)} new benchmark entries")

    return new_entries


def _load_sota_data():
    """Load SOTA data from JSON."""
    if os.path.exists(SOTA_DATA_FILE):
        try:
            with open(SOTA_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_sota_data(data):
    """Save SOTA data to JSON."""
    os.makedirs(os.path.dirname(SOTA_DATA_FILE), exist_ok=True)
    with open(SOTA_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _regenerate_sota_md(data):
    """Regenerate the SOTA.md file from data."""
    header = SOTA_HEADER.format(date=datetime.now().strftime("%Y-%m-%d"))
    rows = []
    for entry in data:
        task = entry.get("task", "—")
        dataset = entry.get("dataset", "—")
        model = entry.get("model", "—")
        score = entry.get("score", "—")
        paper = entry.get("paper", "—")
        date = entry.get("date", "—")
        rows.append(f"| {task} | {dataset} | {model} | {score} | {paper} | {date} |")

    content = header + "\n".join(rows) + "\n"
    write_file(SOTA_FILE, content)
