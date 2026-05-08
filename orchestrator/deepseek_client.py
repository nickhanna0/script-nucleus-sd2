"""Simple DeepSeek API client wrapper with safe failure fallback.

This wrapper expects `DEEPSEEK_API_KEY` in environment. If absent or a
call fails, callers should handle the failure and optionally fall back
to local mock logic.
"""
import os
import requests
from typing import Optional, Dict, Any
try:
    from .config import DEEPSEEK_API_KEY, DEEPSEEK_DEFAULT_MODEL
except Exception:
    from config import DEEPSEEK_API_KEY, DEEPSEEK_DEFAULT_MODEL

API_BASE = "https://api.deepseek.ai/v1"


class DeepSeekClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.model = model or DEEPSEEK_DEFAULT_MODEL

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 512) -> Dict[str, Any]:
        """Call DeepSeek chat/completions endpoint and return text on success.

        Returns a dict: {"success": bool, "text": str, "raw": obj, "error": str}
        """
        if not self.available():
            return {"success": False, "text": "", "raw": None, "error": "No API key"}

        url = f"{API_BASE}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            # Try to extract text from common response shapes
            text = ""
            if isinstance(data, dict):
                # Chat-style: choices -> message/content
                choices = data.get("choices") or []
                if choices:
                    first = choices[0]
                    if isinstance(first.get("message"), dict):
                        text = first["message"].get("content", "")
                    else:
                        text = first.get("text", "")

            return {"success": True, "text": text, "raw": data, "error": None}
        except Exception as e:
            return {"success": False, "text": "", "raw": None, "error": str(e)}


def get_client() -> DeepSeekClient:
    return DeepSeekClient()
