"""
CORTEX — Field Sentiment Analyzer
Generates "mood scores" for each research field.
"""

import json
import os
from datetime import datetime
from core.utils import format_progress_bar


SENTIMENT_FILE = "logs/sentiment.json"


def generate_sentiment(ai_engine, persona_prompt):
    """
    Generate sentiment scores for all tracked research fields.

    Returns a dict: {"NLP": {"score": 82, "label": "Optimistic", "reason": "..."}, ...}
    """

    prompt = """Assess the current momentum and health of each of these AI research fields
based on recent developments, publication rates, and industry adoption.

Fields to assess:
1. NLP (Natural Language Processing)
2. CV (Computer Vision)
3. XAI (Explainable AI)
4. BCI (Brain-Computer Interfaces)
5. Emerging Tech (Quantum ML, Neuromorphic, Robotics)

For each field, provide:
1. "score": A number 0-100 representing momentum/health
2. "label": One of ["Surging", "Optimistic", "Active", "Cautious", "Stagnant", "Declining"]
3. "reason": A single, specific sentence explaining why (reference a real trend or event)

Respond with a JSON object: {"fields": {"NLP": {...}, "CV": {...}, ...}}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if result and isinstance(result, dict) and "fields" in result:
        sentiment = result["fields"]
        _save_sentiment(sentiment)
        return sentiment

    # Fallback
    return _load_sentiment() or _default_sentiment()


def format_sentiment_dashboard(sentiment):
    """Format sentiment data as an ASCII dashboard for the README."""
    lines = ["```"]
    for field, data in sentiment.items():
        if isinstance(data, dict):
            score = data.get("score", 50)
            label = data.get("label", "Active")
            reason = data.get("reason", "")
            bar = format_progress_bar(score)
            lines.append(f"{field:>12}:  {bar} {score}% [{label}] — {reason}")
    lines.append("```")
    return "\n".join(lines)


def _save_sentiment(sentiment):
    """Save sentiment data to disk."""
    os.makedirs(os.path.dirname(SENTIMENT_FILE), exist_ok=True)
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "fields": sentiment,
    }
    with open(SENTIMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_sentiment():
    """Load last saved sentiment."""
    if os.path.exists(SENTIMENT_FILE):
        try:
            with open(SENTIMENT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("fields")
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _default_sentiment():
    """Default sentiment values."""
    return {
        "NLP": {"score": 75, "label": "Active", "reason": "Steady progress in open-source LLMs."},
        "CV": {"score": 70, "label": "Active", "reason": "Diffusion models maturing rapidly."},
        "XAI": {"score": 50, "label": "Cautious", "reason": "Regulatory pressure increasing."},
        "BCI": {"score": 40, "label": "Emerging", "reason": "Clinical trials expanding slowly."},
        "Emerging": {"score": 55, "label": "Active", "reason": "Quantum ML gaining traction."},
    }
