#!/usr/bin/env python3
"""
CORTEX — Weekly Synthesis Orchestrator
Runs every Sunday to generate the weekly blog, paper deep dive, and podcast.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from core.config import load_config, get_persona_prompt
from core.ai_engine import GeminiEngine
from core.memory import Memory
from core.git_ops import commit_file, commit_files
from core.utils import now_str

from generators.weekly_synthesis import generate_weekly_synthesis
from generators.paper_deep_dive import generate_paper_deep_dive
from generators.cross_pollination import generate_cross_pollination
from generators.sentiment import generate_sentiment, format_sentiment_dashboard


def main():
    print("=" * 60)
    print(f"  CORTEX — Weekly Synthesis")
    print(f"  Date: {now_str()}")
    print("=" * 60)

    config = load_config()
    persona_prompt = get_persona_prompt(config)

    try:
        ai = GeminiEngine(
            model=config["ai"].get("model", "gemini-2.0-flash"),
            use_search=config["ai"].get("use_search_grounding", True),
            temperature=config["ai"].get("temperature", 0.9),
        )
    except ValueError as e:
        print(f"  ❌ {e}")
        return

    memory = Memory(
        history_file=config["memory"].get("history_file", "logs/history.json"),
        no_repeat_days=config["memory"].get("no_repeat_days", 14),
    )

    # ══════════════════════════════════════════════════
    # 1. WEEKLY SYNTHESIS BLOG
    # ══════════════════════════════════════════════════
    print("\n  📝 Generating weekly synthesis blog...")
    blog_file = generate_weekly_synthesis(ai, persona_prompt, memory)
    if blog_file:
        commit_file(blog_file, f"[WEEKLY] Published synthesis report")

    # ══════════════════════════════════════════════════
    # 2. PAPER DEEP DIVE
    # ══════════════════════════════════════════════════
    print("  📄 Generating paper deep dive...")
    paper_file = generate_paper_deep_dive(ai, persona_prompt, memory)
    if paper_file:
        commit_file(paper_file, f"[PAPER] Deep dive published")

    # ══════════════════════════════════════════════════
    # 3. CROSS-POLLINATION REPORT
    # ══════════════════════════════════════════════════
    print("  🔗 Generating cross-pollination report...")
    cross_result = generate_cross_pollination(ai, persona_prompt, memory)
    if cross_result:
        commit_file(cross_result["filename"], f"[CROSS] {cross_result['title']}")

    # ══════════════════════════════════════════════════
    # 4. SENTIMENT UPDATE
    # ══════════════════════════════════════════════════
    print("  📈 Generating weekly sentiment dashboard...")
    sentiment = generate_sentiment(ai, persona_prompt)

    # ══════════════════════════════════════════════════
    # 5. UPDATE README DASHBOARD
    # ══════════════════════════════════════════════════
    print("  🖥️  Updating README dashboard...")
    _update_readme(config, sentiment, memory)
    commit_files(["README.md", "logs/sentiment.json"], "[DASHBOARD] Weekly README refresh")

    # ══════════════════════════════════════════════════
    # 6. AUDIO PODCAST (gTTS)
    # ══════════════════════════════════════════════════
    if config.get("tts", {}).get("enabled", False):
        print("  🎙️  Generating audio podcast...")
        _generate_podcast(blog_file)

    print(f"\n{'=' * 60}")
    print(f"  ✅ Weekly synthesis complete")
    print(f"{'=' * 60}")


def _update_readme(config, sentiment, memory):
    """Regenerate the README.md with latest stats."""
    from core.utils import week_number, year, read_file
    from generators.sentiment import format_sentiment_dashboard

    wk = week_number()
    yr = year()

    # Count stats
    entries = memory.history.get("entries", [])
    total_commits = sum(len(e.get("commit_messages", [])) for e in entries)
    total_papers = sum(len(e.get("arxiv_ids", [])) for e in entries)
    days_active = len(entries)

    # Get today's topic
    from core.config import get_todays_topic
    today_topic = get_todays_topic(config)

    sentiment_block = format_sentiment_dashboard(sentiment) if sentiment else "```\nNo sentiment data yet.\n```"

    # Check for active bounties
    bounty_line = ""
    try:
        import json
        if os.path.exists("logs/bounties.json"):
            with open("logs/bounties.json", "r") as f:
                bounties = json.load(f)
            open_bounties = [b for b in bounties if b.get("status") == "open"]
            if open_bounties:
                bounty_line = f"🎯 **Active Bounty:** {open_bounties[-1].get('title', 'Unknown')}"
    except Exception:
        pass

    readme = f"""<div align="center">

# 🧠 CORTEX

**An autonomous AI research entity.**

*Curating daily insights across NLP, Computer Vision, Explainable AI, Brain-Computer Interfaces, and Emerging Technologies.*

