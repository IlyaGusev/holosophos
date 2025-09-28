import logging
from typing import Any, Optional, Sequence

import fire  # type: ignore
from phoenix.otel import register
from codearkt.codeact import CodeActAgent, Prompts
from codearkt.llm import LLM
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_query

from holosophos.files import PROMPTS_DIR_PATH
from holosophos.settings import settings

from holosophos.agents import (
    get_librarian_agent,
    get_mle_solver_agent,
    get_writer_agent,
    get_proposer_agent,
    get_reviewer_agent,
)


MCP_CONFIG = {
    "mcpServers": {
        "academia": {"url": settings.ACADEMIA_MCP_URL, "transport": "streamable-http"},
        "mle_kit": {"url": settings.MLE_KIT_MCP_URL, "transport": "streamable-http"},
    }
}
AGENTS = ("librarian", "mle_solver", "writer", "proposer", "reviewer")


def compose_main_agent(
    model_name: str = settings.MODEL_NAME,
    max_completion_tokens: int = settings.MAX_COMPLETION_TOKENS,
    max_history_tokens: int = settings.MAX_HISTORY_TOKENS,
    verbosity_level: int = logging.INFO,
    tools: Optional[Sequence[str]] = None,
    included_agents: Sequence[str] = AGENTS,
) -> CodeActAgent:
    model = LLM(
        model_name=model_name,
        max_completion_tokens=max_completion_tokens,
        max_history_tokens=max_history_tokens,
    )

    librarian_agent = get_librarian_agent(
        model=model,
        verbosity_level=verbosity_level,
        max_iterations=settings.LIBRARIAN_MAX_ITERATIONS,
        planning_interval=settings.LIBRARIAN_PLANNING_INTERVAL,
        tools=settings.LIBRARIAN_TOOLS,
    )
    mle_solver_agent = get_mle_solver_agent(
        model=model,
        max_iterations=settings.MLE_SOLVER_MAX_ITERATIONS,
        verbosity_level=verbosity_level,
        planning_interval=settings.MLE_SOLVER_PLANNING_INTERVAL,
        is_remote=settings.MLE_SOLVER_IS_REMOTE,
        tools=(
            settings.MLE_SOLVER_TOOLS_REMOTE
            if settings.MLE_SOLVER_IS_REMOTE
            else settings.MLE_SOLVER_TOOLS
        ),
    )
    writer_agent = get_writer_agent(
        model=model,
        max_iterations=settings.WRITER_MAX_ITERATIONS,
        verbosity_level=verbosity_level,
        planning_interval=settings.WRITER_PLANNING_INTERVAL,
        tools=settings.WRITER_TOOLS,
    )
    proposer_agent = get_proposer_agent(
        model=model,
        max_iterations=settings.PROPOSER_MAX_ITERATIONS,
        verbosity_level=verbosity_level,
        planning_interval=settings.PROPOSER_PLANNING_INTERVAL,
        tools=settings.PROPOSER_TOOLS,
    )
    reviewer_agent = get_reviewer_agent(
        model=model,
        max_iterations=settings.REVIEWER_MAX_ITERATIONS,
        verbosity_level=verbosity_level,
        planning_interval=settings.REVIEWER_PLANNING_INTERVAL,
        tools=settings.REVIEWER_TOOLS,
    )
    prompts = Prompts.load(PROMPTS_DIR_PATH / "system.yaml")
    agents = (librarian_agent, mle_solver_agent, writer_agent, proposer_agent, reviewer_agent)
    managed_agents = [agent for agent in agents if agent.name in included_agents]
    if tools is None:
        tools = settings.MANAGER_TOOLS
    agent = CodeActAgent(
        name="manager",
        description="Manager agent",
        tool_names=tools,
        managed_agents=managed_agents,
        llm=model,
        max_iterations=settings.MANAGER_MAX_ITERATIONS,
        planning_interval=settings.MANAGER_PLANNING_INTERVAL,
        verbosity_level=verbosity_level,
        prompts=prompts,
    )
    return agent


async def run_main_agent(
    query: str,
    model_name: str = settings.MODEL_NAME,
    verbosity_level: int = logging.INFO,
    enable_phoenix: bool = False,
    phoenix_project_name: str = settings.PHOENIX_PROJECT_NAME,
    phoenix_endpoint: str = settings.RESOLVED_PHOENIX_ENDPOINT,
    included_agents: Sequence[str] = AGENTS,
) -> Any:
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
        included_agents=included_agents,
    )
    return await run_query(query, agent, mcp_config=MCP_CONFIG, add_mcp_server_prefixes=False)


if __name__ == "__main__":
    fire.Fire(run_main_agent)
