import logging
from logging.config import dictConfig
from typing import Any

import fire  # type: ignore
from uvicorn.config import LOGGING_CONFIG as UVICORN_LOGGING_CONFIG
from phoenix.otel import register
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_server

from holosophos.main_agent import MCP_CONFIG, compose_main_agent
from holosophos.settings import settings


def configure_uvicorn_style_logging(level: int = logging.INFO) -> None:
    config = {**UVICORN_LOGGING_CONFIG}
    config["disable_existing_loggers"] = False
    config["root"] = {"handlers": ["default"], "level": logging.getLevelName(level)}
    dictConfig(config)


def server(
    model_name: str = settings.MODEL_NAME,
    verbosity_level: int = settings.VERBOSITY_LEVEL,
    enable_phoenix: bool = settings.ENABLE_PHOENIX,
    phoenix_project_name: str = settings.PHOENIX_PROJECT_NAME,
    phoenix_endpoint: str = settings.RESOLVED_PHOENIX_ENDPOINT,
    max_completion_tokens: int = settings.MAX_COMPLETION_TOKENS,
    max_history_tokens: int = settings.MAX_HISTORY_TOKENS,
    port: int = settings.PORT,
) -> Any:
    configure_uvicorn_style_logging(verbosity_level)
    logger = logging.getLogger(__name__)
    logger.setLevel(verbosity_level)
    logger.info(f"Running with {model_name} model")
    logger.info(f"Context: {max_history_tokens} tokens")
    logger.info(f"Output: {max_completion_tokens} tokens")
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
        max_completion_tokens=max_completion_tokens,
        max_history_tokens=max_history_tokens,
    )
    run_server(agent, MCP_CONFIG, add_mcp_server_prefixes=False, port=port)


if __name__ == "__main__":
    fire.Fire(server)
