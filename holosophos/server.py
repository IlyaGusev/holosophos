import logging
from typing import Any

import fire  # type: ignore
from dotenv import load_dotenv
from phoenix.otel import register
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_server

from holosophos.main_agent import MCP_CONFIG, compose_main_agent


def server(
    model_name: str = "deepseek/deepseek-chat-v3-0324",
    verbosity_level: int = logging.INFO,
    planning_interval: int = 4,
    max_iterations: int = 100,
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
    run_server(agent, MCP_CONFIG)


if __name__ == "__main__":
    fire.Fire(server)
