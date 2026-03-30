from typing import List

import requests


class GeminiService:
    def __init__(
        self,
        api_key: str,
        model: str,
        api_base: str,
        auth_mode: str = "auto",
        vertex_access_token: str = "",
        vertex_project_id: str = "",
        vertex_location: str = "us-central1",
        vertex_use_project_endpoint: bool = False,
        timeout_seconds: int = 30,
    ) -> None:
        self.auth_mode = (auth_mode or "auto").lower()
        if self.auth_mode not in {"auto", "api_key", "oauth"}:
            raise RuntimeError("GEMINI_AUTH_MODE must be one of: auto, api_key, oauth.")
        if self.auth_mode == "api_key" and not api_key:
            raise RuntimeError("GEMINI_KEY or GEMINI_API_KEY is required in api_key mode.")

        self.api_key = api_key
        self.model = model
        self.api_base = api_base.rstrip("/")
        self.vertex_access_token = (vertex_access_token or "").strip()
        self.vertex_project_id = (vertex_project_id or "").strip()
        self.vertex_location = (vertex_location or "us-central1").strip()
        self.vertex_use_project_endpoint = vertex_use_project_endpoint
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

        response = self._make_request(payload)

        data = response.json()
        text_chunks = self._extract_text_parts(data)
        if not text_chunks:
            raise ValueError("Gemini returned an empty response.")

        return "\n".join(text_chunks).strip()

    def _make_request(self, payload: dict) -> requests.Response:
        if self.auth_mode == "api_key":
            return self._request_with_api_key(payload)

        if self.auth_mode == "oauth":
            return self._request_with_oauth(payload)

        if self.api_key:
            try:
                return self._request_with_api_key(payload)
            except requests.HTTPError as exc:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                # Auto mode falls back only when API key auth is rejected.
                if status_code != 401:
                    raise

        if self._has_oauth_config():
            return self._request_with_oauth(payload)

        if not self.api_key:
            raise ValueError(
                "No Gemini credentials configured. Set GEMINI_KEY/GEMINI_API_KEY or OAuth credentials."
            )

        raise ValueError(
            "Gemini API key authentication failed and OAuth fallback is not configured."
        )

    def _request_with_api_key(self, payload: dict) -> requests.Response:
        if not self.api_key:
            raise ValueError("GEMINI_KEY or GEMINI_API_KEY is required for API key auth.")

        response = requests.post(
            self._build_generate_url(),
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response

    def _request_with_oauth(self, payload: dict) -> requests.Response:
        access_token = self._get_oauth_access_token()
        response = requests.post(
            self._build_generate_url(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response

    def _has_oauth_config(self) -> bool:
        return bool(self.vertex_access_token) or bool(self.vertex_project_id) or self.auth_mode == "oauth"

    def _get_oauth_access_token(self) -> str:
        if self.vertex_access_token:
            return self.vertex_access_token

        try:
            import google.auth
            from google.auth.transport.requests import Request as GoogleAuthRequest
        except ImportError as exc:
            raise ValueError(
                "OAuth mode requires google-auth. Install dependencies from requirements.txt."
            ) from exc

        try:
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            credentials.refresh(GoogleAuthRequest())
        except Exception as exc:
            raise ValueError(
                "Could not obtain OAuth access token. Set VERTEX_ACCESS_TOKEN or configure "
                "GOOGLE_APPLICATION_CREDENTIALS/ADC."
            ) from exc

        access_token = getattr(credentials, "token", None)
        if not access_token:
            raise ValueError("OAuth token retrieval succeeded but token is empty.")

        return access_token

    def _build_generate_url(self) -> str:
        model_path = self.model
        if not model_path.startswith("publishers/"):
            model_path = f"publishers/google/models/{model_path}"

        if self.vertex_use_project_endpoint:
            if not self.vertex_project_id:
                raise ValueError(
                    "VERTEX_PROJECT_ID (or GOOGLE_CLOUD_PROJECT) is required when "
                    "VERTEX_USE_PROJECT_ENDPOINT=1."
                )
            location = self.vertex_location
            return (
                f"https://{location}-aiplatform.googleapis.com/v1/projects/{self.vertex_project_id}"
                f"/locations/{location}/{model_path}:generateContent"
            )

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
