from typing import Any, Dict

import yaml
from jinja2 import Template

from holosophos.files import PROMPTS_DIR_PATH


def get_prompt(template_name: str) -> Dict[str, Any]:
    template_path = PROMPTS_DIR_PATH / f"{template_name}.yaml"
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    templates: Dict[str, Any] = yaml.safe_load(template)
    return templates


def render_prompt(prompt: str, **kwargs: Any) -> str:
    template = Template(prompt)
    return template.render(**kwargs).strip() + "\n"
