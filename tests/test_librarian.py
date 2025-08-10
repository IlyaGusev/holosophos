import re
import logging
from typing import Optional

from codearkt.server import run_query
from codearkt.llm import LLM
from academia_mcp.tools import arxiv_search, arxiv_download, s2_citations

from holosophos.agents import get_librarian_agent


def extract_first_number(text: str) -> Optional[int]:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


async def test_librarian_case1() -> None:
    query = "Which work introduces Point-E, a language-guided DM?"
    model = LLM(model_name="deepseek/deepseek-chat-v3-0324", temperature=0.0)
    agent = get_librarian_agent(model=model, tools=["arxiv_search", "arxiv_download"])
    answer = await run_query(query, agent, additional_tools=[arxiv_search, arxiv_download])
    assert "2212.08751" in str(answer)


async def test_librarian_case2() -> None:
    query = "What paper was first to propose generating sign pose sequences from gloss sequences by employing VQVAE?"
    model = LLM(model_name="deepseek/deepseek-chat-v3-0324", temperature=0.0)
    agent = get_librarian_agent(
        model=model, tools=["arxiv_search", "arxiv_download"], verbosity_level=logging.DEBUG
    )
    answer = await run_query(query, agent, additional_tools=[arxiv_search, arxiv_download])
    assert "2208.09141" in str(answer)


async def test_librarian_case3() -> None:
    query = (
        "How many citations does the transformers paper have according to Semantic Scholar? "
        "Return only one number as a string and nothing else."
    )
    model = LLM(model_name="deepseek/deepseek-chat-v3-0324", temperature=0.0)
    agent = get_librarian_agent(model=model, tools=["arxiv_search", "s2_citations"])
    answer = await run_query(query, agent, additional_tools=[arxiv_search, s2_citations])
    int_answer = extract_first_number(answer.strip())
    assert int_answer is not None
    assert int_answer > 100000
