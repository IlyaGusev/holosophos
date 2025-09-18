from codearkt.llm import LLM
from codearkt.server import run_query
from academia_mcp.tools import arxiv_search, arxiv_download

from holosophos.main_agent import compose_main_agent


async def test_composition(deepseek: LLM) -> None:
    query = "Find abstract of the PingPong paper by Ilya Gusev"
    agent = compose_main_agent(
        model_name=deepseek._model_name, included_agents=("librarian",), tools=tuple()
    )
    answer = await run_query(
        query,
        agent,
        additional_tools={
            "arxiv_search": arxiv_search,
            "arxiv_download": arxiv_download,
        },
        add_mcp_server_prefixes=False,
    )
    assert "leverages different language models to simulate users" in str(answer)
