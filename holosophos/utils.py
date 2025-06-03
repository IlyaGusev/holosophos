from pathlib import Path
from typing import Any, Optional, Dict, List

import yaml
import requests
from pypdf import PdfReader

from holosophos.files import PROMPTS_DIR_PATH


def get_prompt(template_name: str) -> Dict[str, Any]:
    template_path = PROMPTS_DIR_PATH / f"{template_name}.yaml"
    with open(template_path) as f:
        template = f.read()
    templates: Dict[str, Any] = yaml.safe_load(template)
    return templates


def truncate_content(
    content: str,
    max_length: int,
    prefix_only: bool = False,
    suffix_only: bool = False,
    target_line: Optional[int] = None,
) -> str:
    assert int(prefix_only) + int(suffix_only) + int(target_line is not None) <= 1
    disclaimer = (
        f"\n\n..._This content has been truncated to stay below {max_length} characters_...\n\n"
    )
    half_length = max_length // 2
    if len(content) <= max_length:
        return content

    if prefix_only:
        prefix = content[:max_length]
        return prefix + disclaimer

    elif suffix_only:
        suffix = content[-max_length:]
        return disclaimer + suffix

    elif target_line:
        line_start_pos = 0
        next_pos = content.find("\n") + 1
        line_end_pos = next_pos
        for _ in range(target_line):
            next_pos = content.find("\n", next_pos) + 1
            line_start_pos = line_end_pos
            line_end_pos = next_pos
        assert line_end_pos >= line_start_pos
        length = line_end_pos - line_start_pos
        remaining_length = max(0, max_length - length)
        half_length = remaining_length // 2
        start = max(0, line_start_pos - half_length)
        end = min(len(content), line_end_pos + half_length)
        final_content = content[start:end]
        if start == 0:
            return final_content + disclaimer
        elif end == len(content):
            return disclaimer + final_content
        return disclaimer + content[start:end] + disclaimer

    prefix = content[:half_length]
    suffix = content[-half_length:]
    return prefix + disclaimer + suffix


def download_pdf(url: str, output_path: Path) -> None:
    response = requests.get(url)
    response.raise_for_status()
    content_type = response.headers.get("content-type")
    assert content_type
    assert "application/pdf" in content_type.lower()
    with open(output_path.resolve(), "wb") as fp:
        fp.write(response.content)


def parse_pdf_file(pdf_path: Path) -> List[str]:
    # Why not Marker? Because it is too heavy.
    reader = PdfReader(str(pdf_path.resolve()))

    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
            prefix = f"## Page {page_number}\n\n"
            pages.append(prefix + text)
        except Exception:
            continue
    return pages
