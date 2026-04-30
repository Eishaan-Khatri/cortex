"""
CORTEX — Code Snippet Generator
Generates small, runnable Python code snippets related to today's research topic.
"""

import os
from datetime import datetime


def generate_code_snippet(ai_engine, topic, avoidance_context, persona_prompt):
    """
    Generate a runnable Python code snippet related to today's topic.

    Returns a dict:
    {"filename": "...", "code": "...", "description": "...", "keywords": [...]}
    """

    prompt = f"""Today's research domain: {topic['full_name']}
Subtopics: {', '.join(topic['subtopics'])}

Generate a SINGLE, self-contained Python code snippet that demonstrates a concept
from today's research domain. The code must:

1. Be runnable as-is (no external data files needed).
2. Be 20-60 lines of code.
3. Include a docstring explaining what it demonstrates.
4. Use only standard library + numpy/torch/matplotlib (common packages).
5. Demonstrate an actual technical concept, not just print statements.

Examples of good snippets:
- A minimal attention mechanism implementation
- A signal processing filter for EEG data
- A SHAP-like feature importance calculator
- A simple diffusion step visualization

Respond with a JSON object:
{{
    "description": "One-line description of what the snippet does",
    "code": "The full Python code as a string",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

{avoidance_context}"""

    result = ai_engine.generate(
        prompt=prompt,
        system_prompt=persona_prompt,
        json_mode=True,
        use_search=False,  # No search needed for code generation
    )

    if result and isinstance(result, dict) and "code" in result:
        date_str = datetime.now().strftime("%Y_%m_%d")
        topic_slug = topic["key"].lower().replace(" ", "_")
        filename = f"snippets/{date_str}_{topic_slug}.py"

        return {
            "filename": filename,
            "code": result["code"],
            "description": result.get("description", f"Code snippet for {topic['full_name']}"),
            "keywords": result.get("keywords", [topic["key"]]),
        }

    # Fallback: simple snippet
    return _fallback_snippet(topic)


def _fallback_snippet(topic):
    """Generate a simple fallback snippet."""
    date_str = datetime.now().strftime("%Y_%m_%d")
    topic_slug = topic["key"].lower().replace(" ", "_")

    code = f'''"""
CORTEX Code Fragment — {topic['full_name']}
Generated: {datetime.now().strftime('%Y-%m-%d')}

Demonstrates a basic concept in {topic['full_name']}.
"""

import random
import math

def signal_analysis(data_points=100):
    """Analyze synthetic signal data for pattern detection."""
    # Generate synthetic data
    signal = [math.sin(i * 0.1) + random.gauss(0, 0.1) for i in range(data_points)]

    # Compute running average
    window = 5
    smoothed = []
    for i in range(len(signal) - window):
        avg = sum(signal[i:i+window]) / window
        smoothed.append(avg)

    # Detect anomalies (values > 2 std from mean)
    mean = sum(smoothed) / len(smoothed)
    std = (sum((x - mean) ** 2 for x in smoothed) / len(smoothed)) ** 0.5
    anomalies = [i for i, x in enumerate(smoothed) if abs(x - mean) > 2 * std]

    print(f"Signal length: {{len(signal)}}")
    print(f"Anomalies detected: {{len(anomalies)}}")
    print(f"Signal stability: {{100 - len(anomalies)}}%")

    return smoothed, anomalies

if __name__ == "__main__":
    signal_analysis()
'''

    return {
        "filename": f"snippets/{date_str}_{topic_slug}.py",
        "code": code,
        "description": f"Signal analysis pattern for {topic['full_name']}",
        "keywords": [topic["key"], "signal", "analysis"],
    }
