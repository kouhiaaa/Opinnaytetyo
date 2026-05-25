from db.schema import init_db


def test_init_db_creates_all_tables():
    conn = init_db(":memory:")
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not r[0].startswith("sqlite_")
    }
    assert tables == {"runs", "responses", "metric_scores", "judge_scores"}


def test_init_db_is_idempotent():
    conn = init_db(":memory:")
    from db.schema import CREATE_RUNS, CREATE_RESPONSES, CREATE_METRIC_SCORES, CREATE_JUDGE_SCORES
    for stmt in [CREATE_RUNS, CREATE_RESPONSES, CREATE_METRIC_SCORES, CREATE_JUDGE_SCORES]:
        conn.execute(stmt)  # IF NOT EXISTS — must not raise
