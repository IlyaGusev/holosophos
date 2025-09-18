import re
from typing import Optional

from codearkt.server import run_query
from codearkt.llm import LLM
from academia_mcp.tools import arxiv_search, arxiv_download, s2_get_citations

from holosophos.agents import get_librarian_agent


def extract_first_number(text: str) -> Optional[int]:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


async def test_librarian_case1(deepseek: LLM) -> None:
    query = "Which work introduces Point-E, a language-guided DM?"
    agent = get_librarian_agent(
        model=deepseek,
        tools=["arxiv_search", "arxiv_download"],
        max_iterations=40,
        planning_interval=5,
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
    assert "2212.08751" in str(answer)


async def test_librarian_case2(deepseek: LLM) -> None:
    query = "What paper was first to propose generating sign pose sequences from gloss sequences by employing VQVAE?"
    agent = get_librarian_agent(
        model=deepseek,
        tools=["arxiv_search", "arxiv_download"],
        max_iterations=40,
        planning_interval=5,
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
    assert "2208.09141" in str(answer)


async def test_librarian_case3(deepseek: LLM) -> None:
    query = (
        "How many citations does the transformers paper have according to Semantic Scholar? "
        "Return only one number as a string and nothing else."
    )
    agent = get_librarian_agent(
        model=deepseek,
        tools=["arxiv_search", "s2_get_citations"],
        max_iterations=40,
        planning_interval=5,
    )
    answer = await run_query(
        query,
        agent,
        additional_tools={
            "arxiv_search": arxiv_search,
            "s2_get_citations": s2_get_citations,
        },
        add_mcp_server_prefixes=False,
    )
    int_answer = extract_first_number(answer.strip())
    assert int_answer is not None
    assert int_answer > 100000
