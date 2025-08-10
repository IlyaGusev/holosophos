import json
import logging
from typing import Optional
from dataclasses import dataclass

import fire  # type: ignore
from dotenv import load_dotenv
from phoenix.otel import register
from codearkt.otel import CodeActInstrumentor
from codearkt.server import run_batch

from holosophos.main_agent import MCP_CONFIG, compose_main_agent


@dataclass
class AgentTask:
    query: str
    model_name: str
    task_id: int
    field: str
    target: float


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
    correct_count = 0
    for record, result in zip(records, results):
        query = record["query"]
        field = record["field"]
        target = record["target"]
        is_less = record["mode"] == "less"
        is_correct = False
        predicted_value = None
        if isinstance(result, str) and "{" in result and "}" in result:
            json_result = result[result.find("{") : result.rfind("}") + 1]
            json_result = json_result.replace("'", '"')
            parsed_result = json.loads(json_result)
            if field in parsed_result:
                predicted_value = parsed_result[field]
        elif isinstance(result, dict):
            if field in result:
                predicted_value = result[field]

        if predicted_value is not None:
            if is_less and predicted_value <= target:
                is_correct = True
            elif not is_less and predicted_value >= target:
                is_correct = True
 
        correct_count += int(is_correct)
        print(
            f"Query: {query}\nTarget: {target}\nResult: {result}\nLabel: {is_correct}\n\n"
        )
    print(f"Overall accuracy: {correct_count / len(records) * 100.0:.1f}")


if __name__ == "__main__":
    fire.Fire(run_eval)
