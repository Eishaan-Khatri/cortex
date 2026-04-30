"""
CORTEX — Gemini AI Engine
Handles all interactions with the Gemini API, including search-grounded generation.
Uses the REST API directly to minimize dependencies.
"""

import os
import json
import time
import requests


GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiEngine:
    """Wrapper around the Gemini REST API with rate-limit handling."""

    def __init__(self, api_key=None, model=None, use_search=True, temperature=0.9):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or "gemini-2.0-flash"
        self.use_search = use_search
        self.temperature = temperature
        self.last_request_time = 0
        self.min_interval = 30  # Mandatory 30s gap between calls for free-tier

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as an environment variable "
                "or pass it directly."
            )

    def generate(self, prompt, system_prompt=None, json_mode=False, use_search=None):
        """
        Generate content using Gemini with rate-limit safety.
        """
        # ══════════════════════════════════════════════════
        # 1. RATE LIMIT COOLDOWN
        # ══════════════════════════════════════════════════
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait = self.min_interval - elapsed
            print(f"  [CORTEX] Pacing request (cooldown)... {wait:.1f}s")
            time.sleep(wait)

        url = f"{GEMINI_API_BASE}/models/{self.model}:generateContent"
        params = {"key": self.api_key}

        # Build request body
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 8192,
            },
        }

        # System instruction
        if system_prompt:
            body["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        # JSON mode
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        # Search grounding
        search_enabled = use_search if use_search is not None else self.use_search
        if search_enabled:
            body["tools"] = [{"googleSearch": {}}]

        # ══════════════════════════════════════════════════
        # 2. REQUEST WITH RETRY
        # ══════════════════════════════════════════════════
        for attempt in range(5):  # Increased retries
            try:
                self.last_request_time = time.time()
                resp = requests.post(url, params=params, json=body, timeout=90)

                if resp.status_code == 429:
                    # Exponential backoff on rate limit
                    wait_time = (attempt + 1) * 30
                    print(f"  [CORTEX] 429 Rate Limited. Waiting {wait_time}s (attempt {attempt+1}/5)...")
                    time.sleep(wait_time)
                    continue

                if resp.status_code != 200:
                    print(f"  [CORTEX] API Error {resp.status_code}: {resp.text[:200]}")
                    time.sleep(10)
                    continue

                data = resp.json()

                # Extract text from response
                text = self._extract_text(data)

                if json_mode:
                    return self._parse_json(text)

                return text

            except requests.exceptions.RequestException as e:
                print(f"  [CORTEX] Connection error (attempt {attempt + 1}/5): {e}")
                time.sleep(15)

        return None

    def _extract_text(self, response_data):
        """Extract text from Gemini API response."""
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            # Concatenate all text parts
            text_parts = [p["text"] for p in parts if "text" in p]
            return "\n".join(text_parts)
        except (KeyError, IndexError, TypeError):
            return ""

    def _parse_json(self, text):
        """Parse JSON from text, handling markdown code blocks."""
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass
            # Try array
            start = cleaned.find("[")
            end = cleaned.rfind("]") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass
            print(f"  [CORTEX] Failed to parse JSON. Raw text: {text[:200]}")
            return None
