# Local LLM Evaluator

A Streamlit benchmarking app that evaluates three local LLMs across five task categories using BERTScore, latency, determinism, and LLM-as-judge scoring. Built as part of a thesis project.

## Models evaluated

| Model | Ollama tag |
|---|---|
| Llama 3 8B | `llama3:8b-instruct-q4_K_M` |
| Qwen 2.5 7B | `qwen2.5:7b-instruct-q4_K_M` |
| Mistral 7B | `mistral:7b-instruct-q4_K_M` |

## Evaluation categories

- **Code generation** — generate working code for described tasks
- **Code debugging** — identify and fix bugs in provided snippets
- **Logical reasoning** — multi-step logic and math problems
- **Instruction following** — tasks with verifiable format requirements
- **General quality** — open-ended tasks measuring coherence and fluency

## Metrics

- **BERTScore F1** — semantic similarity vs. reference answers
- **Determinism** — consistency across N repeated runs of the same prompt
- **LLM-as-judge** — cross-judging: each model scores the other two (self-scores excluded)
- **Latency** — time to first token and tokens per second
- **Composite score** — weighted average of all metrics

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- ~15 GB free disk space (model weights)
- ~6 GB free RAM (for CPU inference) or ~5 GB free VRAM (for GPU)

---

## Setup

### 1. Install Ollama

Download and install from [ollama.com](https://ollama.com), then start the server:

```bash
ollama serve
```

### 2. Pull the models

```bash
ollama pull llama3:8b-instruct-q4_K_M
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull mistral:7b-instruct-q4_K_M
```

This downloads ~14 GB total. It only needs to be done once.

### 3. Clone the repo

```bash
git clone https://github.com/kouhiaaa/Opinnaytetyo.git
cd Opinnaytetyo
```

### 4. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** This installs PyTorch and `bert-score`, which together download ~500 MB the first time BERTScore runs (the `roberta-large` model). Subsequent runs use the cached version.

### 6. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage

### Running a benchmark

1. Go to **Run Benchmarks** in the sidebar
2. Select which models and categories to include
3. Set the number of repeats per prompt (default 3 — used for determinism scoring)
4. Click **Run**

A full run across all 3 models, 5 categories, and 3 repeats takes roughly 30–90 minutes depending on your hardware. Results are saved to `results.db` (SQLite) and persist between sessions.

### Viewing results

Go to **Dashboard** to see:
- Leaderboard with composite scores
- Radar chart comparing all metrics
- Category breakdown charts (BERTScore and judge score per category)
- Bar charts for individual metrics
- Raw responses viewer — read what each model actually said for any prompt

### Editing prompts

Go to **Prompt Editor** to view, edit, or add prompts. Changes are saved back to the YAML files in `prompts/`.

---

## Project structure

```
├── app.py                  # Streamlit entry point
├── prompts/                # YAML prompt files, one per category
├── runner/
│   ├── runner.py           # Orchestrates benchmark runs
│   ├── ollama.py           # Ollama API client (streaming)
│   ├── metrics.py          # BERTScore, latency, determinism
│   ├── judge.py            # LLM-as-judge cross-evaluation
│   ├── scores.py           # Composite score computation
│   └── prompts.py          # Prompt file loader
├── db/
│   ├── schema.py           # SQLite table definitions
│   └── store.py            # Read/write helpers
├── views/
│   ├── run.py              # Run Benchmarks page
│   ├── dashboard.py        # Dashboard page
│   └── prompts.py          # Prompt Editor page
└── tests/                  # pytest test suite
```

---

## Running tests

```bash
pytest tests/ -v
```

---

## Troubleshooting

**`ConnectionError` on port 11434**
Ollama is not running. Start it with `ollama serve`.

**`404 Not Found` from Ollama**
The model tag isn't available. Run `ollama list` to check what's installed and `ollama pull <tag>` to download the missing model.

**`500 Internal Server Error` from Ollama**
Usually means not enough VRAM. Close other GPU-heavy applications, or check available memory with `nvidia-smi`. The models need ~5 GB free VRAM each; they will fall back to CPU if GPU memory is unavailable (much slower).

**BERTScore is slow on first run**
The `roberta-large` model (~500 MB) is downloaded the first time. Subsequent runs use the cached version.
