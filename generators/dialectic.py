"""
CORTEX — Dialectic Engine
Generates deep Thesis → Antithesis → Synthesis debate structures.
"""

def generate_dialectic(ai_engine, topic, avoidance_context, persona_prompt):
    """
    Generate a dialectic debate on a current topic.
    """

    prompt = f"""Today's research domain: {topic['full_name']}
Subtopics: {', '.join(topic['subtopics'])}

Engage in deep dialectical analysis. Pick a genuinely debatable, CURRENT research
controversy in {topic['full_name']} and produce a structured debate.

Respond with a JSON object:
{{
    "debate_topic": "A technical, intriguing title for the debate.",
    "context": "Why is this debate happening right now? (2 sentences)",
    "thesis": "[THESIS] A detailed paragraph (3-4 sentences) arguing the dominant or emerging position.",
    "antithesis": "[ANTITHESIS] A detailed paragraph (3-4 sentences) presenting a rigorous critique or alternative.",
    "synthesis": "[SYNTHESIS] A high-level resolution (3-4 sentences) that reconciles the tension or identifies the necessary path forward.",
    "keywords": ["key1", "key2", "key3", "key4"]
}}

{avoidance_context}

RULES:
- Both sides must be intellectually honest and use specific technical arguments.
- The synthesis must be the "Alpha" perspective—the most advanced way to think about the problem.
- No buzzwords. Focus on architectural trade-offs, theoretical limits, or empirical data.

Respond in JSON mode."""

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
        "context": f"Current shifts in {topic['full_name']} are forcing a re-evaluation of core architectural assumptions.",
        "thesis": f"[THESIS] Current approaches in {topic['key']} are converging toward a unified framework based on global standardization.",
        "antithesis": f"[ANTITHESIS] Fragmentation is increasing as specialization deepens, making unified frameworks impractical for niche subdomains.",
        "synthesis": f"[SYNTHESIS] The path forward lies in 'Modular Interoperability'—standardized interfaces that allow for specialized diversity without complete fragmentation.",
        "keywords": [topic["key"], "debate", "methodology"],
    }
