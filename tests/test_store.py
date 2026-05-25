import pytest
from db.schema import init_db
from db.store import (
    insert_run, insert_response, insert_metric, insert_judge_score,
    get_runs, get_responses_for_run, get_metric_scores_for_run, get_judge_scores_for_run,
)


@pytest.fixture
def conn():
    return init_db(":memory:")


def test_insert_and_get_run(conn):
    run_id = insert_run(conn, n_repeats=3, models=["llama3", "mistral"], categories=["code_generation"])
    assert isinstance(run_id, int)
    runs = get_runs(conn)
    assert len(runs) == 1
    assert runs[0]["n_repeats"] == 3
    assert runs[0]["models"] == ["llama3", "mistral"]
    assert runs[0]["categories"] == ["code_generation"]


def test_insert_response(conn):
    run_id = insert_run(conn, 1, ["llama3"], ["code_generation"])
    resp_id = insert_response(conn, run_id, "llama3", "p1", "code_generation", 0, "output", 100.0, 500.0, 50)
    assert isinstance(resp_id, int)
    responses = get_responses_for_run(conn, run_id)
    assert len(responses) == 1
    assert responses[0]["output"] == "output"
    assert responses[0]["token_count"] == 50


def test_insert_metric(conn):
    run_id = insert_run(conn, 1, ["llama3"], ["code_generation"])
    resp_id = insert_response(conn, run_id, "llama3", "p1", "code_generation", 0, "out", 50.0, 200.0, 20)
    insert_metric(conn, resp_id, "bert_f1", 0.85)
    scores = get_metric_scores_for_run(conn, run_id)
    assert len(scores) == 1
    assert scores[0]["metric"] == "bert_f1"
    assert abs(scores[0]["value"] - 0.85) < 1e-6


def test_insert_judge_score(conn):
    run_id = insert_run(conn, 1, ["llama3"], ["code_generation"])
    insert_judge_score(conn, run_id, "mistral", "llama3", "p1", "pointwise", 8)
    scores = get_judge_scores_for_run(conn, run_id)
    assert len(scores) == 1
    assert scores[0]["score"] == 8
    assert scores[0]["judge_model"] == "mistral"
