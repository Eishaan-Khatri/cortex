#!/usr/bin/env python3
"""
CORTEX — Daily Autocommit Orchestrator
Main entry point for the daily GitHub Action.

Generates 5-20 research-grounded commits per day, including:
- Research insights with ArXiv references
- Dialectic debates (Thesis/Antithesis/Synthesis)
- Code snippets
- Glossary updates
- SOTA tracking
- Data art
- Failure tracking
- Bounty hunting
"""

import os
import sys
import random
import time
from datetime import datetime

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from core.config import load_config, get_todays_topic, get_commit_range, get_persona_prompt
from core.ai_engine import GeminiEngine
from core.memory import Memory
from core.git_ops import commit_file, commit_files, commit_all, ensure_branch, switch_branch
from core.utils import (
    append_to_file, prepend_to_markdown, write_file, sanitize_commit_message, today_str, now_str,
)

from generators.daily_insights import generate_daily_insights
from generators.dialectic import generate_dialectic
from generators.code_snippets import generate_code_snippet
from generators.glossary import update_glossary
from generators.sota_tracker import update_sota
from generators.sentiment import generate_sentiment, format_sentiment_dashboard
from generators.arxiv_diver import deep_dive_paper
from generators.failures import check_for_failures
from generators.bounties import hunt_bounties
from generators.data_art import generate_data_art
from generators.eli5 import generate_eli5


LEDGER_FILE = "ledger.md"


