import logging
from typing import Optional

from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


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
    model: LLM,
    max_iterations: int = 42,
    planning_interval: Optional[int] = None,
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = Prompts.load(PROMPTS_DIR_PATH / "writer.yaml")
    return CodeActAgent(
        name=NAME,
        description=DESCRIPTION,
        tool_names=["academia_md_to_pdf"],
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        prompts=prompts,
        verbosity_level=verbosity_level,
    )
