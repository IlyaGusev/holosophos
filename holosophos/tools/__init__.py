from typing import Callable, Any

from smolagents.tools import tool, Tool  # type: ignore

from holosophos.tools.arxiv_search import arxiv_search
from holosophos.tools.anthology_search import anthology_search
from holosophos.tools.arxiv_download import arxiv_download
from holosophos.tools.bash import bash
from holosophos.tools.text_editor import text_editor
from holosophos.tools.document_qa import DocumentQATool
from holosophos.tools.visit_webpage import CustomVisitWebpageTool


def convert_tool_to_smolagents(function: Callable[..., Any]) -> Tool:
    return tool(function)


arxiv_search_tool = convert_tool_to_smolagents(arxiv_search)
arxiv_download_tool = convert_tool_to_smolagents(arxiv_download)
anthology_search_tool = convert_tool_to_smolagents(anthology_search)
bash_tool = convert_tool_to_smolagents(bash)
text_editor_tool = convert_tool_to_smolagents(text_editor)

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
]
