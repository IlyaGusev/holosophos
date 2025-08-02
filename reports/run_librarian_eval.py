import json
import logging
import asyncio
from typing import Any, List, Optional
from dataclasses import dataclass

import fire  # type: ignore
from tqdm import tqdm
from holosophos.main_agent import run_main_agent


@dataclass
class AgentTask:
    query: str
    model_name: str
    task_id: int
    target: List[str]


def run_eval(
    input_path: str,
    model_name: str = "deepseek/deepseek-chat-v3-0324",
    max_workers: int = 1,
    verbosity_level: int = logging.INFO,
    nrows: Optional[int] = None,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "http://localhost:6006/v1/traces",
) -> None:
    with open(input_path) as f:
        records = [json.loads(line) for line in f]
    if nrows:
        records = records[:nrows]
    tasks = [
        AgentTask(
            query=r["query"], target=r["target"], model_name=model_name, task_id=i
        )
        for i, r in enumerate(records)
    ]

    async def worker(task: AgentTask) -> Any:
        answer = await run_main_agent(
            query=task.query,
            model_name=task.model_name,
            verbosity_level=verbosity_level,
            enable_phoenix=enable_phoenix,
            phoenix_project_name=phoenix_project_name,
            phoenix_endpoint=phoenix_endpoint,
        )
        print(f"TARGET: {task.target}\nPREDICTED: {answer}")
        return answer

    async def run_all_tasks():
        semaphore = asyncio.Semaphore(max_workers)
        results = []

        async def sem_worker(task):
            async with semaphore:
                return await worker(task)

        coros = [sem_worker(task) for task in tasks]
        for f in tqdm(
            asyncio.as_completed(coros),
            total=len(tasks),
            desc="Processing queries",
            unit="query",
        ):
            result = await f
            results.append(result)
        return results

    results = asyncio.run(run_all_tasks())

    correct_count = 0
    for record, result in zip(records, results):
        query = record["query"]
        target = record["target"]
        is_correct = False
        for arxiv_id in target:
            if arxiv_id in str(result):
                is_correct = True
        correct_count += int(is_correct)
        print(
            f"Query: {query}\nTarget: {target}\nPrediction: {result}\nLabel: {is_correct}\n\n"
        )
    print(f"Overall accuracy: {correct_count / len(records) * 100.0:.1f}")


if __name__ == "__main__":
    fire.Fire(run_eval)
