from dataclasses import dataclass, field
from pathlib import Path
import yaml

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@dataclass
class Prompt:
    id: str
    category: str
    prompt: str
    reference: str
    tags: list = field(default_factory=list)


def load_prompts(categories: list = None, prompts_dir: Path = None) -> list:
    base = prompts_dir or PROMPTS_DIR
    prompts = []
    for path in sorted(base.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for item in data.get("prompts", []):
            p = Prompt(
                id=item["id"],
                category=item["category"],
                prompt=item["prompt"],
                reference=item.get("reference", ""),
                tags=item.get("tags", []),
            )
            if categories is None or p.category in categories:
                prompts.append(p)
    return prompts
