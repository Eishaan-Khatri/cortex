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
    """Wrapper around the Gemini REST API."""

    def __init__(self, api_key=None, model=None, use_search=True, temperature=0.9):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or "gemini-2.0-flash"
        self.use_search = use_search
        self.temperature = temperature

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as an environment variable "
                "or pass it directly."
            )

    def generate(self, prompt, system_prompt=None, json_mode=False, use_search=None):
        """
        Generate content using Gemini.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system instruction.
            json_mode: If True, request JSON output.
            use_search: Override search grounding setting.

        Returns:
            The generated text (str), or parsed JSON (dict) if json_mode is True.
        """
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

        # Make request with retry
        for attempt in range(3):
            try:
                resp = requests.post(url, params=params, json=body, timeout=60)

                if resp.status_code == 429:
                    # Rate limited — wait and retry
                    wait_time = (attempt + 1) * 15
                    print(f"  [CORTEX] Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                resp.raise_for_status()
                data = resp.json()

                # Extract text from response
                text = self._extract_text(data)

                if json_mode:
                    return self._parse_json(text)

                return text

            except requests.exceptions.RequestException as e:
                print(f"  [CORTEX] API error (attempt {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(5)
                else:
                    raise

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
