import pytest

from smart_home.server.ai.transport import GeminiAITransport
from smart_home.server.ai.types import AIPrompt


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, object]:
        return self._payload


class FakeAsyncClient:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.requests: list[tuple[str, dict[str, object]]] = []
        self.response = FakeResponse(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"automations":[{"device_id":1,'
                                        '"parameters":{"power":"on"},'
                                        '"timestamp":200}]}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            }
        )
        self.closed = False

    async def post(self, endpoint: str, json: dict[str, object]) -> FakeResponse:
        self.requests.append((endpoint, json))
        return self.response

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_gemini_transport_sends_prompt_and_parses_json(monkeypatch) -> None:
    fake_client = FakeAsyncClient()

    class FakeHttpx:
        @staticmethod
        def AsyncClient(**kwargs: object) -> FakeAsyncClient:
            fake_client.kwargs = kwargs
            return fake_client

    monkeypatch.setitem(__import__("sys").modules, "httpx", FakeHttpx)
    transport = GeminiAITransport("test-key", model="gemini-test")

    response = await transport.send(
        AIPrompt(
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": "Suggest automations."},
            ]
        )
    )

    assert response == {
        "automations": [
            {
                "device_id": 1,
                "parameters": {"power": "on"},
                "timestamp": 200,
            }
        ]
    }
    assert fake_client.kwargs["headers"]["x-goog-api-key"] == "test-key"
    endpoint, payload = fake_client.requests[0]
    assert endpoint.endswith("/models/gemini-test:generateContent")
    assert payload["system_instruction"] == {
        "parts": [{"text": "Return JSON only."}]
    }
    assert payload["contents"] == [
        {
            "parts": [{"text": "Suggest automations."}],
        }
    ]

    await transport.aclose()
    assert fake_client.closed is True


def test_gemini_transport_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        GeminiAITransport("")