def main():
    print("=" * 60)
    print(f"  CORTEX — Daily Research Pulse")
    print(f"  Date: {now_str()}")
    print("=" * 60)

    # Load configuration
    config = load_config()
    topic = get_todays_topic(config)
    min_commits, max_commits = get_commit_range(config)
    persona_prompt = get_persona_prompt(config)

    print(f"\n  📡 Today's Focus: {topic['full_name']} ({topic['key']})")

    # Skip if it's Synthesis day (handled by weekly.py)
    if topic.get("is_synthesis_day"):
        print("  ℹ️  Sunday is Synthesis day. Run weekly.py instead.")
        print("  Generating minimal daily commits for contribution graph...")
        _minimal_sunday_commits(config, persona_prompt)
        return

    # Initialize AI engine
    try:
        ai = GeminiEngine(
            model=config["ai"].get("model", "gemini-2.0-flash"),
            use_search=config["ai"].get("use_search_grounding", True),
            temperature=config["ai"].get("temperature", 0.9),
        )
    except ValueError as e:
        print(f"  ❌ {e}")
        print("  Falling back to template-based generation...")
        ai = None

    # Initialize memory
    memory = Memory(
        history_file=config["memory"].get("history_file", "logs/history.json"),
        no_repeat_days=config["memory"].get("no_repeat_days", 14),
    )

    # Check if already ran today
    if memory.was_topic_covered_today():
        print("  ⚠️  Already generated content for today. Skipping.")
        return

    avoidance_context = memory.get_avoidance_context()

    # Determine number of commits
    num_insights = random.randint(min_commits, max_commits)
    # Reserve slots for dialectic + code snippet + extras
    num_insights = max(3, num_insights - 4)

    all_keywords = []
    all_arxiv_ids = []
    all_commit_messages = []
    all_content_text = ""

    print(f"\n  Generating {num_insights} insights + dialectic + code + extras...\n")

    # ══════════════════════════════════════════════════
    # 1. DAILY INSIGHTS (main bulk of commits)
    # ══════════════════════════════════════════════════
    if ai:
        insights = generate_daily_insights(ai, topic, num_insights, avoidance_context, persona_prompt)
    else:
        from generators.daily_insights import _fallback_insights
        insights = _fallback_insights(topic, num_insights)

    for insight in insights:
        msg = sanitize_commit_message(insight.get("commit_message", f"[{topic['key']}] Research pulse"))
        expansion = insight.get("expansion", "")
        keywords = insight.get("keywords", [])
        arxiv_id = insight.get("arxiv_id")

        # Build ledger entry
        entry = f"- [{now_str()}] {msg}\n"
        if expansion:
            entry += f"  > {expansion}\n"
        if arxiv_id:
            entry += f"  > 📄 arXiv:{arxiv_id}\n"
        entry += "\n"

        prepend_to_markdown(LEDGER_FILE, entry)
        commit_file(LEDGER_FILE, msg)

        all_keywords.extend(keywords)
        if arxiv_id:
            all_arxiv_ids.append(arxiv_id)
        all_commit_messages.append(msg)
        all_content_text += f"{msg} {expansion} "

        # Small delay to make commits look natural
        time.sleep(0.5)

    # ══════════════════════════════════════════════════
    # 2. DIALECTIC DEBATE
    # ══════════════════════════════════════════════════
    if ai:
        print("\n  🗣️  Generating dialectic debate...")
        dialectic = generate_dialectic(ai, topic, avoidance_context, persona_prompt)

        debate_topic = dialectic.get("debate_topic", "")
        for phase in ["thesis", "antithesis", "synthesis"]:
            text = dialectic.get(phase, "")
            if text:
                # Ensure prefix exists
                prefix = f"[{phase.upper()}]"
                if not text.startswith(prefix):
                    text = f"{prefix} {text}"

                msg = sanitize_commit_message(text)
                entry = f"- [{now_str()}] {msg}\n"
                if phase == "thesis":
                    entry = f"\n### Dialectic: {debate_topic}\n\n" + entry

                prepend_to_markdown(LEDGER_FILE, entry)
                commit_file(LEDGER_FILE, msg)
                all_commit_messages.append(msg)
                all_content_text += f"{text} "
                time.sleep(0.5)

        all_keywords.extend(dialectic.get("keywords", []))

    # ══════════════════════════════════════════════════
    # 3. CODE SNIPPET
    # ══════════════════════════════════════════════════
    if ai:
        print("  💻 Generating code snippet...")
        snippet = generate_code_snippet(ai, topic, avoidance_context, persona_prompt)

        if snippet and snippet.get("code"):
            write_file(snippet["filename"], snippet["code"])
            msg = sanitize_commit_message(f"[CODE] {snippet.get('description', 'Code fragment')}")
            commit_file(snippet["filename"], msg)
            all_commit_messages.append(msg)
            all_keywords.extend(snippet.get("keywords", []))

    # ══════════════════════════════════════════════════
    # 4. ENHANCED KNOWLEDGE (Glossary + SOTA + Art)
    # Combined into fewer calls to respect free-tier limits
    # ══════════════════════════════════════════════════
    if ai and all_content_text:
        print("  📖 Updating glossary & SOTA...")
        new_terms = update_glossary(ai, all_content_text, persona_prompt)
        if new_terms:
            msg = sanitize_commit_message(f"[GLOSSARY] Added: {', '.join(new_terms[:3])}")
            commit_file("GLOSSARY.md", msg)
        
        update_sota(ai, all_content_text, topic, persona_prompt)
    
    print("  🎨 Generating data art...")
    art = generate_data_art(topic)
    if art:
        msg = sanitize_commit_message(f"[ART] {art['description']}")
        commit_file(art["filename"], msg)

    # ══════════════════════════════════════════════════
    # 6.5 ARXIV DEEP DIVE (New Feature)
    # ══════════════════════════════════════════════════
    if ai:
        print("  📄 Performing ArXiv Deep Dive...")
        paper_res = deep_dive_paper(ai, topic, persona_prompt)
        if paper_res:
            msg = sanitize_commit_message(f"[PAPER] Deep dive: {paper_res['title']}")
            commit_file(paper_res["filename"], msg)
            all_commit_messages.append(msg)
            all_keywords.extend(paper_res.get("keywords", []))

    # ══════════════════════════════════════════════════
    # 7. FAILURE CHECK
    # ══════════════════════════════════════════════════
    if ai:
        print("  ⚠️  Checking for failures & retractions...")
        failures = check_for_failures(ai, topic, persona_prompt)
        if failures:
            msg = sanitize_commit_message(f"[FAILURE] Logged {len(failures)} entries in {topic['key']}")
            commit_file("RETRACTIONS_AND_FAILURES.md", msg)
            all_commit_messages.append(msg)

    # ══════════════════════════════════════════════════
    # 8. BOUNTY HUNTING
    # ══════════════════════════════════════════════════
    if ai:
        print("  🎯 Hunting bounties...")
        claimed = hunt_bounties(ai, persona_prompt)
        if claimed:
            msg = sanitize_commit_message(f"[BOUNTY] 🏆 CLAIMED: {claimed[0].get('title', 'Unknown')}")
            commit_files(["BOUNTIES.md", "logs/bounties.json"], msg)
            all_commit_messages.append(msg)

    # ══════════════════════════════════════════════════
    # 9. SENTIMENT UPDATE
    # ══════════════════════════════════════════════════
    if ai:
        print("  📈 Updating field sentiment...")
        sentiment = generate_sentiment(ai, persona_prompt)
        if sentiment:
            # Update sentiment in logs
            msg = sanitize_commit_message(f"[PULSE] Field sentiment update — {topic['key']} day")
            commit_file("logs/sentiment.json", msg)
            all_commit_messages.append(msg)

    # ══════════════════════════════════════════════════
    # 10. ELI5 BRANCH
    # ══════════════════════════════════════════════════
    if ai and insights:
        print("  🧒 Generating ELI5 content...")
        eli5_content = generate_eli5(ai, insights, topic, persona_prompt)

        if eli5_content:
            # Save ELI5 content to a file on main branch (simpler than branch switching in CI)
            eli5_text = f"\n## {today_str()} — {topic['full_name']} (Simplified)\n\n"
            for item in eli5_content:
                eli5_text += f"- **Simple version:** {item.get('eli5', '')}\n"
                eli5_text += f"  - *Metaphor: {item.get('metaphor', '')}*\n\n"

            prepend_to_markdown("ELI5.md", eli5_text)
            msg = sanitize_commit_message(f"[ELI5] Simplified {topic['key']} insights for everyone")
            commit_file("ELI5.md", msg)
            all_commit_messages.append(msg)

    # ══════════════════════════════════════════════════
    # 11. UPDATE MEMORY
    # ══════════════════════════════════════════════════
    memory.add_entry(
        date=today_str(),
        topic=topic["key"],
        keywords=list(set(all_keywords)),
        arxiv_ids=list(set(all_arxiv_ids)),
        commit_messages=all_commit_messages,
    )

    # Commit memory update
    commit_file("logs/history.json", f"[MEMORY] Updated history — {topic['key']} day complete")

    print(f"\n{'=' * 60}")
    print(f"  ✅ Daily pulse complete: {len(all_commit_messages)} commits generated")
    print(f"  📡 Topic: {topic['full_name']}")
    print(f"  🔑 Keywords: {', '.join(list(set(all_keywords))[:10])}")
    print(f"  📄 Papers referenced: {len(all_arxiv_ids)}")
    print(f"{'=' * 60}")


def _minimal_sunday_commits(config, persona_prompt):
    """Generate a few minimal commits on Sunday to keep the graph green."""
    entry = f"- [{now_str()}] [SYNTHESIS] Preparing weekly synchronization...\n"
    prepend_to_markdown(LEDGER_FILE, entry)
    commit_file(LEDGER_FILE, "[SYNTHESIS] Weekly sync initiated")

    # Generate art for Sunday too
    topic = {"key": "Synthesis", "full_name": "Weekly Synthesis", "subtopics": []}
    art = generate_data_art(topic)
    if art:
        commit_file(art["filename"], f"[ART] Sunday reflection — {art['description']}")


if __name__ == "__main__":
    main()
