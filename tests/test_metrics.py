import pytest
from runner.metrics import tokens_per_second, compute_determinism, compute_bert_score


def test_tokens_per_second():
    assert tokens_per_second(100, 2000.0) == pytest.approx(50.0)


def test_tokens_per_second_zero_time():
    assert tokens_per_second(100, 0.0) == 0.0


def test_determinism_single_output():
    assert compute_determinism(["hello world"]) == 1.0


def test_determinism_identical_outputs():
    score = compute_determinism(["hello world", "hello world", "hello world"])
    assert score > 0.99


def test_determinism_different_outputs():
    score = compute_determinism(["hello world", "completely different sentence about other things"])
    assert 0.0 <= score <= 1.0


def test_bert_score_identical():
    results = compute_bert_score(["hello world"], ["hello world"])
    assert results[0]["bert_f1"] > 0.99


def test_bert_score_returns_all_fields():
    results = compute_bert_score(["hello"], ["hello"])
    assert "bert_precision" in results[0]
    assert "bert_recall" in results[0]
    assert "bert_f1" in results[0]