![Days Active](https://img.shields.io/badge/Days_Active-{days_active}-blue?style=for-the-badge)
![Commits](https://img.shields.io/badge/Research_Commits-{total_commits}-green?style=for-the-badge)
![Papers](https://img.shields.io/badge/Papers_Referenced-{total_papers}-orange?style=for-the-badge)

---

### 📡 Current Focus: **{today_topic['full_name']}**

{bounty_line}

</div>

## Research Pulse

{sentiment_block}

## 📅 Weekly Schedule

| Day | Domain | Focus |
|:----|:-------|:------|
| Monday | 🗣️ NLP | Large Language Models, Tokenization, RAG |
| Tuesday | 👁️ CV | Diffusion Models, Video Synthesis, 3D Vision |
| Wednesday | 🔍 XAI | Interpretability, Fairness, Ethical AI |
| Thursday | 🧠 BCI | Neural Decoding, Brain-to-Text, Neuroprosthetics |
| Friday | 🚀 Emerging | Quantum ML, Neuromorphic, Robotics |
| Saturday | ⚙️ General | Open Source, DevTools, Industry Trends |
| Sunday | 📊 Synthesis | Weekly blog, Paper deep dive, Podcast |

## 📂 Repository Structure

| Directory | Contents |
|:----------|:---------|
| [`ledger.md`](./ledger.md) | Daily research log |
| [`blogs/`](./blogs/) | Weekly synthesis reports |
| [`papers/`](./papers/) | Paper deep dives with code |
| [`snippets/`](./snippets/) | Daily code fragments |
| [`art/`](./art/) | Generative data visualizations |
| [`audio/`](./audio/) | Weekly podcast episodes |
| [`GLOSSARY.md`](./GLOSSARY.md) | Auto-built technical glossary |
| [`SOTA.md`](./SOTA.md) | State-of-the-art tracker |
| [`PREDICTIONS.md`](./PREDICTIONS.md) | AI forecasting log |
| [`BOUNTIES.md`](./BOUNTIES.md) | Research bounty board |
| [`RETRACTIONS_AND_FAILURES.md`](./RETRACTIONS_AND_FAILURES.md) | Hall of Failures |
| [`ELI5.md`](./ELI5.md) | Simple explanations |

## 🔧 Fork & Customize

1. Fork this repository
2. Add your `GEMINI_API_KEY` to GitHub Secrets
3. Edit `config.yml` to set your research domains
4. The GitHub Action handles the rest

## How It Works

CORTEX uses **Gemini with Google Search grounding** to find and analyze the latest
research every day. Each insight is committed individually, creating a living,
version-controlled research journal.

<details>
<summary>Architecture</summary>

```
┌─────────────────────────────────────────────┐
│             GitHub Actions (Cron)            │
│  ┌────────┐  ┌────────┐  ┌───────────────┐  │
│  │ Daily  │  │Weekly  │  │   Monthly     │  │
│  │ 00:00  │  │Sunday  │  │   1st of Mo.  │  │
│  └───┬────┘  └───┬────┘  └──────┬────────┘  │
│      │           │              │            │
│      ▼           ▼              ▼            │
│  ┌─────────────────────────────────────────┐ │
│  │          CORTEX Core Engine             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────┐ │ │
│  │  │ AI Engine│  │  Memory  │  │Git Ops│ │ │
│  │  │ (Gemini) │  │ (14-day) │  │       │ │ │
│  │  └──────────┘  └──────────┘  └───────┘ │ │
│  └─────────────────────────────────────────┘ │
│      │                                       │
│      ▼                                       │
│  ┌─────────────────────────────────────────┐ │
│  │            Content Generators           │ │
│  │  Insights │ Dialectic │ Code │ Art     │ │
│  │  Glossary │ SOTA │ Sentiment │ ELI5   │ │
│  │  Predictions │ Bounties │ Failures    │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

</details>

---

*CORTEX is an experiment in autonomous AI research curation.
Built by [Eishaan Khatri](https://github.com/Eishaan-Khatri).*
"""

    from core.utils import write_file
    write_file("README.md", readme)


def _generate_podcast(blog_file):
    """Generate an audio podcast from the weekly blog using gTTS."""
    try:
        from gtts import gTTS
        from core.utils import read_file, week_number, year

        blog_text = read_file(blog_file)
        if not blog_text:
            print("  [TTS] No blog content to convert.")
            return

        # Strip markdown formatting for better TTS
        import re
        clean = re.sub(r'[#*`\[\]|>-]', '', blog_text)
        clean = re.sub(r'```.*?```', '', clean, flags=re.DOTALL)
        clean = clean[:5000]  # Limit length

        wk = week_number()
        yr = year()
        audio_file = f"audio/week_{wk:02d}_{yr}.mp3"

        os.makedirs("audio", exist_ok=True)
        tts = gTTS(text=clean, lang="en", slow=False)
        tts.save(audio_file)

        from core.git_ops import commit_file
        commit_file(audio_file, f"[PODCAST] Week {wk} audio synthesis")
        print(f"  [TTS] Generated: {audio_file}")

    except ImportError:
        print("  [TTS] gTTS not installed. Skipping podcast generation.")
    except Exception as e:
        print(f"  [TTS] Error generating podcast: {e}")


if __name__ == "__main__":
    main()
