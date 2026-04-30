import os
import re
import json

def apply_template():
    # Use relative paths within the repo
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, "templates", "README_template.md")
    readme_path = os.path.join(base_dir, "README.md")
    ledger_path = os.path.join(base_dir, "ledger.md")
    briefing_path = os.path.join(base_dir, "DAILY_BRIEFING.md")
    sentiment_path = os.path.join(base_dir, "logs", "sentiment.json")
    
    if not os.path.exists(template_path):
        print(f"Template not found at {template_path}")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
        
    # Topic
    topic = "Emerging Tech"
    
    # Narrative
    narrative = "Synthesis in progress..."
    if os.path.exists(briefing_path):
        with open(briefing_path, "r", encoding="utf-8") as f:
            narrative = f.read()
    
    # Sentiment (Mood)
    mood = "Active"
    mood_detail = "Research ongoing."
    if os.path.exists(sentiment_path):
        try:
            with open(sentiment_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    latest = data[-1]
                    mood = latest.get("mood", "Active")
                    mood_detail = latest.get("brief_logic", "")
        except: pass
        
    # Data Art
    art_path = "./art/banner.png"
    art_desc = "CORTEX Interface"
    if os.path.exists(os.path.join(base_dir, "art")):
        files = [f for f in os.listdir(os.path.join(base_dir, "art")) if f.endswith(".png") and "banner" not in f]
        if files:
            files.sort(reverse=True)
            art_path = f"./art/{files[0]}"
            art_desc = f"Latest autonomous visualization"

    # Research Feed
    feed = "Initializing..."
    if os.path.exists(ledger_path):
        with open(ledger_path, "r", encoding="utf-8") as f:
            ledger_content = f.read()
        sections = re.split(r"---", ledger_content)
        feed_items = []
        for section in sections:
            headline_match = re.search(r"### (.*)", section)
            summary_match = re.search(r"> (.*)", section)
            if headline_match and summary_match:
                feed_items.append(f"- **{headline_match.group(1).strip()}**: {summary_match.group(1).strip()}")
            if len(feed_items) >= 5: break
        if feed_items: feed = "\n".join(feed_items)

    replacements = {
        "[[TODAYS_TOPIC]]": topic,
        "[[TECHNICAL_NARRATIVE]]": narrative,
        "[[SENTIMENT_MOOD]]": mood,
        "[[SENTIMENT_DETAIL]]": mood_detail,
        "[[DATA_ART_PATH]]": art_path,
        "[[DATA_ART_DESC]]": art_desc,
        "[[RESEARCH_FEED]]": feed
    }
    
    for k, v in replacements.items():
        template = template.replace(k, str(v))
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(template)
    
    print("Dashboard README refreshed.")

if __name__ == "__main__":
    apply_template()
