# app.py
import streamlit as st

st.set_page_config(page_title="LLM Evaluator", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    ["Run Benchmarks", "Dashboard", "Prompt Editor"],
)

if page == "Run Benchmarks":
    from views.run import show
    show()
elif page == "Dashboard":
    from views.dashboard import show
    show()
elif page == "Prompt Editor":
    from views.prompts import show
    show()
