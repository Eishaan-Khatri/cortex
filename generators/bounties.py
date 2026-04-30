"""
CORTEX — Agentic Bounty System
Declares research bounties and hunts for them daily.
"""

import os
import json
from datetime import datetime
from core.utils import write_file


BOUNTIES_JSON = "logs/bounties.json"
BOUNTIES_MD = "BOUNTIES.md"

BOUNTIES_HEADER = """# 🎯 CORTEX Bounty Board

CORTEX sets itself research challenges and hunts for answers.
When a bounty is claimed, the full analysis is published.

---

"""


def declare_bounty(ai_engine, persona_prompt):
    """Declare a new research bounty for the month."""

    prompt = """Declare a specific, measurable research bounty — a question that CORTEX
will actively hunt for over the coming month.

The bounty should be:
- Specific enough to have a clear "claimed" condition
- Ambitious but realistically findable
- Related to cutting-edge AI research
- Interesting to researchers and engineers

Provide a JSON object:
{
    "title": "Short bounty title",
    "description": "What we're looking for (2-3 sentences)",
    "claim_criteria": "Specific conditions for claiming this bounty",
    "domain": "NLP/CV/BCI/XAI/Cross-field",
    "difficulty": "Easy/Medium/Hard/Legendary"
}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if not result or not isinstance(result, dict):
        return None

    bounty = result
    bounty["id"] = f"B-{datetime.now().strftime('%Y-%m')}-{_next_id()}"
    bounty["created"] = datetime.now().strftime("%Y-%m-%d")
    bounty["status"] = "open"
    bounty["claim_date"] = None
    bounty["claim_analysis"] = None

    all_bounties = _load_bounties()
    all_bounties.append(bounty)
    _save_bounties(all_bounties)
    _regenerate_bounties_md(all_bounties)

    print(f"  [BOUNTY] Declared: {bounty.get('title', 'Unknown')}")
    return bounty


def hunt_bounties(ai_engine, persona_prompt):
    """Check if any open bounties can be claimed based on new research."""

    all_bounties = _load_bounties()
    open_bounties = [b for b in all_bounties if b.get("status") == "open"]

    if not open_bounties:
        print("  [BOUNTY] No open bounties to hunt")
        return []

    bounty_text = "\n".join(
        f"- [{b.get('id')}] {b.get('title')}: {b.get('claim_criteria')}"
        for b in open_bounties
    )

    prompt = f"""Check if any of these research bounties can be CLAIMED based on
recently published research or developments.

OPEN BOUNTIES:
{bounty_text}

For each bounty, determine if there is NOW a paper, project, or development
that meets the claim criteria.

Respond with JSON:
{{
    "results": [
        {{
            "id": "bounty-id",
            "claimable": true/false,
            "evidence": "If claimable: the specific paper/project that claims it (2-3 sentences)",
            "source": "ArXiv ID or URL"
        }}
    ]
}}

Only mark as claimable if there is STRONG, specific evidence."""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if not result or not isinstance(result, dict):
        return []

    claimed = []
    results = result.get("results", [])

    for r in results:
        if r.get("claimable"):
            # Find and update the bounty
            for b in all_bounties:
                if b.get("id") == r.get("id"):
                    b["status"] = "claimed"
                    b["claim_date"] = datetime.now().strftime("%Y-%m-%d")
                    b["claim_analysis"] = r.get("evidence", "")
                    b["claim_source"] = r.get("source", "")
                    claimed.append(b)
                    print(f"  [BOUNTY] 🏆 CLAIMED: {b.get('title')}")

    if claimed:
        _save_bounties(all_bounties)
        _regenerate_bounties_md(all_bounties)

    return claimed


def _next_id():
    bounties = _load_bounties()
    return f"{len(bounties) + 1:03d}"


def _load_bounties():
    if os.path.exists(BOUNTIES_JSON):
        try:
            with open(BOUNTIES_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def _save_bounties(data):
    os.makedirs(os.path.dirname(BOUNTIES_JSON), exist_ok=True)
    with open(BOUNTIES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _regenerate_bounties_md(all_bounties):
    """Regenerate BOUNTIES.md."""
    content = BOUNTIES_HEADER

    # Sort by ID descending (latest at top)
    all_bounties.sort(key=lambda x: x.get("id", ""), reverse=True)

    open_b = [b for b in all_bounties if b.get("status") == "open"]
    claimed_b = [b for b in all_bounties if b.get("status") == "claimed"]


    if open_b:
        content += "## 🔓 Open Bounties\n\n"
        for b in open_b:
            content += f"### {b.get('title', 'Untitled')}\n"
            content += f"**ID:** {b.get('id')} | **Difficulty:** {b.get('difficulty', '?')} | **Domain:** {b.get('domain', '?')}\n\n"
            content += f"{b.get('description', '')}\n\n"
            content += f"**Claim Criteria:** {b.get('claim_criteria', '')}\n\n---\n\n"

    if claimed_b:
        content += "## 🏆 Claimed Bounties\n\n"
        for b in claimed_b:
            content += f"### ✅ {b.get('title', 'Untitled')}\n"
            content += f"**Claimed:** {b.get('claim_date', '?')}\n\n"
            content += f"{b.get('claim_analysis', '')}\n\n"
            if b.get("claim_source"):
                content += f"*Source: {b['claim_source']}*\n\n"
            content += "---\n\n"

    write_file(BOUNTIES_MD, content)
