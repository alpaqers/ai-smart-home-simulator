from abc import ABC, abstractmethod
import json

from smart_home.server.ai.types import AIPrompt


class AITransport(ABC):
    @abstractmethod
    async def send(self, prompt: AIPrompt) -> dict[str, object]:
        ...

    async def aclose(self) -> None:
        return None


class HttpAITransport(AITransport):
    def __init__(
        self,
        endpoint: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        import httpx

        self._endpoint = endpoint
        self._client = httpx.AsyncClient(headers=headers or {}, timeout=timeout)

    async def send(self, prompt: AIPrompt) -> dict[str, object]:
        response = await self._client.post(
            self._endpoint,
            json={"messages": prompt.messages, **prompt.parameters},
        )
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()


class GeminiAITransport(AITransport):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gemini-3.5-flash",
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required")

        import httpx

        self._endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )
        self._client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            timeout=timeout,
        )

    async def send(self, prompt: AIPrompt) -> dict[str, object]:
        response = await self._client.post(
            self._endpoint,
            json=self._build_payload(prompt),
        )
        response.raise_for_status()
        return self._extract_json_response(response.json())

    async def aclose(self) -> None:
        await self._client.aclose()

    def _build_payload(self, prompt: AIPrompt) -> dict[str, object]:
        system_parts: list[dict[str, str]] = []
        user_parts: list[dict[str, str]] = []

        for message in prompt.messages:
            content = message.get("content", "")
            if not content:
                continue

            if message.get("role") == "system":
                system_parts.append({"text": content})
            else:
                user_parts.append({"text": content})

        payload: dict[str, object] = {
            "contents": [
                {
                    "parts": user_parts,
                }
            ],
            "generationConfig": {
                "responseFormat": {
                    "text": {
                        "mimeType": "application/json",
                    }
                }
            },
        }

        if system_parts:
            payload["system_instruction"] = {
                "parts": system_parts,
            }

        return payload

    def _extract_json_response(self, raw: dict[str, object]) -> dict[str, object]:
        try:
            candidates = raw["candidates"]
            if not isinstance(candidates, list) or not candidates:
                raise ValueError("Gemini response has no candidates")

            content = candidates[0]["content"]
            parts = content["parts"]
            if not isinstance(parts, list) or not parts:
                raise ValueError("Gemini response candidate has no parts")

            text = parts[0]["text"]
            if not isinstance(text, str):
                raise ValueError("Gemini response text is not a string")

            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise ValueError("Gemini JSON response must be an object")

            return parsed
        except (KeyError, TypeError) as exc:
            raise ValueError("Unexpected Gemini response format") from exc
