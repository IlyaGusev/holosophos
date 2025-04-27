from typing import Callable, Any

from smolagents.tools import tool, Tool  # type: ignore

from holosophos.tools.arxiv_search import arxiv_search
from holosophos.tools.anthology_search import anthology_search
from holosophos.tools.arxiv_download import arxiv_download
from holosophos.tools.bash import bash
from holosophos.tools.text_editor import text_editor
from holosophos.tools.document_qa import DocumentQATool
from holosophos.tools.visit_webpage import CustomVisitWebpageTool
from holosophos.tools.remote_gpu import (
    remote_bash,
    create_remote_text_editor,
    remote_download,
)
from holosophos.tools.hf_datasets_search import hf_datasets_search
from holosophos.tools.s2_citations import s2_citations
from holosophos.tools.latex_conversion import md_to_pdf


def convert_tool_to_smolagents(function: Callable[..., Any]) -> Tool:
    return tool(function)


remote_text_editor = create_remote_text_editor(text_editor)

arxiv_search_tool = convert_tool_to_smolagents(arxiv_search)
arxiv_download_tool = convert_tool_to_smolagents(arxiv_download)
anthology_search_tool = convert_tool_to_smolagents(anthology_search)
bash_tool = convert_tool_to_smolagents(bash)
text_editor_tool = convert_tool_to_smolagents(text_editor)
remote_bash_tool = convert_tool_to_smolagents(remote_bash)
remote_download_tool = convert_tool_to_smolagents(remote_download)
remote_text_editor_tool = convert_tool_to_smolagents(remote_text_editor)
hf_datasets_search_tool = convert_tool_to_smolagents(hf_datasets_search)
s2_citations_tool = convert_tool_to_smolagents(s2_citations)
md_to_pdf_tool = convert_tool_to_smolagents(md_to_pdf)

__all__ = [
    "arxiv_search",
    "arxiv_download",
    "anthology_search",
    "convert_tool_to_smolagents",
    "DocumentQATool",
    "CustomVisitWebpageTool",
    "bash",
    "text_editor",
    "arxiv_search_tool",
    "arxiv_download_tool",
    "anthology_search_tool",
    "bash_tool",
    "text_editor_tool",
    "remote_bash",
    "remote_download",
    "remote_text_editor",
    "remote_bash_tool",
    "remote_text_editor_tool",
    "remote_download_tool",
    "hf_datasets_search",
    "hf_datasets_search_tool",
    "s2_citations",
    "s2_citations_tool",
    "md_to_pdf",
    "md_to_pdf_tool",
]
