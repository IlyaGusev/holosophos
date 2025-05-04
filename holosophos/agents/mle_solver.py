from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    CustomVisitWebpageTool,
    remote_text_editor_tool,
    remote_bash_tool,
    remote_download_tool,
    hf_datasets_search_tool,
)

NAME = "mle_solver"
DESCRIPTION = """This team member is an egineer that writes code and runs computational experiments using remote GPUs.
He has access to tools that write and execute code on a remote GPU.
Ask him when you need to solve any programming tasks that require GPU.
Give him your detailed task as an argument. Follow the task format described above, include all the details."""


def get_mle_solver_agent(
    model: Model,
    max_steps: int = 42,
    planning_interval: Optional[int] = 7,
    max_print_outputs_length: int = 20000,
    verbosity_level: int = 2,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[
            remote_bash_tool,
            remote_text_editor_tool,
            remote_download_tool,
            hf_datasets_search_tool,
            DuckDuckGoSearchTool(),
            CustomVisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("mle_solver"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
        verbosity_level=verbosity_level,
    )
