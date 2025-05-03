from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import md_to_pdf_tool

NAME = "writer"
DESCRIPTION = """This team member is a technical writer that can create PDF reports from Markdown content.
He has access to tools for converting Markdown to PDF using LaTeX.
Ask him when you need to create PDF reports with mathematical formulas, tables, and plots.
Important note: Any tasks related to PDF creation should be delegated to the writer agent.

The writer agent is specifically designed to handle:
- Writing technical texts
- Converting Markdown to PDF
- Including mathematical formulas
- Formatting technical documents
- Creating reports with plots and tables
"""


def get_writer_agent(
    model: Model,
    max_steps: int = 42,
    planning_interval: Optional[int] = 7,
    max_print_outputs_length: int = 20000,
    verbosity_level: int = 2,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[md_to_pdf_tool],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("writer"),
        max_print_outputs_length=max_print_outputs_length,
        verbosity_level=verbosity_level,
    )
