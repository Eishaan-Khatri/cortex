"""
CORTEX — Shared Utilities
Date helpers, file I/O, and formatting functions.
"""

import os
import re
from datetime import datetime


def today_str():
    """Return today's date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def now_str():
    """Return current datetime as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def week_number():
    """Return current ISO week number."""
    return datetime.now().isocalendar()[1]


def year():
    """Return current year."""
    return datetime.now().year


def append_to_file(filepath, content):
    """Append content to a file, creating it if needed."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)


def prepend_to_markdown(filepath, content, marker="---"):
    """
    Insert content into a markdown file after the first occurrence of the marker.
    If marker not found, appends to the end.
    Ensures 'Latest at Top' (descending order).
    """
    if not os.path.exists(filepath):
        write_file(filepath, content)
        return

    old_content = read_file(filepath)
    if marker in old_content:
        parts = old_content.split(marker, 1)
        new_content = parts[0] + marker + "\n\n" + content + parts[1]
    else:
        new_content = old_content + "\n" + content

    write_file(filepath, new_content)



def read_file(filepath):
    """Read a file's contents, return empty string if not found."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_file(filepath, content):
    """Write content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def sanitize_commit_message(message):
    """Clean a commit message for git compatibility."""
    # Remove quotes that could break git commit -m
    message = message.replace('"', "'")
    # Remove newlines
    message = message.replace("\n", " ").replace("\r", "")
    # Truncate to reasonable length
    if len(message) > 200:
        message = message[:197] + "..."
    return message.strip()


def format_progress_bar(value, max_value=100, width=10):
    """Generate an ASCII progress bar."""
    filled = int((value / max_value) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def extract_keywords_from_text(text):
    """Extract potential keywords from generated text."""
    # Simple keyword extraction: words that appear to be technical terms
    words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*\b', text)
    # Also catch acronyms
    acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
    return list(set(words + acronyms))
