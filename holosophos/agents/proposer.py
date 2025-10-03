import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent
from codearkt.prompt_storage import PromptStorage
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "proposer"
DESCRIPTION = """This team member generates creative ideas for research experiments.
He analyzes existing ideas and proposes new research directions, assessing their interestingness, feasibility, and novelty.
Ask him when you need to come up with new research proposals.
He can read files from the working directory.
Provide a detailed task description and context as an argument, as well as the arxiv_id of the baseline paper."""


def get_proposer_agent(
    model: LLM,
    max_iterations: int,
    planning_interval: Optional[int],
    tools: Sequence[str],
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = PromptStorage.load(PROMPTS_DIR_PATH / "proposer.yaml")
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
