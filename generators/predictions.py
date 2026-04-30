"""
CORTEX — Prediction System
Generates monthly predictions and scores old ones.
"""

import os
import json
from datetime import datetime, timedelta
from core.utils import read_file, write_file, append_to_file


PREDICTIONS_JSON = "logs/predictions.json"
PREDICTIONS_MD = "PREDICTIONS.md"

PREDICTIONS_HEADER = """# 🔮 CORTEX Prediction Log

Monthly predictions about the future of AI and technology.
Each prediction is scored after 6 months.

| Symbol | Meaning |
|:-------|:--------|
| 🟢 | Correct |
| 🔴 | Wrong |
| 🟡 | Partially correct |
| ⏳ | Pending (not yet due) |

---

"""


def generate_predictions(ai_engine, persona_prompt):
    """Generate 5 new predictions for the next 6 months."""

    month = datetime.now().strftime("%B %Y")
    due_date = (datetime.now() + timedelta(days=180)).strftime("%B %Y")

    prompt = f"""Generate 5 specific, falsifiable predictions about AI and technology
for the next 6 months (due: {due_date}).

Each prediction must be:
- SPECIFIC enough to be scored as right or wrong
- Based on current observable trends
- Covering different domains (NLP, CV, BCI, industry, open-source)

Provide a JSON object:
{{
    "predictions": [
        {{
            "id": "P-YYYY-MM-NNN",
            "prediction": "The specific prediction text",
            "domain": "NLP/CV/BCI/XAI/Industry/Open Source",
            "confidence": 60-95,
            "reasoning": "1-2 sentences on why you believe this"
        }}
    ]
}}

Use prediction IDs in format P-{datetime.now().strftime('%Y-%m')}-001 through 005."""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if not result or not isinstance(result, dict):
        return []

    predictions = result.get("predictions", [])
    if not predictions:
        return []

    # Save to JSON
    all_predictions = _load_predictions()
    for pred in predictions:
        pred["created"] = datetime.now().strftime("%Y-%m-%d")
        pred["due"] = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        pred["status"] = "pending"
        pred["score"] = None
        all_predictions.append(pred)

    _save_predictions(all_predictions)
    _regenerate_predictions_md(all_predictions)

    print(f"  [PREDICTIONS] Generated {len(predictions)} new predictions")
    return predictions


def score_predictions(ai_engine, persona_prompt):
    """Score predictions that are due."""

    all_predictions = _load_predictions()
    today = datetime.now().strftime("%Y-%m-%d")

    due_predictions = [
        p for p in all_predictions
        if p.get("status") == "pending" and p.get("due", "9999-99-99") <= today
    ]

    if not due_predictions:
        print("  [PREDICTIONS] No predictions due for scoring")
        return []

    pred_text = "\n".join(
        f"- [{p.get('id')}] {p.get('prediction')}" for p in due_predictions
    )

    prompt = f"""Score these AI predictions that are now due. For each one,
determine if they came true based on current knowledge.

PREDICTIONS TO SCORE:
{pred_text}

For each prediction, provide:
1. "id": The prediction ID
2. "status": "correct", "wrong", or "partial"
3. "explanation": Why you scored it this way (1-2 sentences, reference real events)

Respond as JSON: {{"scores": [...]}}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if not result or not isinstance(result, dict):
        return []

    scores = result.get("scores", [])
    score_map = {s["id"]: s for s in scores}

    # Update predictions
    for pred in all_predictions:
        if pred.get("id") in score_map:
            s = score_map[pred["id"]]
            pred["status"] = s.get("status", "pending")
            pred["score"] = s.get("explanation", "")

    _save_predictions(all_predictions)
    _regenerate_predictions_md(all_predictions)

    print(f"  [PREDICTIONS] Scored {len(scores)} predictions")
    return scores


def _load_predictions():
    if os.path.exists(PREDICTIONS_JSON):
        try:
            with open(PREDICTIONS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_predictions(data):
    os.makedirs(os.path.dirname(PREDICTIONS_JSON), exist_ok=True)
    with open(PREDICTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _regenerate_predictions_md(all_predictions):
    """Regenerate the PREDICTIONS.md file."""
    content = PREDICTIONS_HEADER

    # Sort by ID descending (latest at top)
    all_predictions.sort(key=lambda x: x.get("id", ""), reverse=True)

    # Group by status
    pending = [p for p in all_predictions if p.get("status") == "pending"]
    scored = [p for p in all_predictions if p.get("status") != "pending"]


    if pending:
        content += "## ⏳ Active Predictions\n\n"
        for p in pending:
            conf = p.get("confidence", "?")
            content += f"- **[{p.get('id')}]** {p.get('prediction')} "
            content += f"*(Confidence: {conf}% | Due: {p.get('due', '?')})*\n"
            content += f"  - Reasoning: {p.get('reasoning', '')}\n\n"

    if scored:
        content += "\n## 📊 Scored Predictions\n\n"
        for p in scored:
            status = p.get("status", "unknown")
            icon = {"correct": "🟢", "wrong": "🔴", "partial": "🟡"}.get(status, "❓")
            content += f"- {icon} **[{p.get('id')}]** {p.get('prediction')}\n"
            content += f"  - Score: {p.get('score', 'No explanation')}\n\n"

    write_file(PREDICTIONS_MD, content)
