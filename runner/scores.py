WEIGHTS = {
    "judge_mean": 0.35,
    "bert_f1": 0.25,
    "determinism": 0.20,
    "tokens_per_second": 0.10,
    "judge_if_mean": 0.10,
}


def compute_composite_scores(model_metrics: dict) -> dict:
    """
    model_metrics: {model_name: {metric_name: float}}
    Returns: {model_name: composite_score} where scores are in [0, 1].

    judge_mean and judge_if_mean are on a 1-10 scale, normalized by dividing by 10.
    tokens_per_second is normalized relative to the fastest model.
    bert_f1 and determinism are already in [0, 1].
    """
    normalized = {model: {} for model in model_metrics}

    max_tps = max((v.get("tokens_per_second", 0.0) for v in model_metrics.values()), default=1.0) or 1.0

    for model, vals in model_metrics.items():
        normalized[model]["judge_mean"] = vals.get("judge_mean", 0.0) / 10.0
        normalized[model]["judge_if_mean"] = vals.get("judge_if_mean", 0.0) / 10.0
        normalized[model]["bert_f1"] = vals.get("bert_f1", 0.0)
        normalized[model]["determinism"] = vals.get("determinism", 0.0)
        normalized[model]["tokens_per_second"] = vals.get("tokens_per_second", 0.0) / max_tps

    return {
        model: sum(WEIGHTS[m] * normalized[model][m] for m in WEIGHTS)
        for model in model_metrics
    }
