import yaml
import pytest
from unittest.mock import patch
from db.schema import init_db
from db.store import get_runs, get_responses_for_run, get_metric_scores_for_run, get_judge_scores_for_run
from runner.ollama import GenerationResult
from runner.runner import run_benchmark

FAKE_YAML = {
    "prompts": [
        {"id": "p1", "category": "code_generation", "prompt": "Write hello", "reference": "print('hi')", "tags": []},
    ]
}


@pytest.fixture
def prompt_dir(tmp_path):
    (tmp_path / "code_generation.yaml").write_text(yaml.dump(FAKE_YAML))
    return tmp_path


def fake_generate(model, prompt, on_token=None):
    return GenerationResult(model=model, output=f"output-{model}", ttft_ms=50.0, total_ms=200.0, token_count=10)


def fake_bert_score(outputs, references):
    return [{"bert_precision": 0.9, "bert_recall": 0.85, "bert_f1": 0.87}] * len(outputs)


@pytest.fixture
def mocked_io(prompt_dir):
    with patch("runner.runner.generate", side_effect=fake_generate), \
         patch("runner.runner.compute_bert_score", side_effect=fake_bert_score), \
         patch("runner.runner.compute_determinism", return_value=0.95), \
         patch("runner.runner.cross_judge", return_value={"llama3": [], "mistral": []}):
        yield prompt_dir


@pytest.fixture
def mocked_io_with_judge_scores(prompt_dir):
    with patch("runner.runner.generate", side_effect=fake_generate), \
         patch("runner.runner.compute_bert_score", side_effect=fake_bert_score), \
         patch("runner.runner.compute_determinism", return_value=0.95), \
         patch("runner.runner.cross_judge", return_value={"llama3": [("mistral", 7)], "mistral": [("llama3", 8)]}):
        yield prompt_dir


def test_creates_run_record(mocked_io):
    conn = init_db(":memory:")
    run_id = run_benchmark(conn, models=["llama3", "mistral"], categories=["code_generation"], n_repeats=2, prompts_dir=mocked_io)
    runs = get_runs(conn)
    assert len(runs) == 1
    assert runs[0]["id"] == run_id
    assert runs[0]["n_repeats"] == 2


def test_stores_correct_response_count(mocked_io):
    conn = init_db(":memory:")
    run_benchmark(conn, models=["llama3", "mistral"], categories=["code_generation"], n_repeats=2, prompts_dir=mocked_io)
    responses = get_responses_for_run(conn, 1)
    # 2 models * 1 prompt * 2 repeats = 4 responses
    assert len(responses) == 4


def test_stores_metric_scores(mocked_io):
    conn = init_db(":memory:")
    run_id = run_benchmark(conn, models=["llama3", "mistral"], categories=["code_generation"], n_repeats=2, prompts_dir=mocked_io)
    metric_scores = get_metric_scores_for_run(conn, run_id)
    assert len(metric_scores) > 0


def test_stores_judge_scores(mocked_io_with_judge_scores):
    conn = init_db(":memory:")
    run_id = run_benchmark(conn, models=["llama3", "mistral"], categories=["code_generation"], n_repeats=2, prompts_dir=mocked_io_with_judge_scores)
    judge_scores = get_judge_scores_for_run(conn, run_id)
    assert len(judge_scores) > 0
