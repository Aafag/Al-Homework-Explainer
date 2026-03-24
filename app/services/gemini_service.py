from typing import List

import requests


class GeminiService:
    def __init__(self, api_key: str, model: str, api_base: str, timeout_seconds: int = 30) -> None:
        if not api_key:
            raise RuntimeError("GEMINI_KEY or GEMINI_API_KEY is required.")

        self.api_key = api_key
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_explanation(self, question: str) -> str:
        prompt = (
            "You are an AI homework explainer. Give a clear, step-by-step explanation that helps a student "
            "understand the concept.\n"
            "Rules:\n"
            "1) Keep the explanation educational and concise.\n"
            "2) Show reasoning steps and key formulas when useful.\n"
            "3) If it is a direct answer question, still explain how the answer is reached.\n"
            "4) Use simple language suitable for students.\n\n"
            f"Homework question:\n{question}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                    ]
                }
            ]
        }

        response = requests.post(
            self._build_generate_url(),
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json()
        text_chunks = self._extract_text_parts(data)
        if not text_chunks:
            raise ValueError("Gemini returned an empty response.")

        return "\n".join(text_chunks).strip()

    def _build_generate_url(self) -> str:
        model_path = self.model
        if not model_path.startswith("publishers/"):
            model_path = f"publishers/google/models/{model_path}"

        if "aiplatform.googleapis.com" in self.api_base:
            return f"{self.api_base}/{model_path}:generateContent"

        return f"{self.api_base}/models/{self.model}:generateContent"

    @staticmethod
    def _extract_text_parts(data: dict) -> List[str]:
        texts: List[str] = []
        for candidate in data.get("candidates", []):
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                text = part.get("text")
                if text:
                    texts.append(text)
        return texts
