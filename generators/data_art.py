"""
CORTEX — Data Art Generator
Creates matplotlib-based data visualizations and abstract generative art.
"""

import os
import random
import math
from datetime import datetime


def generate_data_art(topic):
    """
    Generate a data art visualization related to today's topic.
    Uses only matplotlib (no AI call needed — pure generative art).

    Returns: {"filename": "...", "description": "..."}
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend for CI
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
    except ImportError:
        print("  [ART] matplotlib not available. Skipping art generation.")
        return None

    date_str = datetime.now().strftime("%Y_%m_%d")
    filename = f"art/{date_str}_{topic['key'].lower().replace(' ', '_')}.png"

    # Pick a random art style
    style = random.choice(["lissajous", "spiral", "wave_interference", "neural_field"])

    fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")

    # Color palette based on topic
    palettes = {
        "NLP": ["#00d4aa", "#00b4d8", "#0077b6", "#023e8a"],
        "CV": ["#ff6b6b", "#ee5a24", "#f0932b", "#ffbe76"],
        "XAI": ["#a29bfe", "#6c5ce7", "#fd79a8", "#e84393"],
        "BCI": ["#00cec9", "#55efc4", "#81ecec", "#00b894"],
        "Emerging Tech": ["#fdcb6e", "#f39c12", "#e17055", "#d63031"],
        "General Tech": ["#74b9ff", "#0984e3", "#a29bfe", "#6c5ce7"],
    }
    colors = palettes.get(topic["key"], ["#74b9ff", "#0984e3", "#a29bfe"])

    if style == "lissajous":
        _draw_lissajous(ax, colors)
        description = "Lissajous attractor — harmonic convergence pattern"
    elif style == "spiral":
        _draw_spiral(ax, colors)
        description = "Fibonacci spiral — growth topology"
    elif style == "wave_interference":
        _draw_waves(ax, colors)
        description = "Wave interference — signal superposition"
    else:
        _draw_neural_field(ax, colors)
        description = "Neural field — activation topology"

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Add subtle title
    ax.text(
        0, -1.4, f"CORTEX // {topic['key']} // {datetime.now().strftime('%Y-%m-%d')}",
        color="#ffffff30", fontsize=8, ha="center", fontfamily="monospace",
    )

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close()

    print(f"  [ART] Generated: {description}")
    return {"filename": filename, "description": description}


def _draw_lissajous(ax, colors):
    a, b = random.randint(2, 7), random.randint(3, 8)
    delta = random.uniform(0, math.pi)
    t = [i * 0.01 for i in range(1000)]

    for j, offset in enumerate([0, 0.1, 0.2, 0.3]):
        x = [math.sin((a + offset) * ti + delta) for ti in t]
        y = [math.cos((b + offset) * ti) for ti in t]
        color = colors[j % len(colors)]
        ax.plot(x, y, color=color, alpha=0.6, linewidth=0.5)


def _draw_spiral(ax, colors):
    for j in range(4):
        theta = [i * 0.02 for i in range(500)]
        r = [0.01 * ti * (j + 1) * 0.3 for ti in range(500)]
        x = [r[i] * math.cos(theta[i] + j * math.pi / 2) for i in range(500)]
        y = [r[i] * math.sin(theta[i] + j * math.pi / 2) for i in range(500)]
        color = colors[j % len(colors)]
        ax.plot(x, y, color=color, alpha=0.7, linewidth=0.8)


def _draw_waves(ax, colors):
    for j in range(6):
        freq = random.uniform(2, 8)
        phase = random.uniform(0, 2 * math.pi)
        x = [i * 0.01 - 1.5 for i in range(300)]
        y = [0.3 * math.sin(freq * xi + phase) + (j - 3) * 0.3 for xi in x]
        color = colors[j % len(colors)]
        ax.plot(x, y, color=color, alpha=0.5, linewidth=1.0)


def _draw_neural_field(ax, colors):
    # Random points connected by lines — looks like a neural network
    n_points = 40
    points = [(random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2)) for _ in range(n_points)]

    # Draw connections
    for i in range(n_points):
        for j in range(i + 1, n_points):
            dist = math.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2)
            if dist < 0.6:
                color = random.choice(colors)
                ax.plot(
                    [points[i][0], points[j][0]],
                    [points[i][1], points[j][1]],
                    color=color, alpha=0.2, linewidth=0.5,
                )

    # Draw nodes
    for px, py in points:
        color = random.choice(colors)
        ax.plot(px, py, "o", color=color, markersize=3, alpha=0.8)
