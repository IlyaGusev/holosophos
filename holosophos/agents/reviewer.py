import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent
from codearkt.prompt_storage import PromptStorage
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "reviewer"
DESCRIPTION = """This team member is a peer reviewer for top CS/ML venues (e.g., NeurIPS/ICML/ACL).
He has access to tools for reviewing papers.
Ask him when you need to review a paper.
He has it's own tools to access the paper.
Important note: Any tasks related to paper review should be delegated to the reviewer agent.
"""


def get_reviewer_agent(
    model: LLM,
    max_iterations: int,
    planning_interval: Optional[int],
    tools: Sequence[str],
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = PromptStorage.load(PROMPTS_DIR_PATH / "reviewer.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        tool_names=tools,
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        prompts=prompts,
        verbosity_level=verbosity_level,
    )
