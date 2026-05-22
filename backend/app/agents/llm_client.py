import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.config import get_settings


@dataclass(frozen=True)
class LlmResult:
    text: str
    provider: str


class OptionalLlmClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._disabled = False

    @property
    def enabled(self) -> bool:
        return bool(self.settings.groq_api_key or self.settings.openai_api_key) and not self._disabled

    def complete(self, system_prompt: str, user_prompt: str) -> LlmResult | None:
        if not self.enabled:
            return None

        try:
            if self.settings.groq_api_key:
                return self._chat_completion(
                    provider="groq",
                    url="https://api.groq.com/openai/v1/chat/completions",
                    api_key=self.settings.groq_api_key,
                    model=self.settings.groq_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )

            if self.settings.openai_api_key:
                return self._chat_completion(
                    provider="openai",
                    url="https://api.openai.com/v1/chat/completions",
                    api_key=self.settings.openai_api_key,
                    model=self.settings.openai_model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
            self._disabled = True
            return None

        return None

    def _chat_completion(
        self,
        provider: str,
        url: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> LlmResult:
        payload = json.dumps(
            {
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request, timeout=18) as response:
            body = json.loads(response.read().decode("utf-8"))

        return LlmResult(
            text=body["choices"][0]["message"]["content"].strip(),
            provider=provider,
        )
