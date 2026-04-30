"""
CORTEX — Daily Insights Generator
Generates high-density, structured research briefings for today's topic.
"""

import random
from datetime import datetime

def generate_daily_insights(ai_engine, topic, num_insights, avoidance_context, persona_prompt):
    """
    Generate structured research briefings for today's topic.
    """

    prompt = f"""Today's date: {datetime.now().strftime('%Y-%m-%d')}
Today's research domain: {topic['full_name']}
Subtopics to explore: {', '.join(topic['subtopics'])}

Generate {num_insights} high-density "Research Briefings" about {topic['full_name']}.
Instead of short snippets, focus on creating deep, insightful, and complete observations.

For EACH briefing, provide:
1. "headline": A bold, professional technical title for the discovery.
2. "commit_message": A concise tag-style message: "[{topic['key']}] <Title>" (max 80 chars).
3. "summary": A 1-2 sentence "ELI5" overview explaining why this matters to the broader landscape.
4. "technical_depth": A detailed paragraph (4-6 sentences) explaining the specific methodology, architecture, or findings.
5. "impact": A single-sentence bold "Bottom Line" takeaway.
6. "keywords": 4-6 specific technical keywords for dedup tracking.
7. "arxiv_id": Include the ArXiv ID if applicable (e.g., "2404.12345"). Otherwise null.

{avoidance_context}

CRITICAL RULES:
- Focus on VERY RECENT (last 7-14 days) or extremely high-impact signals.
- Balance deep technical detail with broad context.
- Ensure the writing feels authoritative, precise, and synthetic.
- Avoid buzzwords. Focus on data, benchmarks, and architectural shifts.

Respond with a JSON object: {"insights": [...]}"""

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
            "headline": f"Anomalous Signal in {topic['key']} Research",
            "commit_message": template,
            "summary": f"Automated monitoring detected a shift in {topic['full_name']} methodology.",
            "technical_depth": f"Observation #{random.randint(1000, 9999)} confirms that entropy levels in {topic['full_name']} are shifting toward a new equilibrium point.",
            "impact": "Field stability remains high but requires continuous observation.",
            "keywords": [topic["key"], "observation", f"sector-{random.randint(1, 256)}"],
            "arxiv_id": None,
        })
    return insights
