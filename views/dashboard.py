import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.schema import init_db
from db.store import get_runs, get_responses_for_run, get_metric_scores_for_run, get_judge_scores_for_run
from runner.scores import compute_composite_scores
from runner.prompts import load_prompts, PROMPTS_DIR
from views.run import MODEL_DISPLAY

CATEGORY_DISPLAY = {
    "code_generation": "Code Generation",
    "code_debugging": "Code Debugging",
    "logical_reasoning": "Logical Reasoning",
    "instruction_following": "Instruction Following",
    "general_quality": "General Quality",
}

MODEL_COLORS = ["#6366F1", "#10B981", "#F59E0B"]
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=13, color="#334155"),
    margin=dict(t=40, b=40, l=40, r=20),
)


def _label(model: str) -> str:
    return MODEL_DISPLAY.get(model, model)


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


def _aggregate_by_category(run_id: int, conn) -> dict:
    responses = get_responses_for_run(conn, run_id)
    metrics_rows = get_metric_scores_for_run(conn, run_id)
    judge_rows = get_judge_scores_for_run(conn, run_id)

    prompt_categories = {r["prompt_id"]: r["category"] for r in responses}
    models = list({r["model"] for r in responses})
    categories = list({r["category"] for r in responses})

    acc = {m: {c: {"bert_f1": [], "judge_mean": []} for c in categories} for m in models}

    for row in metrics_rows:
        if row["metric"] == "bert_f1":
            acc[row["model"]][row["category"]]["bert_f1"].append(row["value"])

    for row in judge_rows:
        cat = prompt_categories.get(row["prompt_id"])
        if cat and row["target_model"] in acc and cat in acc[row["target_model"]]:
            acc[row["target_model"]][cat]["judge_mean"].append(row["score"])

    return {
        m: {
            c: {k: (sum(v) / len(v) if v else None) for k, v in vals.items()}
            for c, vals in cat_vals.items()
        }
        for m, cat_vals in acc.items()
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
    sorted_models = sorted(composite.items(), key=lambda x: -x[1])

    # --- Top metric cards ---
    if sorted_models:
        winner = sorted_models[0][0]
        winner_score = sorted_models[0][1]
        avg_bert = sum(v["bert_f1"] for v in model_metrics.values()) / len(model_metrics)
        avg_judge = sum(v["judge_mean"] for v in model_metrics.values()) / len(model_metrics)
        n_responses = len(get_responses_for_run(conn, run_id))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏆 Top Model", _label(winner), f"score {winner_score:.3f}")
        c2.metric("📊 Avg BERTScore F1", f"{avg_bert:.3f}")
        c3.metric("⚖️ Avg Judge Score", f"{avg_judge / 10:.3f}")
        c4.metric("📝 Total Responses", n_responses)
        st.markdown("---")

    # --- Leaderboard ---
    st.subheader("Leaderboard")
    lb_df = pd.DataFrame([
        {
            "Model": _label(m),
            "Composite Score": round(s, 4),
            "BERTScore F1": round(model_metrics[m]["bert_f1"], 4),
            "Determinism": round(model_metrics[m]["determinism"], 4),
            "Judge Score": round(model_metrics[m]["judge_mean"] / 10.0, 4),
            "Speed (tok/s)": round(model_metrics[m]["tokens_per_second"], 2),
        }
        for m, s in sorted_models
    ])
    st.dataframe(lb_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- Radar chart ---
    st.subheader("Overall Performance")
    labels = ["BERTScore F1", "Determinism", "Speed", "Judge Score", "Instr. Following"]
    max_tps = max((v["tokens_per_second"] for v in model_metrics.values()), default=1.0) or 1.0
    fig_radar = go.Figure()
    for idx, (model, vals) in enumerate(model_metrics.items()):
        r_vals = [
            vals["bert_f1"],
            vals["determinism"],
            vals["tokens_per_second"] / max_tps,
            vals["judge_mean"] / 10.0,
            vals["judge_if_mean"] / 10.0,
        ]
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals + [r_vals[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=_label(model),
            line=dict(color=MODEL_COLORS[idx % len(MODEL_COLORS)]),
            fillcolor=MODEL_COLORS[idx % len(MODEL_COLORS)].replace(")", ", 0.15)").replace("rgb", "rgba") if MODEL_COLORS[idx % len(MODEL_COLORS)].startswith("rgb") else MODEL_COLORS[idx % len(MODEL_COLORS)] + "26",
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], gridcolor="#E2E8F0"), angularaxis=dict(gridcolor="#E2E8F0")),
        showlegend=True,
        **CHART_LAYOUT,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # --- Category breakdown ---
    st.subheader("Category Breakdown")
    cat_data = _aggregate_by_category(run_id, conn)
    cat_rows = []
    for model, cats in cat_data.items():
        for cat, vals in cats.items():
            cat_rows.append({
                "Model": _label(model),
                "Category": CATEGORY_DISPLAY.get(cat, cat),
                "BERTScore F1": round(vals["bert_f1"], 3) if vals["bert_f1"] is not None else None,
                "Judge Score": round(vals["judge_mean"] / 10.0, 3) if vals["judge_mean"] is not None else None,
            })
    cat_df = pd.DataFrame(cat_rows)

    tab_bert, tab_judge = st.tabs(["BERTScore F1 by Category", "Judge Score by Category"])
    with tab_bert:
        fig_cat_bert = px.bar(
            cat_df.dropna(subset=["BERTScore F1"]),
            x="Category", y="BERTScore F1", color="Model", barmode="group",
            range_y=[0, 1], color_discrete_sequence=MODEL_COLORS,
        )
        fig_cat_bert.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_cat_bert, use_container_width=True)
    with tab_judge:
        fig_cat_judge = px.bar(
            cat_df.dropna(subset=["Judge Score"]),
            x="Category", y="Judge Score", color="Model", barmode="group",
            range_y=[0, 1], color_discrete_sequence=MODEL_COLORS,
        )
        fig_cat_judge.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_cat_judge, use_container_width=True)

    st.markdown("---")

    # --- Metric bar charts ---
    st.subheader("Metric Comparison")
    cols = st.columns(3)
    bar_specs = [
        ("BERTScore F1", "bert_f1", 1.0),
        ("Judge Score (normalized)", "judge_mean", 10.0),
        ("Determinism", "determinism", 1.0),
    ]
    for col, (label, key, divisor) in zip(cols, bar_specs):
        df = pd.DataFrame([{"Model": _label(m), label: vals[key] / divisor} for m, vals in model_metrics.items()])
        fig = px.bar(df, x="Model", y=label, title=label, range_y=[0, 1], color="Model",
                     color_discrete_sequence=MODEL_COLORS)
        fig.update_layout(**CHART_LAYOUT, showlegend=False)
        col.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Raw responses viewer ---
    st.subheader("Raw Responses")
    responses = get_responses_for_run(conn, run_id)
    prompt_ids = sorted({r["prompt_id"] for r in responses})
    if prompt_ids:
        selected_prompt_id = st.selectbox("Select prompt", prompt_ids)
        prompt_responses = [r for r in responses if r["prompt_id"] == selected_prompt_id and r["repeat_index"] == 0]
        models_in_run = sorted({r["model"] for r in prompt_responses})

        all_prompts = {p.id: p for p in load_prompts(prompts_dir=PROMPTS_DIR)}
        prompt_obj = all_prompts.get(selected_prompt_id)
        if prompt_obj:
            st.info(f"**Prompt:** {prompt_obj.prompt}")
            with st.expander("Reference answer"):
                st.write(prompt_obj.reference)

        if models_in_run:
            cols = st.columns(len(models_in_run))
            for idx, (col, model) in enumerate(zip(cols, models_in_run)):
                resp = next((r for r in prompt_responses if r["model"] == model), None)
                with col:
                    color = MODEL_COLORS[idx % len(MODEL_COLORS)]
                    st.markdown(f"<p style='color:{color};font-weight:700;font-size:15px'>{_label(model)}</p>", unsafe_allow_html=True)
                    if resp:
                        st.text_area(
                            label="response",
                            value=resp["output"],
                            height=300,
                            key=f"resp_{model}_{selected_prompt_id}",
                            disabled=True,
                            label_visibility="collapsed",
                        )
                    else:
                        st.caption("No response recorded")

    st.markdown("---")

    # --- Export ---
    st.subheader("Export")
    st.download_button(
        "⬇️ Download Responses CSV",
        pd.DataFrame(responses).to_csv(index=False),
        "responses.csv",
        "text/csv",
    )
