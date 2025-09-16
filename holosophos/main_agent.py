import os
import logging
from typing import Any, Optional

import fire  # type: ignore
from phoenix.otel import register
from dotenv import load_dotenv
from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_query

from holosophos.files import PROMPTS_DIR_PATH

from holosophos.agents import (
    get_librarian_agent,
    get_mle_solver_agent,
    get_writer_agent,
    get_proposer_agent,
    get_reviewer_agent,
)


MODEL1 = "deepseek/deepseek-chat-v3-0324"
ACADEMIA_MCP_URL = os.getenv("ACADEMIA_MCP_URL", "http://0.0.0.0:5056/mcp")
MLE_KIT_MCP_URL = os.getenv("MLE_KIT_MCP_URL", "http://0.0.0.0:5057/mcp")
MCP_CONFIG = {
    "mcpServers": {
        "academia": {"url": ACADEMIA_MCP_URL, "transport": "streamable-http"},
        "mle_kit": {"url": MLE_KIT_MCP_URL, "transport": "streamable-http"},
    }
}
DEFAULT_TOOLS = (
    "bash",
    "text_editor",
)


def compose_main_agent(
    model_name: str = MODEL1,
    verbosity_level: int = logging.INFO,
    planning_interval: Optional[int] = 9,
    max_iterations: int = 100,
    librarian_max_iterations: int = 100,
    mle_solver_max_iterations: int = 200,
    writer_max_iterations: int = 100,
    proposer_max_iterations: int = 200,
    librarian_planning_interval: Optional[int] = 9,
    mle_solver_planning_interval: Optional[int] = 14,
    writer_planning_interval: Optional[int] = 9,
    proposer_planning_interval: Optional[int] = 9,
    reviewer_max_iterations: int = 50,
    reviewer_planning_interval: Optional[int] = 9,
    max_completion_tokens: int = 8192,
    max_history_tokens: int = 131072,
) -> CodeActAgent:
    load_dotenv()
    model = LLM(
        model_name=model_name,
        max_completion_tokens=max_completion_tokens,
        max_history_tokens=max_history_tokens,
    )

    librarian_agent = get_librarian_agent(
        model=model,
        verbosity_level=verbosity_level,
        max_iterations=librarian_max_iterations,
        planning_interval=librarian_planning_interval,
    )
    mle_solver_agent = get_mle_solver_agent(
        model=model,
        max_iterations=mle_solver_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=mle_solver_planning_interval,
    )
    writer_agent = get_writer_agent(
        model=model,
        max_iterations=writer_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=writer_planning_interval,
    )
    proposer_agent = get_proposer_agent(
        model=model,
        max_iterations=proposer_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=proposer_planning_interval,
    )
    reviewer_agent = get_reviewer_agent(
        model=model,
        max_iterations=reviewer_max_iterations,
        verbosity_level=verbosity_level,
        planning_interval=reviewer_planning_interval,
    )
    prompts = Prompts.load(PROMPTS_DIR_PATH / "system.yaml")
    agent = CodeActAgent(
        name="manager",
        description="Manager agent",
        tool_names=DEFAULT_TOOLS,
        managed_agents=[
            librarian_agent,
            mle_solver_agent,
            writer_agent,
            proposer_agent,
            reviewer_agent,
        ],
        llm=model,
        max_iterations=max_iterations,
        planning_interval=planning_interval,
        verbosity_level=verbosity_level,
        prompts=prompts,
    )
    return agent


async def run_main_agent(
    query: str,
    model_name: str = MODEL1,
    verbosity_level: int = logging.DEBUG,
    planning_interval: int = 3,
    max_iterations: int = 30,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "http://localhost:6006/v1/traces",
) -> Any:
    load_dotenv()
    if enable_phoenix and phoenix_project_name and phoenix_endpoint:
        register(
            project_name=phoenix_project_name,
            endpoint=phoenix_endpoint,
            auto_instrument=True,
        )
        CodeActInstrumentor().instrument()
    agent = compose_main_agent(
        model_name=model_name,
        verbosity_level=verbosity_level,
        planning_interval=planning_interval,
        max_iterations=max_iterations,
    )
    return await run_query(query, agent, mcp_config=MCP_CONFIG)


if __name__ == "__main__":
    fire.Fire(run_main_agent)
