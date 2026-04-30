#!/usr/bin/env python3
"""
CORTEX — Backfill Script
One-time script to generate 6 months of backdated commits.
Uses template-based generation to avoid excessive API calls.

WARNING: This will create ~180 days * 5-15 commits = 900-2700 backdated commits.
Run locally, not in GitHub Actions.
"""

import os
import sys
import random
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from core.config import load_config, get_todays_topic
from core.git_ops import commit_with_date
from core.utils import write_file, append_to_file


# Template-based thoughts for backfill (no API needed for historical data)
THOUGHT_TEMPLATES = {
    "NLP": [
        "[NLP] Observation: Token frequency distributions follow Zipf's law more closely in multilingual corpora",
        "[NLP] Analysis: Attention head specialization increases with model depth — heads 8-12 show syntactic patterns",
        "[NLP] Signal: Embedding space geometry shifts during fine-tuning — catastrophic forgetting detected at epoch {n}",
        "[NLP] Note: Perplexity scores plateau at {n}B parameters for standard benchmarks",
        "[NLP] Finding: In-context learning emerges at ~{n}M parameters with sufficient pretraining data diversity",
        "[NLP] Review: Tokenizer artifacts in low-resource languages cause {n}% performance degradation",
        "[NLP] Trend: Retrieval-augmented approaches reduce hallucination rate by approximately {n}%",
        "[NLP] Insight: Chain-of-thought prompting improves reasoning accuracy by {n}% on math benchmarks",
    ],
    "CV": [
        "[CV] Observation: Diffusion model sampling efficiency improves {n}x with progressive distillation",
        "[CV] Analysis: Vision transformer patch size inversely correlates with fine-grained recognition accuracy",
        "[CV] Signal: Neural radiance fields converge {n}% faster with hash encoding positional features",
        "[CV] Note: Data augmentation strategies plateau after {n} transformation types for ImageNet-scale tasks",
        "[CV] Finding: Self-supervised pretraining on video data yields stronger spatial representations",
        "[CV] Review: Medical imaging segmentation reaches {n}% Dice score with foundation model adapters",
        "[CV] Trend: Text-to-image alignment scores improve logarithmically with CLIP model scale",
        "[CV] Insight: Depth estimation from monocular images now rivals stereo methods at {n}m range",
    ],
    "XAI": [
        "[XAI] Observation: SHAP value computation scales quadratically — approximate methods needed beyond {n}K features",
        "[XAI] Analysis: Saliency maps disagree across methods for {n}% of adversarial examples",
        "[XAI] Signal: Mechanistic interpretability reveals polysemantic neurons in {n}% of transformer layers",
        "[XAI] Note: Concept-based explanations preferred by domain experts over pixel-level attribution",
        "[XAI] Finding: Explanation faithfulness metrics correlate weakly with human trust assessments",
        "[XAI] Review: EU AI Act compliance requires interpretability for {n}% of current production systems",
        "[XAI] Trend: Sparse autoencoders enable decomposition of model behavior into interpretable features",
        "[XAI] Insight: Counterfactual explanations are more actionable than attribution-based methods",
    ],
    "BCI": [
        "[BCI] Observation: Motor imagery classification accuracy reaches {n}% with subject-specific calibration",
        "[BCI] Analysis: EEG signal-to-noise ratio improves {n}dB with adaptive artifact rejection",
        "[BCI] Signal: Non-invasive BCI bandwidth limited to ~{n} bits/minute for spelling applications",
        "[BCI] Note: Transfer learning across BCI subjects reduces calibration time by {n}%",
        "[BCI] Finding: Neural spike sorting accuracy improves with contrastive learning approaches",
        "[BCI] Review: Brain-to-text systems achieve {n} words/minute in controlled settings",
        "[BCI] Trend: Dry electrode technology closing gap with wet electrodes — {n}% correlation",
        "[BCI] Insight: Neurofeedback training effects persist for {n} weeks post-intervention",
    ],
    "Emerging Tech": [
        "[EMERGING] Observation: Quantum advantage demonstrated for {n}-qubit optimization problems",
        "[EMERGING] Analysis: Neuromorphic chip energy efficiency exceeds GPU by {n}x for sparse workloads",
        "[EMERGING] Signal: Federated learning communication overhead reduced {n}% with gradient compression",
        "[EMERGING] Note: Bio-inspired computing architectures show promise for combinatorial optimization",
        "[EMERGING] Finding: Robotic manipulation dexterity improves {n}% with sim-to-real transfer",
        "[EMERGING] Review: AI-driven drug discovery pipeline reduces candidate screening time by {n}x",
        "[EMERGING] Trend: Edge AI inference latency drops below {n}ms for transformer models",
        "[EMERGING] Insight: Energy consumption of training runs doubles every {n} months",
    ],
    "General Tech": [
        "[TECH] Observation: Open-source model performance gap with proprietary systems narrows to {n}%",
        "[TECH] Analysis: Container orchestration overhead for ML workloads averages {n}% of total compute",
        "[TECH] Signal: Developer tool adoption shifts toward AI-assisted code generation",
        "[TECH] Note: Cloud GPU pricing decreases {n}% quarter-over-quarter across major providers",
        "[TECH] Finding: TypeScript adoption in ML tooling increases ecosystem interoperability",
        "[TECH] Review: Security vulnerabilities in ML pipelines average {n} per production deployment",
        "[TECH] Trend: MLOps maturity correlates with {n}x faster model deployment cycles",
        "[TECH] Insight: Rust-based ML frameworks show {n}% performance improvement over Python bindings",
    ],
}

DAY_TO_TOPIC = {
    0: "NLP",        # Monday
    1: "CV",         # Tuesday
    2: "XAI",        # Wednesday
    3: "BCI",        # Thursday
    4: "Emerging Tech",  # Friday
    5: "General Tech",   # Saturday
    6: "NLP",        # Sunday (use NLP as fallback)
}

LEDGER_FILE = "ledger.md"


def main():
    config = load_config()
    days_to_backfill = config.get("backfill", {}).get("days", 180)

    print(f"CORTEX BACKFILL — Generating {days_to_backfill} days of history")
    print("=" * 60)

    start_date = datetime.now() - timedelta(days=days_to_backfill)
    total_commits = 0

    for day_offset in range(days_to_backfill):
        date = start_date + timedelta(days=day_offset)
        weekday = date.weekday()
        topic_key = DAY_TO_TOPIC.get(weekday, "General Tech")

        templates = THOUGHT_TEMPLATES.get(topic_key, THOUGHT_TEMPLATES["General Tech"])
        num_commits = random.randint(5, 15)

        for i in range(num_commits):
            template = random.choice(templates)
            message = template.format(n=random.randint(2, 95))

            # Vary the hour for natural-looking timestamps
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)
            commit_date = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
            date_str = commit_date.strftime("%Y-%m-%dT%H:%M:%S")

            # Append to ledger
            entry = f"- [{commit_date.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
            append_to_file(LEDGER_FILE, entry)

            # Commit with backdated timestamp
            commit_with_date(LEDGER_FILE, message, date_str)
            total_commits += 1

        if day_offset % 30 == 0:
            print(f"  Day {day_offset}/{days_to_backfill} — {total_commits} commits so far")

    print(f"\n{'=' * 60}")
    print(f"  ✅ Backfill complete: {total_commits} commits over {days_to_backfill} days")
    print(f"  Run 'git push origin main' to push to GitHub")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
