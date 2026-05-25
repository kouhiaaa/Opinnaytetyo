import sqlite3

CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    n_repeats   INTEGER NOT NULL,
    models      TEXT    NOT NULL,
    categories  TEXT    NOT NULL
)
"""

CREATE_RESPONSES = """
CREATE TABLE IF NOT EXISTS responses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER NOT NULL,
    model        TEXT    NOT NULL,
    prompt_id    TEXT    NOT NULL,
    category     TEXT    NOT NULL,
    repeat_index INTEGER NOT NULL,
    output       TEXT    NOT NULL,
    ttft_ms      REAL    NOT NULL,
    total_ms     REAL    NOT NULL,
    token_count  INTEGER NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id)
)
"""

CREATE_METRIC_SCORES = """
CREATE TABLE IF NOT EXISTS metric_scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER NOT NULL,
    metric      TEXT    NOT NULL,
    value       REAL    NOT NULL,
    FOREIGN KEY (response_id) REFERENCES responses(id)
)
"""

CREATE_JUDGE_SCORES = """
CREATE TABLE IF NOT EXISTS judge_scores (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER NOT NULL,
    judge_model  TEXT    NOT NULL,
    target_model TEXT    NOT NULL,
    prompt_id    TEXT    NOT NULL,
    ordering     TEXT    NOT NULL,
    score        INTEGER NOT NULL,
    FOREIGN KEY (run_id) REFERENCES runs(id)
)
"""


def init_db(db_path: str = "results.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    for stmt in [CREATE_RUNS, CREATE_RESPONSES, CREATE_METRIC_SCORES, CREATE_JUDGE_SCORES]:
        conn.execute(stmt)
    conn.commit()
    return conn
