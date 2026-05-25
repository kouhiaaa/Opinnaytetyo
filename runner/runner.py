import sqlite3
from pathlib import Path
from typing import Callable

from runner.ollama import generate
from runner.metrics import compute_bert_score, compute_determinism, tokens_per_second
from runner.judge import cross_judge
from runner.prompts import load_prompts, PROMPTS_DIR
from db.store import insert_run, insert_response, insert_metric, insert_judge_score


def run_benchmark(
    conn: sqlite3.Connection,
    models: list,
    categories: list,
    n_repeats: int,
    prompts_dir: Path = None,
    on_progress: Callable[[int, int, str], None] = None,
) -> int:
    if n_repeats < 1:
        raise ValueError("n_repeats must be at least 1")
    prompts = load_prompts(categories=categories, prompts_dir=prompts_dir or PROMPTS_DIR)
    run_id = insert_run(conn, n_repeats, models, categories)
    total = len(models) * len(prompts) * n_repeats
    step = 0
    outputs_store: dict = {}  # (model, prompt_id, repeat) -> (output, response_id)

    for prompt in prompts:
        for model in models:
            repeat_outputs = []
            repeat_ids = []
            for repeat in range(n_repeats):
                step += 1
                if on_progress:
                    on_progress(step, total, f"{model} · {prompt.id} · {repeat + 1}/{n_repeats}")

                result = generate(model, prompt.prompt)
                resp_id = insert_response(
                    conn, run_id, model, prompt.id, prompt.category,
                    repeat, result.output, result.ttft_ms, result.total_ms, result.token_count,
                )
                insert_metric(conn, resp_id, "tokens_per_second", tokens_per_second(result.token_count, result.total_ms))
                repeat_outputs.append(result.output)
                repeat_ids.append(resp_id)
                outputs_store[(model, prompt.id, repeat)] = (result.output, resp_id)

            bert_results = compute_bert_score(repeat_outputs, [prompt.reference] * n_repeats)
            for i, bs in enumerate(bert_results):
                for metric, value in bs.items():
                    insert_metric(conn, repeat_ids[i], metric, value)

            insert_metric(conn, repeat_ids[0], "determinism", compute_determinism(repeat_outputs))

    for prompt in prompts:
        best_outputs = {model: outputs_store[(model, prompt.id, 0)][0] for model in models}
        for target_model, judgments in cross_judge(prompt.prompt, best_outputs).items():
            for judge_model, score in judgments:
                insert_judge_score(conn, run_id, judge_model, target_model, prompt.id, "pointwise", score)

    return run_id
