# app.py
import streamlit as st

st.set_page_config(page_title="LLM Evaluator", layout="wide")

page = st.sidebar.radio(
    "Navigation",
    ["Run Benchmarks", "Dashboard", "Prompt Editor"],
)

if page == "Run Benchmarks":
    from pages.run import show
    show()
elif page == "Dashboard":
    from pages.dashboard import show
    show()
elif page == "Prompt Editor":
    from pages.prompts import show
    show()
