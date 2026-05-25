import re
from runner.ollama import generate

JUDGE_PROMPT = """\
You are an expert evaluator. Score the following response on a scale of 1 to 10.
Criteria: correctness, clarity, completeness. Do NOT favor longer responses.

Task: {task}
Response: {response}

Reply with a single integer from 1 to 10 and nothing else."""


def extract_score(text: str) -> int | None:
    match = re.search(r"\b(10|[1-9])\b", text.strip())
    return int(match.group(1)) if match else None


def cross_judge(task: str, outputs: dict) -> dict:
    """
    outputs: {model_name: response_text}
    Returns: {target_model: [(judge_model, score), ...]}
    Self-judgments excluded.
    """
    results = {model: [] for model in outputs}
    for judge in outputs:
        for target in outputs:
            if judge == target:
                continue
            result = generate(judge, JUDGE_PROMPT.format(task=task, response=outputs[target]))
            score = extract_score(result.output)
            if score is not None:
                results[target].append((judge, score))
    return results
