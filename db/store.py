import json
import sqlite3
from datetime import datetime, timezone


def insert_run(conn: sqlite3.Connection, n_repeats: int, models: list, categories: list) -> int:
    cur = conn.execute(
        "INSERT INTO runs (created_at, n_repeats, models, categories) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), n_repeats, json.dumps(models), json.dumps(categories)),
    )
    conn.commit()
    return cur.lastrowid


def insert_response(
    conn, run_id, model, prompt_id, category, repeat_index, output, ttft_ms, total_ms, token_count
) -> int:
    cur = conn.execute(
        "INSERT INTO responses "
        "(run_id, model, prompt_id, category, repeat_index, output, ttft_ms, total_ms, token_count) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, model, prompt_id, category, repeat_index, output, ttft_ms, total_ms, token_count),
    )
    conn.commit()
    return cur.lastrowid


def insert_metric(conn, response_id: int, metric: str, value: float) -> None:
    conn.execute(
        "INSERT INTO metric_scores (response_id, metric, value) VALUES (?, ?, ?)",
        (response_id, metric, value),
    )
    conn.commit()


def insert_judge_score(
    conn, run_id: int, judge_model: str, target_model: str, prompt_id: str, ordering: str, score: int
) -> None:
    conn.execute(
        "INSERT INTO judge_scores (run_id, judge_model, target_model, prompt_id, ordering, score) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, judge_model, target_model, prompt_id, ordering, score),
    )
    conn.commit()


def get_runs(conn) -> list:
    rows = conn.execute("SELECT * FROM runs ORDER BY created_at DESC").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["models"] = json.loads(d["models"])
        d["categories"] = json.loads(d["categories"])
        result.append(d)
    return result


def get_responses_for_run(conn, run_id: int) -> list:
    return [
        dict(r)
        for r in conn.execute("SELECT * FROM responses WHERE run_id = ?", (run_id,)).fetchall()
    ]


def get_metric_scores_for_run(conn, run_id: int) -> list:
    return [
        dict(r)
        for r in conn.execute(
            """SELECT ms.*, r.model, r.prompt_id, r.category, r.repeat_index
               FROM metric_scores ms
               JOIN responses r ON ms.response_id = r.id
               WHERE r.run_id = ?""",
            (run_id,),
        ).fetchall()
    ]


def get_judge_scores_for_run(conn, run_id: int) -> list:
    return [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM judge_scores WHERE run_id = ?", (run_id,)
        ).fetchall()
    ]
