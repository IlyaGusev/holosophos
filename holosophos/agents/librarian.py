import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "librarian"
DESCRIPTION = """This team member runs, gets, and analyzes information from papers and websites.
He has access to ArXiv, Semantic Scholar, ACL Anthology, and web search.
Ask him any questions about papers and web articles.
Any questions about collecting and analyzing information should be delegated to this team member.
Give him your full task as an argument.
Librarian doesn't have access to the file system!
Follow the task format, and include all the details."""

DEFAULT_TOOLS = (
    "arxiv_download",
    "arxiv_search",
    "anthology_search",
    "s2_get_citations",
    "s2_get_references",
    "hf_datasets_search",
    "document_qa",
    "web_search",
    "visit_webpage",
    "text_editor",
)


def get_librarian_agent(
    model: LLM,
    max_iterations: int = 42,
    planning_interval: Optional[int] = 5,
    verbosity_level: int = logging.INFO,
    tools: Optional[Sequence[str]] = None,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "librarian.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        tool_names=tools or DEFAULT_TOOLS,
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        prompts=prompts,
        verbosity_level=verbosity_level,
    )
