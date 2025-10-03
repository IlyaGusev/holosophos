import logging
from typing import Optional, Sequence

from codearkt.codeact import CodeActAgent
from codearkt.prompt_storage import PromptStorage
from codearkt.llm import LLM

from holosophos.files import PROMPTS_DIR_PATH


NAME = "writer"
DESCRIPTION = """This team member is a technical writer that can create PDF papers/reports.
He has access to tools for composing and compiling LaTeX.
Ask him when you need to create PDF papers/reports with mathematical formulas, tables, and plots.
Important note: Any tasks related to PDF creation should be delegated to the writer agent.

The writer agent is specifically designed to handle:
- Writing technical texts
- Including mathematical formulas
- Formatting technical documents
- Creating reports with plots and tables
"""


def get_writer_agent(
    model: LLM,
    max_iterations: int,
    planning_interval: Optional[int],
    tools: Sequence[str],
    verbosity_level: int = logging.INFO,
) -> CodeActAgent:
    prompts = PromptStorage.load(PROMPTS_DIR_PATH / "writer.yaml")
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
