"""
CORTEX — ELI5 Generator
Generates simple explanations for complex insights.
Commits to the 'eli5' branch.
"""


def generate_eli5(ai_engine, insights, topic, persona_prompt):
    """
    Generate ELI5 (Explain Like I'm 5) versions of today's insights.

    Args:
        insights: List of complex insight dicts from daily_insights.
        topic: Today's topic dict.

    Returns:
        List of simplified insight strings.
    """

    # Take the top 3 most complex insights
    complex_texts = [i.get("expansion", i.get("commit_message", "")) for i in insights[:3]]
    complex_block = "\n".join(f"- {t}" for t in complex_texts)

    prompt = f"""Take these complex AI research insights and rewrite each one in
extremely simple language that a non-technical person could understand.
Use metaphors, analogies, and everyday comparisons.

COMPLEX INSIGHTS:
{complex_block}

For each insight, provide:
1. "original": The first few words of the original (for matching)
2. "eli5": The simplified version (2-3 sentences, using analogies)
3. "metaphor": The core metaphor used

Respond as JSON: {{"explanations": [...]}}

RULES:
- No jargon whatsoever
- Use comparisons to cooking, sports, building, or nature
- Make it genuinely understandable by a 10-year-old"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt="You are a friendly science communicator who makes complex topics simple and fun.",
        json_mode=True,
        use_search=False,
    )

    if result and isinstance(result, dict) and "explanations" in result:
        return result["explanations"]

    # Fallback
    return [
        {
            "original": complex_texts[0][:30] if complex_texts else "",
            "eli5": f"Think of {topic['full_name']} like building with LEGO blocks — each piece connects to make something bigger.",
            "metaphor": "LEGO blocks",
        }
    ]
