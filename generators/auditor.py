"""
CORTEX — Self-Correction Auditor
Reviews past predictions and grades them against current reality.
Demonstrates scientific rigor by publicly admitting failures.
"""

import os
import json
from datetime import datetime
from core.utils import prepend_to_markdown

def load_predictions():
    filepath = "logs/predictions.json"
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_predictions(preds):
    with open("logs/predictions.json", "w", encoding="utf-8") as f:
        json.dump(preds, f, indent=2)

def audit_predictions(ai, persona_prompt):
    """Review pending predictions to see if they've come true."""
    predictions = load_predictions()
    if not predictions:
        return 0
        
    current_date = datetime.now()
    audits_completed = 0
    failures_logged = 0
    
    for pred in predictions:
        # Only audit pending predictions
        if pred.get("status") != "pending":
            continue
            
        # Parse the target date
        try:
            target_date = datetime.strptime(pred["timeframe"], "%Y-%m-%d")
        except ValueError:
            # If the format is weird, skip it
            continue
            
        # If we are within 30 days of the target date, or past it, audit it
        days_until = (target_date - current_date).days
        if days_until <= 30:
            print(f"  [AUDIT] Auditing prediction: {pred['title']}")
            
            prompt = f"""
            {persona_prompt}
            
            On {pred['date_made']}, you made the following prediction about the future of AI:
            
            **Prediction:** {pred['prediction']}
            **Target Date:** {pred['timeframe']}
            
            Today is {current_date.strftime('%Y-%m-%d')}.
            
            Use your search grounding to determine if this prediction came true, is currently coming true, or was completely wrong.
            
            Respond in JSON format:
            {{
                "status": "verified" | "failed",
                "reality_check": "A 2-sentence explanation of what actually happened based on current search results.",
                "reasoning_flaw": "If failed, explain why your original reasoning was flawed. If verified, explain why you were right."
            }}
            """
            
            # Use lower temperature for factual auditing
            original_temp = ai.temperature
            ai.temperature = 0.2
            result = ai.generate_json(prompt)
            ai.temperature = original_temp
            
            if not result:
                continue
                
            pred["status"] = result.get("status", "pending")
            pred["reality_check"] = result.get("reality_check", "")
            pred["audit_date"] = current_date.strftime("%Y-%m-%d")
            
            audits_completed += 1
            
            # If failed, log it to the hall of failures
            if pred["status"] == "failed":
                failures_logged += 1
                failure_entry = f"- **[AUDIT FAILURE] {pred['title']}**\n"
                failure_entry += f"  - **Predicted:** {pred['prediction']}\n"
                failure_entry += f"  - **Reality:** {result.get('reality_check', '')}\n"
                failure_entry += f"  - **Autopsy:** {result.get('reasoning_flaw', '')}\n\n"
                
                prepend_to_markdown("RETRACTIONS_AND_FAILURES.md", failure_entry, "---")
                print(f"  [AUDIT] ⚠️ Logged failure for: {pred['title']}")
            else:
                print(f"  [AUDIT] ✅ Verified prediction: {pred['title']}")

    if audits_completed > 0:
        save_predictions(predictions)
        
    return failures_logged
