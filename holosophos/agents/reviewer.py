import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "reviewer"
DESCRIPTION = """This team member is a peer reviewer for top CS/ML venues (e.g., NeurIPS/ICML/ACL).
He has access to tools for reviewing papers.
Ask him when you need to review a paper.
It has it's own tools to access the paper.
Important note: Any tasks related to paper review should be delegated to the reviewer agent.
Always review the generated papers.
"""

DEFAULT_TOOLS = (
    "academia_review_pdf_paper",
    "academia_download_pdf_paper",
    "academia_visit_webpage",
    "academia_web_search",
    "mle_kit_bash",
    "mle_kit_text_editor",
)


def get_reviewer_agent(
    model: LLM,
    max_iterations: int = 42,
    planning_interval: Optional[int] = None,
    verbosity_level: int = logging.INFO,
    tools: Optional[Sequence[str]] = None,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "reviewer.yaml")
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
