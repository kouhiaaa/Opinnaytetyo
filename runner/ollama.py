import json
import time
from dataclasses import dataclass
from typing import Callable
import requests

OLLAMA_BASE = "http://localhost:11434"


@dataclass
class GenerationResult:
    model: str
    output: str
    ttft_ms: float
    total_ms: float
    token_count: int


def generate(
    model: str,
    prompt: str,
    on_token: Callable[[str], None] = None,
) -> GenerationResult:
    url = f"{OLLAMA_BASE}/api/generate"
    t_start = time.perf_counter()
    ttft_ms = None
    tokens = []

    with requests.post(url, json={"model": model, "prompt": prompt, "stream": True}, stream=True) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("response", "")
            if token:
                if ttft_ms is None:
                    ttft_ms = (time.perf_counter() - t_start) * 1000
                tokens.append(token)
                if on_token:
                    on_token(token)

    total_ms = (time.perf_counter() - t_start) * 1000
    return GenerationResult(
        model=model,
        output="".join(tokens),
        ttft_ms=ttft_ms if ttft_ms is not None else total_ms,
        total_ms=total_ms,
        token_count=len(tokens),
    )
