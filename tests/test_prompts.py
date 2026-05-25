import yaml
import pytest
from runner.prompts import load_prompts, Prompt


@pytest.fixture
def prompt_dir(tmp_path):
    data = {
        "prompts": [
            {"id": "t1", "category": "code_generation", "prompt": "Write hello", "reference": "print('hi')", "tags": ["python"]},
            {"id": "t2", "category": "logical_reasoning", "prompt": "2+2?", "reference": "4", "tags": []},
        ]
    }
    (tmp_path / "test.yaml").write_text(yaml.dump(data))
    return tmp_path


def test_load_all_prompts(prompt_dir):
    prompts = load_prompts(prompts_dir=prompt_dir)
    assert len(prompts) == 2
    assert all(isinstance(p, Prompt) for p in prompts)


def test_filter_by_category(prompt_dir):
    prompts = load_prompts(categories=["code_generation"], prompts_dir=prompt_dir)
    assert len(prompts) == 1
    assert prompts[0].id == "t1"


def test_prompt_fields(prompt_dir):
    prompts = load_prompts(prompts_dir=prompt_dir)
    p = next(x for x in prompts if x.id == "t1")
    assert p.prompt == "Write hello"
    assert p.reference == "print('hi')"
    assert p.tags == ["python"]
