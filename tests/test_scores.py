import pytest
from runner.scores import compute_composite_scores


def make_metrics(bert_f1, determinism, tps, judge_mean, judge_if_mean):
    return {
        "bert_f1": bert_f1,
        "determinism": determinism,
        "tokens_per_second": tps,
        "judge_mean": judge_mean,
        "judge_if_mean": judge_if_mean,
    }


def test_scores_in_range():
    model_metrics = {
        "llama3": make_metrics(0.8, 0.9, 20.0, 7.5, 7.0),
        "mistral": make_metrics(0.7, 0.85, 25.0, 6.5, 6.0),
        "qwen:7b": make_metrics(0.75, 0.88, 15.0, 7.0, 7.5),
    }
    scores = compute_composite_scores(model_metrics)
    for score in scores.values():
        assert 0.0 <= score <= 1.0


def test_better_model_scores_higher():
    model_metrics = {
        "good": make_metrics(0.95, 0.99, 50.0, 9.5, 9.5),
        "bad": make_metrics(0.3, 0.4, 5.0, 2.0, 2.0),
    }
    scores = compute_composite_scores(model_metrics)
    assert scores["good"] > scores["bad"]
