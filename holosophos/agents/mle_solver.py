import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH

NAME = "mle_solver"
DESCRIPTION = """This team member is an engineer who writes code and runs computational experiments using remote GPUs.
He has access to tools that write and execute code on a remote GPU.
Ask him when you need to solve any programming tasks that require a GPU.
Give him your detailed task as an argument.
Follow the task format described above, and include all the details."""


def get_mle_solver_agent(
    model: LLM,
    max_iterations: int,
    planning_interval: Optional[int],
    tools: Sequence[str],
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "mle_solver.yaml")
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
