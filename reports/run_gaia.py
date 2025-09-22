import shutil
import logging
import re
import string
from pathlib import Path
from typing import Optional

import fire  # type: ignore
import pandas as pd
from datasets import load_dataset
from codearkt.server import run_batch
from phoenix.otel import register
from codearkt.otel import CodeActInstrumentor

from holosophos.utils import render_prompt
from holosophos.main_agent import compose_main_agent, MCP_CONFIG
from holosophos.settings import settings


QUESTION_PROMPT = """You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it
and find the exact correct answer (the answer does exist).
Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer!

Here is the question:
===
{{question}}
===

{% if attached_files %}Attached files (copied to the workspace):
{{attached_files}}{% endif %}

Return only the answer after the 'Final answer:' line.
Don't provide any explanations after the 'Final answer:' line.
Answer the given question exactly as requested, read the question carefully.
For instance if are asked "how many thousand hours..." and the answer is 2000 hours, return "2" not "2000".
Don't include measurement units (like m³ or Å or %) in a numerical final answer.
"""


def _normalize_number_str(number_str: str) -> float:
    for char in ["$", "%", ","]:
        number_str = number_str.replace(char, "")
    try:
        return float(number_str)
    except ValueError:
        return float("inf")


def _split_string(
    s: str,
    char_list: list[str] = [",", ";"],
) -> list[str]:
    pattern = f"[{''.join(char_list)}]"
    return re.split(pattern, s)


def _normalize_str(input_str, remove_punct=True) -> str:
    no_spaces = re.sub(r"\s", "", input_str)
    if remove_punct:
        translator = str.maketrans("", "", string.punctuation)
        return no_spaces.lower().translate(translator)
    else:
        return no_spaces.lower()


def _answer_scorer(
    model_answer: Optional[str],
    ground_truth: str,
) -> bool:
    def is_float(element: any) -> bool:
        try:
            float(element)
            return True
        except ValueError:
            return False
    if model_answer is None:
        model_answer = "None"

    if is_float(ground_truth):
        normalized_answer = _normalize_number_str(model_answer)
        return normalized_answer == float(ground_truth)

    elif any(char in ground_truth for char in [",", ";"]):
        gt_elems = _split_string(ground_truth)
        ma_elems = _split_string(model_answer)

        if len(gt_elems) != len(ma_elems):
            return False

        comparisons = []
        for ma_elem, gt_elem in zip(ma_elems, gt_elems):
            if is_float(gt_elem):
                normalized_ma_elem = _normalize_number_str(ma_elem)
                comparisons.append(normalized_ma_elem == float(gt_elem))
            else:
                comparisons.append(
                    _normalize_str(ma_elem, remove_punct=False)
                    == _normalize_str(gt_elem, remove_punct=False)
                )
        return all(comparisons)

    else:
        return _normalize_str(model_answer) == _normalize_str(ground_truth)


async def run_gaia(
    split: str = "validation",
    model_name: str = "deepseek/deepseek-chat-v3.1",
    max_workers: int = 1,
    verbosity_level: int = logging.INFO,
    nrows: Optional[int] = None,
    enable_phoenix: bool = False,
    phoenix_project_name: str = settings.PHOENIX_PROJECT_NAME,
    phoenix_endpoint: str = settings.RESOLVED_PHOENIX_ENDPOINT,
    predictions_path: str = "predictions.jsonl",
    files_only: bool = False,
):
    if enable_phoenix and phoenix_project_name and phoenix_endpoint:
        register(
            project_name=phoenix_project_name,
            endpoint=phoenix_endpoint,
            auto_instrument=True,
        )
        CodeActInstrumentor().instrument()

    eval_ds = load_dataset("gaia-benchmark/GAIA", "2023_all")[split]
    eval_ds = eval_ds.rename_columns(
        {"Question": "question", "Final answer": "true_answer", "Level": "task"}
    )
    eval_df = pd.DataFrame(eval_ds)
    tasks_to_run = eval_df.to_dict(orient="records")

    agent = compose_main_agent(
        model_name=model_name,
        verbosity_level=verbosity_level,
        included_agents=("librarian",),
    )
    tasks = []
    true_answers = []
    for example in tasks_to_run[:nrows]:
        file_path = example["file_path"]
        if files_only and not file_path:
            continue
        file_name = None
        if file_path:
            file_name = file_path.split("/")[-1]
            shutil.copy(file_path, Path(settings.WORKSPACE_DIR) / file_name)
        task = render_prompt(QUESTION_PROMPT, question=example["question"], attached_files=file_name)
        tasks.append(task)
        true_answers.append(example["true_answer"])

    predicted_answers = await run_batch(
        tasks,
        agent,
        mcp_config=MCP_CONFIG,
        max_concurrency=max_workers,
        add_mcp_server_prefixes=False,
        task_timeout=7200,
        output_path=Path(predictions_path),
    )

    correct_count = 0
    all_count = 0
    for predicted_answer, true_answer in zip(predicted_answers, true_answers):
        predicted_answer = predicted_answer.split("Final answer:")[-1].strip()
        is_correct = _answer_scorer(predicted_answer, true_answer)
        print(f"True answer: {true_answer}\nPredicted answer: {predicted_answer}")
        print(f"Is correct: {is_correct}")
        print()
        correct_count += int(is_correct)
        all_count += 1
    print(f"Overall accuracy: {correct_count / all_count * 100.0:.1f}")


if __name__ == "__main__":
    fire.Fire(run_gaia)
