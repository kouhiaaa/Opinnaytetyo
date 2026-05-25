# pages/run.py
import streamlit as st
from db.schema import init_db
from runner.runner import run_benchmark

MODELS = ["llama3", "qwen:7b", "mistral"]
CATEGORIES = ["code_generation", "code_debugging", "logical_reasoning", "instruction_following", "general_quality"]


def show():
    st.header("Run Benchmarks")

    selected_models = st.multiselect("Models", MODELS, default=MODELS)
    selected_categories = st.multiselect("Categories", CATEGORIES, default=CATEGORIES)
    n_repeats = st.slider("Repeats per prompt (for determinism)", min_value=1, max_value=10, value=3)

    if st.button("Run", disabled=not selected_models or not selected_categories):
        conn = init_db()
        progress_bar = st.progress(0)
        status = st.empty()

        def on_progress(step, total, message):
            progress_bar.progress(step / total)
            status.text(f"[{step}/{total}] {message}")

        with st.spinner("Running benchmark — this may take several minutes..."):
            run_id = run_benchmark(
                conn=conn,
                models=selected_models,
                categories=selected_categories,
                n_repeats=n_repeats,
                on_progress=on_progress,
            )

        progress_bar.progress(1.0)
        status.text("Done!")
        st.success(f"Run #{run_id} complete. Open the Dashboard to see results.")
        st.session_state["last_run_id"] = run_id
