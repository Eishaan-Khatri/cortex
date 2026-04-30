"""
CORTEX — Daily Briefing Generator
Generates a full technical narrative for the day's research.
"""

def generate_daily_briefing(ai_engine, topic, insights, dialectic, persona_prompt):
    """
    Synthesize all of today's findings into a single, high-fidelity technical narrative.
    """
    
    insights_summary = "\n".join([f"- {i['headline']}: {i['technical_depth']}" for i in insights])
    debate_summary = f"Dialectic: {dialectic['debate_topic']}\nContext: {dialectic['context']}\n{dialectic['thesis']}\n{dialectic['antithesis']}\n{dialectic['synthesis']}"

    prompt = f"""Today's research domain: {topic['full_name']}
Current Findings:
{insights_summary}

Current Debate:
{debate_summary}

Task: Write a "Daily Intelligence Narrative" (3-4 paragraphs) that synthesizes these findings into a coherent technical article.
Rules:
- DO NOT dilute the technical depth. Use precise terminology (e.g., mention specific architectures, loss functions, or hardware constraints if applicable).
- Explain the "WHY": Why does this specific set of findings matter for the field?
- The tone should be synthetic, authoritative, and sophisticated.
- Structure it as a "Dispatch from the Frontier."

Format the response as raw Markdown text.
"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        use_search=True,
    )
    
    return result if result else "Unable to synthesize narrative for today."
