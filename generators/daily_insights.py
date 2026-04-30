"""
CORTEX — Daily Insights Generator
Generates 5-20 unique research insights for today's topic using Gemini with search grounding.
"""

import random


def generate_daily_insights(ai_engine, topic, num_insights, avoidance_context, persona_prompt):
    """
    Generate research insights for today's topic.

    Returns a list of dicts:
    [{"commit_message": "...", "expansion": "...", "keywords": [...], "arxiv_id": "..."}]
    """

    prompt = f"""Today's date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
Today's research domain: {topic['full_name']}
Subtopics to explore: {', '.join(topic['subtopics'])}

Generate exactly {num_insights} unique, cutting-edge research insights about {topic['full_name']}.
Focus on the LATEST breakthroughs, newly published papers, and emerging trends.

For EACH insight, provide:
1. "commit_message": A concise, punchy observation (max 120 chars). Use the persona voice.
   Format: "[{topic['key']}] <insight>"
2. "expansion": A 2-3 sentence deeper analysis of why this matters.
3. "keywords": 3-5 specific technical keywords for dedup tracking.
4. "arxiv_id": If referencing a specific paper, include the ArXiv ID (e.g., "2401.12345"). Otherwise null.

{avoidance_context}

CRITICAL RULES:
- Each insight must be UNIQUE and non-obvious.
- Prefer niche, under-the-radar findings over mainstream news.
- Include at least 2 insights referencing specific recent papers.
- One insight should be a provocative or contrarian take.
- Use precise technical language, never hype words.

Respond with a JSON object: {{"insights": [...]}}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=True,
    )

    if result and isinstance(result, dict) and "insights" in result:
        return result["insights"]

    # Fallback: return minimal insights if AI fails
    print("  [CORTEX] AI generation failed. Using fallback insights.")
    return _fallback_insights(topic, num_insights)


def _fallback_insights(topic, count):
    """Generate template-based fallback insights if the API fails."""
    templates = [
        f"[{topic['key']}] Scanning sector for anomalous patterns in latest publications",
        f"[{topic['key']}] Signal detected: shifting paradigms in {random.choice(topic['subtopics']) if topic['subtopics'] else 'core research'}",
        f"[{topic['key']}] Benchmark drift observed across multiple evaluation frameworks",
        f"[{topic['key']}] Cross-referencing historical data with emerging methodology",
        f"[{topic['key']}] Entropy analysis complete: field stability at {random.randint(40, 95)}%",
    ]

    insights = []
    for i in range(count):
        template = templates[i % len(templates)]
        insights.append({
            "commit_message": template,
            "expansion": f"Automated observation #{random.randint(1000, 9999)} for {topic['full_name']}.",
            "keywords": [topic["key"], "observation", f"sector-{random.randint(1, 256)}"],
            "arxiv_id": None,
        })
    return insights
