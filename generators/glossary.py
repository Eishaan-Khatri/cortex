"""
CORTEX — Glossary Builder
Automatically detects and defines complex technical terms.
"""

import os
from core.utils import read_file, write_file


GLOSSARY_FILE = "GLOSSARY.md"
GLOSSARY_HEADER = """# 🧬 CORTEX Glossary

A living dictionary of technical terms encountered during research.
Auto-generated and updated daily by CORTEX.

---

"""


def update_glossary(ai_engine, todays_content, persona_prompt):
    """
    Scan today's content for complex terms and add definitions to the glossary.

    Args:
        ai_engine: The Gemini engine instance.
        todays_content: All text generated today (insights + dialectic).
        persona_prompt: The persona system prompt.

    Returns:
        List of new terms added.
    """

    # Load existing glossary to avoid duplicates
    existing = read_file(GLOSSARY_FILE)
    existing_terms = _extract_existing_terms(existing)

    prompt = f"""Analyze the following research content and identify complex technical terms
that a computer science graduate student might not immediately know.

CONTENT:
{todays_content[:3000]}

ALREADY IN GLOSSARY (do NOT include these):
{', '.join(existing_terms[:50])}

For each NEW term found, provide:
1. "term": The exact term (e.g., "Sparse Autoencoders")
2. "definition": A concise, precise definition (1-2 sentences max)
3. "category": One of [NLP, CV, XAI, BCI, ML, Math, Systems]

Return a JSON object: {{"terms": [...]}}
If no new terms are found, return {{"terms": []}}
Limit to at most 5 new terms."""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=False,
    )

    if not result or not isinstance(result, dict) or "terms" not in result:
        return []

    new_terms = result["terms"]
    if not new_terms:
        return []

    # Append to glossary file
    if not os.path.exists(GLOSSARY_FILE) or not existing.strip():
        write_file(GLOSSARY_FILE, GLOSSARY_HEADER)

    with open(GLOSSARY_FILE, "a", encoding="utf-8") as f:
        for t in new_terms:
            term = t.get("term", "")
            definition = t.get("definition", "")
            category = t.get("category", "ML")
            if term and definition:
                f.write(f"### {term}\n")
                f.write(f"**Category:** {category}\n\n")
                f.write(f"{definition}\n\n---\n\n")

    added = [t["term"] for t in new_terms if t.get("term")]
    if added:
        print(f"  [GLOSSARY] Added {len(added)} terms: {', '.join(added)}")
    return added


def _extract_existing_terms(glossary_text):
    """Extract term names from existing glossary markdown."""
    terms = []
    for line in glossary_text.split("\n"):
        if line.startswith("### "):
            terms.append(line[4:].strip())
    return terms
