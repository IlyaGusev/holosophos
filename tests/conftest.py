import pytest
from codearkt.llm import LLM

from holosophos.settings import settings


settings.LIBRARIAN_TOOLS = ("arxiv_search", "arxiv_download")


@pytest.fixture
def deepseek() -> LLM:
    return LLM(model_name="deepseek/deepseek-chat-v3-0324", temperature=0.0)
