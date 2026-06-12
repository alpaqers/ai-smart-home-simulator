from abc import ABC, abstractmethod

import httpx

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
