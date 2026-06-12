from abc import ABC, abstractmethod

from smart_home.server.ai.transport import AITransport
from smart_home.server.ai.types import AIContext, AIPrompt, AIResponse
from smart_home.server.registry import DeviceRegistry
from smart_home.server.state_history import DeviceStateHistory


class BaseAIProcessor(ABC):
    def __init__(
        self,
        registry: DeviceRegistry,
        history: DeviceStateHistory,
        transport: AITransport,
    ) -> None:
        self._registry = registry
        self._history = history
        self._transport = transport

    @abstractmethod
    async def gather_context(self) -> AIContext:
        ...

    @abstractmethod
    def build_prompt(self, context: AIContext) -> AIPrompt:
        ...

    @abstractmethod
    def parse_response(self, raw: dict[str, object]) -> AIResponse:
        ...

    async def run(self) -> AIResponse:
        context = await self.gather_context()
        prompt = self.build_prompt(context)
        raw = await self._transport.send(prompt)
        return self.parse_response(raw)
