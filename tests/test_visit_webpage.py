from holosophos.tools import CustomVisitWebpageTool


def test_visit_webpage() -> None:
    tool = CustomVisitWebpageTool()
    result = tool("https://example.org/")
    assert "Example Domain" in result


def test_visit_pdf() -> None:
    tool = CustomVisitWebpageTool()
    result = tool("https://aclanthology.org/2024.emnlp-main.695.pdf")
    assert "The Mystery of the Pathological Path-star Task for Language Models" in result
