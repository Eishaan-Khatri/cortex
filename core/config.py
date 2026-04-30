"""
CORTEX — Configuration Loader
Loads config.yml and resolves today's research topic.
"""

import os
import yaml
from datetime import datetime


_CONFIG_CACHE = None


def load_config(config_path=None):
    """Load and cache the configuration from config.yml."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")

    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f)

    return _CONFIG_CACHE


def get_todays_topic(config=None, date=None):
    """
    Determine today's research topic based on the day of the week.
    Returns a dict: {"key": "NLP", "full_name": "...", "subtopics": [...]}
    """
    if config is None:
        config = load_config()

    if date is None:
        date = datetime.now()

    day_name = date.strftime("%A").lower()
    schedule = config["schedule"]

    # Map day names to schedule keys
    topic_key = schedule.get(day_name, "General Tech")

    # Special case: Sunday is "Synthesis" — no specific topic
    if topic_key == "Synthesis":
        return {
            "key": "Synthesis",
            "full_name": "Weekly Synthesis",
            "subtopics": [],
            "is_synthesis_day": True,
        }

    topic_info = config["topics"].get(topic_key, {})
    return {
        "key": topic_key,
        "full_name": topic_info.get("full_name", topic_key),
        "subtopics": topic_info.get("subtopics", []),
        "is_synthesis_day": False,
    }


def get_commit_range(config=None):
    """Return (min_commits, max_commits) from config."""
    if config is None:
        config = load_config()
    commits = config.get("commits", {})
    return commits.get("min_per_day", 5), commits.get("max_per_day", 20)


def get_persona_prompt(config=None):
    """Return the persona system prompt."""
    if config is None:
        config = load_config()
    return config["persona"]["system_prompt"]


def get_all_topic_keys(config=None):
    """Return all topic keys (excluding Synthesis)."""
    if config is None:
        config = load_config()
    return list(config["topics"].keys())
