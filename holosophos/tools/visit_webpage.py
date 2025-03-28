from pathlib import Path

from smolagents.default_tools import VisitWebpageTool  # type: ignore

from holosophos.files import WORKSPACE_DIR_PATH
from holosophos.utils import download_pdf, parse_pdf_file


class CustomVisitWebpageTool(VisitWebpageTool):  # type: ignore
    def forward(self, url: str) -> str:
        if url.endswith(".pdf") or "/pdf/" in url:
            name = url.split("/")[-1]
            pdf_path: Path = WORKSPACE_DIR_PATH / name
            if not pdf_path.exists():
                download_pdf(url, pdf_path)
            pages = parse_pdf_file(pdf_path)
            return "\n\n".join(pages)
        result: str = super().forward(url)
        return result
