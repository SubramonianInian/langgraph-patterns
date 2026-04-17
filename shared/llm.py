import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

load_dotenv()

DEFAULT_MODEL = "anthropic:claude-sonnet-4-5"


def get_model(model: str | None = None, **kwargs) -> BaseChatModel:
    """Return a chat model, resolved from argument → env var → default.

    The prefix selects the provider (`anthropic:`, `openai:`, `azure_openai:`).
    Swap providers by changing `LLM_MODEL` in `.env`; no code changes needed.
    """
    model_id = model or os.getenv("LLM_MODEL", DEFAULT_MODEL)
    return init_chat_model(model_id, **kwargs)
