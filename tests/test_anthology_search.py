import pytest

from holosophos.tools import anthology_search

def test_anthology_search_basic_search() -> None:
    result = anthology_search('ti:"BERT for NLP"')
    assert isinstance(result, str)
    assert len(result) > 0