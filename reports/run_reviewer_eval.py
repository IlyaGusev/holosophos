import json
import logging
from typing import Optional

import fire  # type: ignore
from dotenv import load_dotenv
from phoenix.otel import register
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_batch

from holosophos.main_agent import MCP_CONFIG, compose_main_agent


async def run_eval(
    input_path: str,
    model_name: str = "deepseek/deepseek-chat-v3-0324",
    max_workers: int = 1,
    verbosity_level: int = logging.INFO,
    nrows: Optional[int] = None,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "http://localhost:6006/v1/traces",
) -> None:
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
    )

    with open(input_path) as f:
        records = [json.loads(line) for line in f]
    if nrows:
        records = records[:nrows]

    queries = [r["query"] for r in records]
    results = await run_batch(queries, agent, mcp_config=MCP_CONFIG, max_concurrency=max_workers)
    for result in results:
        print(result)


if __name__ == "__main__":
    fire.Fire(run_eval)
