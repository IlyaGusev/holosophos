from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    anthology_search_tool,
    arxiv_search_tool,
    arxiv_download_tool,
    hf_datasets_search_tool,
    s2_citations_tool,
    DocumentQATool,
    CustomVisitWebpageTool,
)

NAME = "librarian"
DESCRIPTION = """This team member runs gets and analyzes information from papers.
He has access to ArXiv, Semantic Scholar, ACL Anthology, and web search.
Ask him any questions about papers and web articles.
Give him your task as an argument. Follow the task format described above, include all the details."""


def get_librarian_agent(
    model: Model,
    max_steps: int = 21,
    planning_interval: Optional[int] = 5,
    max_print_outputs_length: int = 20000,
    verbosity_level: int = 2,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[
            DuckDuckGoSearchTool(),
            anthology_search_tool,
            arxiv_search_tool,
            arxiv_download_tool,
            s2_citations_tool,
            hf_datasets_search_tool,
            DocumentQATool(model),
            CustomVisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("librarian"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
        verbosity_level=verbosity_level,
    )
