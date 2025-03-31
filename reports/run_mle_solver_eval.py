import json
from typing import Any, Optional
from dataclasses import dataclass

import fire  # type: ignore
from holosophos.main_agent import run_main_agent


@dataclass
class AgentTask:
    query: str
    model_name: str
    task_id: int
    field: str
    target: float


def run_eval(
    input_path: str,
    model_name: str = "gpt-4o-mini",
    max_workers: int = 1,
    verbosity_level: int = 2,
    nrows: Optional[int] = None,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos-aboriskin",
    phoenix_endpoint: str = "https://app.phoenix.arize.com/v1/traces",
) -> None:
    with open(input_path) as f:
        records = [json.loads(line) for line in f]
    if nrows:
        records = records[:nrows]
    tasks = [
        AgentTask(model_name=model_name, task_id=i, **r) for i, r in enumerate(records)
    ]

    def worker(task: AgentTask) -> Any:
        answer = run_main_agent(
            query=task.query,
            model_name=task.model_name,
            verbosity_level=verbosity_level,
            enable_phoenix=enable_phoenix,
            phoenix_project_name=phoenix_project_name,
            phoenix_endpoint=phoenix_endpoint,
        )
        return answer

    correct_count = 0
    for record, task in zip(records, tasks):
        result = worker(task)
        query = record["query"]
        field = record["field"]
        target = record["target"]
        is_correct = False
        predicted_value = None
        if isinstance(result, str) and "{" in result and "}" in result:
            json_result = result[result.find("{") : result.rfind("}") + 1]
            json_result = json_result.replace("'", '"')
            parsed_result = json.loads(json_result)
            if field in parsed_result:
                predicted_value = parsed_result[field]
                if predicted_value >= target:
                    is_correct = True
        elif isinstance(result, dict):
            if field in result:
                predicted_value = result[field]
                if predicted_value >= target:
                    is_correct = True
        correct_count += int(is_correct)
        print(
            f"Query: {query}\nTarget: {target}\nResult: {result}\nLabel: {is_correct}\n\n"
        )
    print(f"Overall accuracy: {correct_count / len(records) * 100.0:.1f}")


if __name__ == "__main__":
    fire.Fire(run_eval)
