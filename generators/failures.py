"""
CORTEX — Hall of Failures Tracker
Tracks retractions, failed reproductions, and debunked claims.
"""

from datetime import datetime
from core.utils import read_file, append_to_file


FAILURES_FILE = "RETRACTIONS_AND_FAILURES.md"

FAILURES_HEADER = """# ⚠️ Hall of Failures & Retractions

CORTEX maintains intellectual honesty by tracking when the research community
gets it wrong. Retractions, failed reproductions, and debunked claims are
documented here.

> *"Science progresses one funeral at a time."* — Max Planck

---

"""


def check_for_failures(ai_engine, topic, persona_prompt):
    """
    Ask the AI if there are any recent retractions or failures in today's field.

    Returns a list of failure entries.
    """

    prompt = f"""Check for any RECENT (last 30 days) notable failures, retractions,
or debunked claims in {topic['full_name']}. This includes:

1. Papers that were retracted or had significant errata
2. Benchmark results that failed to reproduce
3. Hyped technologies that underdelivered
4. Major claims that were publicly challenged

For each finding, provide:
1. "claim": The original claim that was made
2. "failure": What went wrong (1-2 sentences)
3. "source": Where this was reported
4. "severity": One of ["Retraction", "Failed Reproduction", "Overhyped", "Challenged"]

Respond with a JSON object: {{"failures": [...]}}
If nothing notable, return {{"failures": []}}
Be genuine — only report REAL failures, not hypothetical ones."""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if not result or not isinstance(result, dict):
        return []

    failures = result.get("failures", [])
    if not failures:
        return []

    # Initialize file if needed
    existing = read_file(FAILURES_FILE)
    if not existing.strip():
        from core.utils import write_file
        write_file(FAILURES_FILE, FAILURES_HEADER)

    # Append new failures
    date = datetime.now().strftime("%Y-%m-%d")
    for f in failures:
        claim = f.get("claim", "Unknown")
        failure = f.get("failure", "Details unavailable")
        source = f.get("source", "Unknown source")
        severity = f.get("severity", "Challenged")

        entry = f"### [{severity}] {claim}\n"
        entry += f"**Date Logged:** {date} | **Field:** {topic['full_name']}\n\n"
        entry += f"{failure}\n\n"
        entry += f"*Source: {source}*\n\n---\n\n"

        from core.utils import prepend_to_markdown
        prepend_to_markdown(FAILURES_FILE, entry)


    if failures:
        print(f"  [FAILURES] Logged {len(failures)} entries")

    return failures
