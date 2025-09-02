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

DEFAULT_TOOLS = (
    "mle_kit_remote_bash",
    "mle_kit_remote_text_editor",
    "mle_kit_remote_download",
    "mle_kit_llm_proxy_remote",
    "academia_hf_datasets_search",
    "academia_web_search",
    "academia_visit_webpage",
)


def get_mle_solver_agent(
    model: LLM,
    max_iterations: int = 42,
    planning_interval: Optional[int] = 7,
    verbosity_level: int = logging.INFO,
    tools: Optional[Sequence[str]] = None,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "mle_solver.yaml")
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
