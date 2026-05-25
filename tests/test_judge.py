import pytest
from unittest.mock import patch
from runner.judge import extract_score, cross_judge
from runner.ollama import GenerationResult


def fake_result(text: str) -> GenerationResult:
    return GenerationResult(model="test", output=text, ttft_ms=10.0, total_ms=100.0, token_count=5)


def test_extract_score_plain():
    assert extract_score("7") == 7


def test_extract_score_in_sentence():
    assert extract_score("I rate this response 8 out of 10.") == 8


def test_extract_score_ten():
    assert extract_score("10") == 10


def test_extract_score_invalid():
    assert extract_score("great!") is None


def test_cross_judge_excludes_self():
    outputs = {"llama3": "output A", "mistral": "output B", "qwen:7b": "output C"}
    with patch("runner.judge.generate", return_value=fake_result("8")):
        results = cross_judge("Write hello", outputs)
    for target, judgments in results.items():
        judges = [j for j, _ in judgments]
        assert target not in judges


def test_cross_judge_total_judgments():
    outputs = {"llama3": "A", "mistral": "B", "qwen:7b": "C"}
    with patch("runner.judge.generate", return_value=fake_result("7")):
        results = cross_judge("task", outputs)
    total = sum(len(v) for v in results.values())
    assert total == 6  # 3 models * 2 judges each
