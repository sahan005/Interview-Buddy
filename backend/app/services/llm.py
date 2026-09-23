import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Search for .env in current directory, backend/.env, or parent
env_paths = [
    Path(".env"),
    Path("backend/.env"),
    Path(__file__).resolve().parent.parent.parent / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self._init_client()

    def _init_client(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Google GenAI Gemini client successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")
                self.client = None

    def is_available(self) -> bool:
        if not self.client:
            self._init_client()
        return bool(self.client and self.api_key)

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        """Call Gemini model with JSON response enforcement."""
        if not self.is_available():
            return None

        # Direct, working model for current Gemini SDK
        models_to_try = [
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
        ]

        from google.genai import types
        full_prompt = f"{system_instruction}\n\nTask:\n{prompt}\n\nRespond ONLY with a valid JSON object. Do not include markdown code block backticks."
        
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                    )
                )
                raw = response.text.strip()
                if raw.startswith("```"):
                    lines = raw.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    raw = "\n".join(lines).strip()
                parsed = json.loads(raw)
                return parsed
            except Exception as e:
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        return None

llm_service = GeminiService()
