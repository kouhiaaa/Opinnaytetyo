# pages/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.schema import init_db
from db.store import get_runs, get_responses_for_run, get_metric_scores_for_run, get_judge_scores_for_run
from runner.scores import compute_composite_scores


def _aggregate(run_id: int, conn) -> dict:
    responses = get_responses_for_run(conn, run_id)
    metrics_rows = get_metric_scores_for_run(conn, run_id)
    judge_rows = get_judge_scores_for_run(conn, run_id)
    models = list({r["model"] for r in responses})

    acc = {m: {"bert_f1": [], "determinism": [], "tokens_per_second": [], "judge_mean": [], "judge_if_mean": []} for m in models}

    for row in metrics_rows:
        key = row["metric"]
        if key in ("bert_f1", "determinism", "tokens_per_second"):
            acc[row["model"]][key].append(row["value"])

    prompt_categories = {r["prompt_id"]: r["category"] for r in responses}
    for row in judge_rows:
        cat = prompt_categories.get(row["prompt_id"], "")
        bucket = "judge_if_mean" if cat == "instruction_following" else "judge_mean"
        acc[row["target_model"]][bucket].append(row["score"])

    return {
        model: {k: (sum(v) / len(v) if v else 0.0) for k, v in vals.items()}
        for model, vals in acc.items()
    }


def show():
    st.header("Dashboard")
    conn = init_db()
    runs = get_runs(conn)

    if not runs:
        st.info("No benchmark runs yet. Go to Run Benchmarks to start.")
        return

    run_options = {f"Run #{r['id']} — {r['created_at'][:19]}": r["id"] for r in runs}
    selected_label = st.selectbox("Select run", list(run_options.keys()))
    run_id = run_options[selected_label]

    model_metrics = _aggregate(run_id, conn)
    composite = compute_composite_scores(model_metrics)

    st.subheader("Leaderboard")
    lb_df = pd.DataFrame([
        {"Model": m, "Composite Score": round(s, 4)}
        for m, s in sorted(composite.items(), key=lambda x: -x[1])
    ])
    st.dataframe(lb_df, use_container_width=True)

    st.subheader("Category Breakdown (Radar)")
    metric_keys = ["bert_f1", "determinism", "tokens_per_second", "judge_mean", "judge_if_mean"]
    labels = ["BERTScore F1", "Determinism", "Speed", "Judge Score", "Instr. Following"]
    max_tps = max((v["tokens_per_second"] for v in model_metrics.values()), default=1.0) or 1.0
    fig_radar = go.Figure()
    for model, vals in model_metrics.items():
        r_vals = [
            vals["bert_f1"],
            vals["determinism"],
            vals["tokens_per_second"] / max_tps,
            vals["judge_mean"] / 10.0,
            vals["judge_if_mean"] / 10.0,
        ]
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals + [r_vals[0]], theta=labels + [labels[0]], fill="toself", name=model
        ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("Metric Comparison")
    cols = st.columns(3)
    bar_specs = [
        ("BERTScore F1", "bert_f1"),
        ("Judge Score (1–10)", "judge_mean"),
        ("Determinism", "determinism"),
    ]
    for col, (label, key) in zip(cols, bar_specs):
        df = pd.DataFrame([{"Model": m, label: vals[key]} for m, vals in model_metrics.items()])
        col.plotly_chart(px.bar(df, x="Model", y=label, title=label), use_container_width=True)

    st.subheader("Export")
    responses = get_responses_for_run(conn, run_id)
    st.download_button(
        "Download Responses CSV",
        pd.DataFrame(responses).to_csv(index=False),
        "responses.csv",
        "text/csv",
    )
