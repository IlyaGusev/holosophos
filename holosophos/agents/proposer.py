from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import DocumentQATool, CustomVisitWebpageTool


NAME = "proposer"
DESCRIPTION = """This team member generates creative ideas for research experiments.
He analyzes existing ideas and proposes new research directions, assessing their interestingness, feasibility, and novelty.
Ask him when you need to come up with new experiments or research approaches.
Provide a detailed task description and context as an argument."""


def get_proposer_agent(
    model: Model,
    max_steps: int = 10,
    planning_interval: Optional[int] = 7,
    max_print_outputs_length: int = 20000,
    verbosity_level: int = 2,
    stream_outputs: bool = False,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[
            DuckDuckGoSearchTool(),
            DocumentQATool(model),
            CustomVisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("proposer"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
        verbosity_level=verbosity_level,
        stream_outputs=stream_outputs,
    )
