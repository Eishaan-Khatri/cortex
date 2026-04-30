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

    # Get top 5 ledger entries for the live feed
    ledger_snippet = "No entries yet."
    if os.path.exists("ledger.md"):
        try:
            with open("ledger.md", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Find the marker and take next 5 non-empty lines
                marker_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() == "---":
                        marker_idx = i
                        break
                
                entries = []
                for line in lines[marker_idx+1:]:
                    line = line.strip()
                    if line and line.startswith("- ["):
                        entries.append(line)
                    if len(entries) >= 5:
                        break
                if entries:
                    ledger_snippet = "\n".join(entries)
        except Exception:
            pass

    readme = f"""<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,100:00ffcc&height=200&section=header&text=CORTEX&fontSize=80&fontColor=ffffff&animation=twinkling&fontAlignY=35&desc=Autonomous%20AI%20Research%20Entity&descAlignY=55&descSize=20" width="100%" />

<p align="center">
  <i>Curating the bleeding edge of Artificial Intelligence, completely autonomously.</i>
</p>

<p align="center">
  <a href="https://github.com/Eishaan-Khatri/cortex"><img src="https://img.shields.io/badge/Status-Autonomous-00ffcc?style=for-the-badge&logo=probot" alt="Status" /></a>
  <a href="./ledger.md"><img src="https://img.shields.io/badge/Days_Active-{days_active}-00a8ff?style=for-the-badge&logo=git" alt="Days Active" /></a>
  <a href="./ledger.md"><img src="https://img.shields.io/badge/Research_Commits-{total_commits}-ff9f43?style=for-the-badge&logo=github" alt="Commits" /></a>
  <a href="./papers"><img src="https://img.shields.io/badge/Papers_Referenced-{total_papers}-ff4757?style=for-the-badge&logo=arxiv" alt="Papers" /></a>
</p>

---

### 📡 Current Objective: **{today_topic['full_name']}**
{bounty_line}

</div>

## 🌐 Live Research Feed
> **CORTEX** continuously updates the [Ledger](./ledger.md) with daily research observations, dialectical debates, and state-of-the-art developments.

```markdown
{ledger_snippet}
```
*👉 [View the full cryptographic ledger](./ledger.md)*

## 📈 Field Pulse (Sentiment)
> Autonomous assessment of current AI research domains based on recent publications.

{sentiment_block}

## 🗓️ Weekly Execution Matrix
CORTEX follows a strict chronological execution path to ensure diverse intelligence gathering.

| Vector | Designation | Primary Focus Area |
|:---------|:------------|:----------------------|
| **`Monday`** | 🗣️ NLP | Large Language Models, Tokenization, RAG |
| **`Tuesday`** | 👁️ CV | Diffusion Models, Video Synthesis, 3D Vision |
| **`Wednesday`** | 🔍 XAI | Interpretability, Fairness, Ethical AI |
| **`Thursday`** | 🧠 BCI | Neural Decoding, Brain-to-Text, Neuroprosthetics |
| **`Friday`** | 🚀 Emerging | Quantum ML, Neuromorphic, Robotics |
| **`Saturday`** | ⚙️ Systems | Open Source, DevTools, Industry Trends |
| **`Sunday`** | 📊 Synthesis| Global synchronization, paper deep-dives, podcast |


## 🗄️ Core Databanks
Navigate CORTEX's autonomous memory structures.

| Databank | Description |
|:---------|:------------|
| 📖 **[`GLOSSARY.md`](./GLOSSARY.md)** | Auto-compiling dictionary of newly discovered technical terms |
| 🏆 **[`SOTA.md`](./SOTA.md)** | Dynamic State-of-the-Art benchmark tracker |
| 🔮 **[`PREDICTIONS.md`](./PREDICTIONS.md)** | Verifiable, time-locked forecasts on AI developments |
| 🎯 **[`BOUNTIES.md`](./BOUNTIES.md)** | Autonomous research bounties claimed by the agent |
| ⚠️ **[`RETRACTIONS_AND_FAILURES.md`](./RETRACTIONS_AND_FAILURES.md)** | Tracking dead-ends and withdrawn papers |
| 🧒 **[`ELI5.md`](./ELI5.md)** | Complex findings digested for non-technical observation |

## 🛠️ Replicate CORTEX
1. **Fork** this repository.
2. Inject your `GEMINI_API_KEY` into GitHub Secrets.
3. Configure target vectors in `config.yml`.
4. The GitHub Actions Chron-daemon will automate the rest.

<details>
<summary><b>View System Architecture</b></summary>

```text
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
│  │  │ Gemini 2 │  │  Memory  │  │Git Ops│ │ │
│  │  │ + Search │  │ (14-day) │  │       │ │ │
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
<div align="center">
<i>Engineered by <a href="https://github.com/Eishaan-Khatri">Eishaan Khatri</a>. Powered by Gemini.</i>
</div>
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
