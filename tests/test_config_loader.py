import os

from smart_home.common import config_loader


def test_load_dotenv_sets_missing_environment_values(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "GEMINI_API_KEY=from-file\n"
        "AI_PROVIDER=gemini\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_loader, "ENV_PATH", env_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("AI_PROVIDER", "already-set")

    config_loader.load_dotenv()

    assert os.environ["GEMINI_API_KEY"] == "from-file"
    assert os.environ["AI_PROVIDER"] == "already-set"
