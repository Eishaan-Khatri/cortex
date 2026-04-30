"""
CORTEX — Memory System
Tracks generated content to prevent repeats within a configurable window.
"""

import os
import json
from datetime import datetime, timedelta


class Memory:
    """Manages the no-repeat history buffer."""

    def __init__(self, history_file="logs/history.json", no_repeat_days=14):
        self.history_file = history_file
        self.no_repeat_days = no_repeat_days
        self.history = self._load()

    def _load(self):
        """Load history from disk."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"entries": []}
        return {"entries": []}

    def save(self):
        """Save history to disk."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def add_entry(self, date, topic, keywords, arxiv_ids=None, commit_messages=None):
        """Record today's generated content."""
        entry = {
            "date": date if isinstance(date, str) else date.strftime("%Y-%m-%d"),
            "topic": topic,
            "keywords": keywords,
            "arxiv_ids": arxiv_ids or [],
            "commit_messages": commit_messages or [],
        }
        self.history["entries"].append(entry)
        self._prune()
        self.save()

    def _prune(self):
        """Remove entries older than the no-repeat window."""
        cutoff = datetime.now() - timedelta(days=self.no_repeat_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        self.history["entries"] = [
            e for e in self.history["entries"]
            if e.get("date", "") >= cutoff_str
        ]

    def get_avoidance_context(self):
        """
        Generate a text block listing recently covered topics and keywords
        to inject into AI prompts for deduplication.
        """
        if not self.history["entries"]:
            return "No previous history. Generate freely."

        lines = ["RECENTLY COVERED (avoid repeating these):"]
        for entry in self.history["entries"][-14:]:
            date = entry.get("date", "unknown")
            topic = entry.get("topic", "unknown")
            keywords = ", ".join(entry.get("keywords", [])[:10])
            arxiv = ", ".join(entry.get("arxiv_ids", [])[:5])

            line = f"  [{date}] {topic}: {keywords}"
            if arxiv:
                line += f" | Papers: {arxiv}"
            lines.append(line)

        return "\n".join(lines)

    def get_recent_keywords(self):
        """Return all keywords from the current window as a set."""
        keywords = set()
        for entry in self.history["entries"]:
            keywords.update(entry.get("keywords", []))
        return keywords

    def get_recent_arxiv_ids(self):
        """Return all ArXiv IDs from the current window."""
        ids = set()
        for entry in self.history["entries"]:
            ids.update(entry.get("arxiv_ids", []))
        return ids

    def was_topic_covered_today(self, date=None):
        """Check if we already generated content for today."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        elif not isinstance(date, str):
            date = date.strftime("%Y-%m-%d")
        return any(e.get("date") == date for e in self.history["entries"])
