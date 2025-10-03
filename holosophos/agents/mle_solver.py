import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent
from codearkt.prompt_storage import PromptStorage
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH

NAME = "mle_solver"
DESCRIPTION = """This team member is an engineer who writes code and runs computational experiments.
He has access to tools that write and execute code.
Ask him when you need to solve any programming tasks.
Give him your detailed task as an argument.
Follow the task format described above, and include all the details."""


def get_mle_solver_agent(
    model: LLM,
    max_iterations: int,
    planning_interval: Optional[int],
    tools: Sequence[str],
    verbosity_level: int = logging.INFO,
    is_remote: bool = False,
) -> CodeActAgent:
    if is_remote:
        prompts = PromptStorage.load(PROMPTS_DIR_PATH / "mle_solver_remote.yaml")
    else:
        prompts = PromptStorage.load(PROMPTS_DIR_PATH / "mle_solver.yaml")
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
