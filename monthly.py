#!/usr/bin/env python3
"""
CORTEX — Monthly Orchestrator
Runs on the 1st of every month.
Handles: predictions (new + scoring), bounty declarations.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from core.config import load_config, get_persona_prompt
from core.ai_engine import GeminiEngine
from core.git_ops import commit_file, commit_files
from core.utils import now_str

from generators.predictions import generate_predictions, score_predictions
from generators.bounties import declare_bounty
from generators.auditor import audit_predictions


def main():
    print("=" * 60)
    print(f"  CORTEX — Monthly Report")
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

    # ══════════════════════════════════════════════════
    # 1. SCORE OLD PREDICTIONS
    # ══════════════════════════════════════════════════
    print("\n  📊 Scoring due predictions...")
    scored = score_predictions(ai, persona_prompt)
    if scored:
        commit_files(
            ["PREDICTIONS.md", "logs/predictions.json"],
            f"[PREDICTIONS] Scored {len(scored)} predictions",
        )

    print("  🔬 Running Scientific Audit...")
    failures = audit_predictions(ai, persona_prompt)
    if failures > 0:
        print(f"  [AUDIT] Found {failures} flawed predictions. Failures logged.")
    else:
        print("  [AUDIT] No flawed predictions found or none ready for audit.")

    # ══════════════════════════════════════════════════
    # 2. GENERATE NEW PREDICTIONS
    # ══════════════════════════════════════════════════
    print("  🔮 Generating new predictions...")
    new_preds = generate_predictions(ai, persona_prompt)
    if new_preds:
        commit_files(
            ["PREDICTIONS.md", "logs/predictions.json"],
            f"[PREDICTIONS] Declared {len(new_preds)} new predictions",
        )

    # ══════════════════════════════════════════════════
    # 3. DECLARE NEW BOUNTY
    # ══════════════════════════════════════════════════
    print("  🎯 Declaring new bounty...")
    bounty = declare_bounty(ai, persona_prompt)
    if bounty:
        commit_files(
            ["BOUNTIES.md", "logs/bounties.json"],
            f"[BOUNTY] New bounty: {bounty.get('title', 'Unknown')}",
        )

    print(f"\n{'=' * 60}")
    print(f"  ✅ Monthly report complete")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
