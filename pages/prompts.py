# pages/prompts.py
import streamlit as st
import yaml
from runner.prompts import load_prompts, PROMPTS_DIR


def _save(prompt_id: str, new_prompt: str, new_reference: str):
    for path in PROMPTS_DIR.glob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for item in data.get("prompts", []):
            if item["id"] == prompt_id:
                item["prompt"] = new_prompt
                item["reference"] = new_reference
                path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
                return


def show():
    st.header("Prompt Editor")
    prompts = load_prompts()
    categories = ["All"] + sorted({p.category for p in prompts})
    selected = st.selectbox("Filter by category", categories)
    filtered = prompts if selected == "All" else [p for p in prompts if p.category == selected]

    st.write(f"{len(filtered)} prompts")
    for p in filtered:
        with st.expander(f"[{p.category}] {p.id}"):
            new_prompt = st.text_area("Prompt", value=p.prompt, key=f"prompt_{p.id}")
            new_ref = st.text_area("Reference answer", value=p.reference, key=f"ref_{p.id}")
            if st.button("Save", key=f"save_{p.id}"):
                _save(p.id, new_prompt, new_ref)
                st.success("Saved.")
                st.rerun()
