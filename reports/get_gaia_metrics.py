import json
from statistics import mean, median

from datasets import load_dataset  # type: ignore
import pandas as pd  # type: ignore
import fire  # type: ignore

from reports.run_gaia import _answer_scorer, _get_final_answer


def get_gaia_metrics(predictions_path: str) -> None:
    with open(predictions_path) as r:
        records = [json.loads(line) for line in r]

    eval_ds = load_dataset("gaia-benchmark/GAIA", "2023_all")["validation"]
    eval_ds = eval_ds.rename_columns(
        {"Question": "question", "Final answer": "true_answer", "Level": "task"}
    )
    eval_df = pd.DataFrame(eval_ds)
    tasks_to_run = eval_df.to_dict(orient="records")
    correct_count = 0
    timeout_count = 0
    all_count = 0
    for record in records:
        true_answer = None
        for task in tasks_to_run:
            if task["question"] in record["query"]:
                true_answer = task["true_answer"]
                break
        assert true_answer is not None
        predicted_answer = record["result"]
        predicted_answer = _get_final_answer(predicted_answer)
        if "timeout" in predicted_answer.lower():
            timeout_count += 1
        is_correct = _answer_scorer(predicted_answer, str(true_answer))
        correct_count += int(is_correct)
        all_count += 1

        if not is_correct:
            print("True answer:", true_answer)
            print("Predicted answwer:", predicted_answer)
            print("Session ID:", record["session_id"])
            print()
    print("Accuracy:", correct_count / all_count)
    print("Timeouts:", timeout_count / all_count)

    total_prompt_tokens = sum([r["token_usage"]["prompt_tokens"] for r in records])
    total_completion_tokens = sum([r["token_usage"]["completion_tokens"] for r in records])
    avg_duration = mean([r["duration"] for r in records])
    median_duration = median([r["duration"] for r in records])
    print("Num tasks:", len(records))
    print(f"Prompt tokens: {total_prompt_tokens // 1000000}M, {total_prompt_tokens}")
    print(f"Completion tokens: {total_completion_tokens // 1000000}M, {total_completion_tokens}")
    print("Avg duration:", avg_duration)
    print("Median duration:", median_duration)


if __name__ == "__main__":
    fire.Fire(get_gaia_metrics)
