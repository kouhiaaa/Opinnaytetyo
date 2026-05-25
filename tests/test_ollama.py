import json
import pytest
from unittest.mock import patch, MagicMock
from runner.ollama import generate, GenerationResult


def make_stream(tokens):
    lines = [json.dumps({"response": t}).encode() for t in tokens]
    lines.append(json.dumps({"response": "", "done": True}).encode())
    mock_resp = MagicMock()
    mock_resp.iter_lines.return_value = iter(lines)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_generate_returns_result():
    with patch("runner.ollama.requests.post", return_value=make_stream(["Hello", " world"])):
        result = generate("llama3", "Say hello")
    assert isinstance(result, GenerationResult)
    assert result.output == "Hello world"
    assert result.model == "llama3"
    assert result.token_count == 2


def test_generate_measures_latency():
    with patch("runner.ollama.requests.post", return_value=make_stream(["Hi"])):
        result = generate("llama3", "Hi")
    assert result.ttft_ms > 0
    assert result.total_ms >= result.ttft_ms


def test_generate_calls_on_token():
    received = []
    with patch("runner.ollama.requests.post", return_value=make_stream(["A", "B", "C"])):
        generate("llama3", "test", on_token=received.append)
    assert received == ["A", "B", "C"]
