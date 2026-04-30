"""
CORTEX — Dialectic Engine
Generates Thesis → Antithesis → Synthesis debate structures.
"""


def generate_dialectic(ai_engine, topic, avoidance_context, persona_prompt):
    """
    Generate a dialectic debate on a current topic.

    Returns a dict:
    {"topic": "...", "thesis": "...", "antithesis": "...", "synthesis": "...", "keywords": [...]}
    """

    prompt = f"""Today's research domain: {topic['full_name']}
Subtopics: {', '.join(topic['subtopics'])}

Engage in dialectical analysis. Pick a genuinely debatable, CURRENT research
question in {topic['full_name']} and produce:

1. "debate_topic": The core question being debated (1 sentence).
2. "thesis": A strong, well-argued position (1-2 sentences). Prefix with [THESIS].
3. "antithesis": A convincing counter-argument (1-2 sentences). Prefix with [ANTITHESIS].
4. "synthesis": A nuanced resolution that acknowledges both sides (1-2 sentences). Prefix with [SYNTHESIS].
5. "keywords": 3-5 technical keywords.

{avoidance_context}

RULES:
- The debate must be about a REAL, current controversy in the field.
- Both thesis and antithesis must be intellectually honest — no strawmen.
- The synthesis should propose a novel perspective, not just "both are right."

Respond with a JSON object matching the structure above."""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if result and isinstance(result, dict):
        return result

    # Fallback
    return {
        "debate_topic": f"The trajectory of {topic['full_name']}",
        "thesis": f"[THESIS] Current approaches in {topic['key']} are converging toward a unified framework.",
        "antithesis": f"[ANTITHESIS] Fragmentation is increasing as specialization deepens.",
        "synthesis": f"[SYNTHESIS] The field needs standardized interfaces between specialized modules.",
        "keywords": [topic["key"], "debate", "methodology"],
    }
