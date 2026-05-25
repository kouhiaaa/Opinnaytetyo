from bert_score import score as _bert_score


def tokens_per_second(token_count: int, total_ms: float) -> float:
    if total_ms == 0:
        return 0.0
    return token_count / (total_ms / 1000)


def compute_bert_score(outputs: list, references: list) -> list:
    P, R, F1 = _bert_score(outputs, references, lang="en", verbose=False)
    return [
        {"bert_precision": float(p), "bert_recall": float(r), "bert_f1": float(f)}
        for p, r, f in zip(P.tolist(), R.tolist(), F1.tolist())
    ]


def compute_determinism(outputs: list) -> float:
    if len(outputs) < 2:
        return 1.0
    _, _, F1 = _bert_score(outputs[:-1], outputs[1:], lang="en", verbose=False)
    return float(F1.mean())
