WEIGHTS = {
    "judge_mean": 0.40,
    "bert_f1": 0.30,
    "determinism": 0.20,
    "judge_if_mean": 0.10,
}


def compute_composite_scores(model_metrics: dict) -> dict:
    """
    model_metrics: {model_name: {metric_name: float}}
    Returns: {model_name: composite_score} where scores are in [0, 1].

    judge_mean and judge_if_mean are on a 1-10 scale, normalized by dividing by 10.
    bert_f1 and determinism are already in [0, 1].
    tokens_per_second is excluded from quality composite — shown separately in the dashboard.
    """
    normalized = {model: {} for model in model_metrics}

    for model, vals in model_metrics.items():
        normalized[model]["judge_mean"] = vals.get("judge_mean", 0.0) / 10.0
        normalized[model]["judge_if_mean"] = vals.get("judge_if_mean", 0.0) / 10.0
        normalized[model]["bert_f1"] = vals.get("bert_f1", 0.0)
        normalized[model]["determinism"] = vals.get("determinism", 0.0)

    return {
        model: sum(WEIGHTS[m] * normalized[model][m] for m in WEIGHTS)
        for model in model_metrics
    }
