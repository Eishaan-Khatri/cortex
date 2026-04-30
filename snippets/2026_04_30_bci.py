"""
CORTEX Code Fragment — Brain-Computer Interfaces
Generated: 2026-04-30

Demonstrates a basic concept in Brain-Computer Interfaces.
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

    print(f"Signal length: {len(signal)}")
    print(f"Anomalies detected: {len(anomalies)}")
    print(f"Signal stability: {100 - len(anomalies)}%")

    return smoothed, anomalies

if __name__ == "__main__":
    signal_analysis()
