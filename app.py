import streamlit as st

st.set_page_config(
    page_title="LLM Evaluator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Sidebar branding */
[data-testid="stSidebar"] {
    background-color: #1E293B;
}
[data-testid="stSidebar"] * {
    color: #F1F5F9 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    padding: 4px 0;
}

/* Hide only the menu and footer, keep the sidebar toggle */
#MainMenu, footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}

/* Background dot grid */
.stApp {
    background-color: #F1F5F9;
    background-image: radial-gradient(#CBD5E1 1px, transparent 1px);
    background-size: 22px 22px;
}

/* Main content card */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    border-radius: 16px;
}

/* Page headers */
h1 { color: #1E293B; font-weight: 700; }
h2 { color: #334155; font-weight: 600; }
h3 { color: #475569; font-weight: 600; }

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 13px;
    color: #64748B;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 700;
    color: #1E293B;
}

/* Buttons */
.stButton > button {
    background-color: #6366F1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    transition: background-color 0.2s;
}
.stButton > button:hover {
    background-color: #4F46E5;
    color: white;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 500;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}

/* Selectbox / multiselect */
[data-baseweb="select"] {
    border-radius: 8px !important;
}

/* Progress bar */
.stProgress > div > div {
    background-color: #6366F1;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🧠 LLM Evaluator")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Run Benchmarks", "Dashboard", "Prompt Editor"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Llama 3 · Qwen 2.5 · Mistral")
    st.caption("Thesis project · Savonia AMK")

if page == "Run Benchmarks":
    from views.run import show
    show()
elif page == "Dashboard":
    from views.dashboard import show
    show()
elif page == "Prompt Editor":
    from views.prompts import show
    show()
