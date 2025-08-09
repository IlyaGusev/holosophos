import logging
from typing import Optional

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "librarian"
DESCRIPTION = """This team member runs gets and analyzes information from papers.
He has access to ArXiv, Semantic Scholar, ACL Anthology, and web search.
Ask him any questions about papers and web articles.
Give him your full task as an argument. Follow the task format, include all the details."""


def get_librarian_agent(
    model: LLM,
    max_iterations: int = 21,
    planning_interval: Optional[int] = 5,
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "librarian.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        tool_names=[
            "academia_arxiv_download",
            "academia_arxiv_search",
            "academia_anthology_search",
            "academia_s2_citations",
            "academia_hf_datasets_search",
            "academia_document_qa",
            "exa_web_search_exa",
            "exa_crawling_exa",
        ],
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        prompts=prompts,
        verbosity_level=verbosity_level,
    )
