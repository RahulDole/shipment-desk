import os

from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """Return an LLM client when an API key is configured.

    The project is designed to work even when no key is configured, so the
    pipeline falls back to deterministic rule-based handling in that case.
    """
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        base_url = None
        if os.getenv("GROQ_API_KEY"):
            base_url = "https://api.groq.com/openai/v1"

        model_name = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
        return ChatOpenAI(
            model=model_name,
            api_key=SecretStr(api_key),
            base_url=base_url,
            temperature=0,
        )
    except Exception:
        return None
