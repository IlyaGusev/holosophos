import json
import re
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from acl_anthology import Anthology

SORT_BY_OPTIONS = ("relevance", "published")
SORT_ORDER_OPTIONS = ("ascending", "descending")

def _format_text_field(text: str) -> str:
    return " ".join([line.strip() for line in text.split() if line.strip()])

def _format_authors(authors: List[Any]) -> str:
    names = [f'{author.name.first} {author.name.last}' for author in authors]
    result = ", ".join(names[:3])
    if len(names) > 3:
        result += f", and {len(names) - 3} more authors"
    return result

def _format_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y").strftime("%B %d, %Y")
    except ValueError:
        return date_str

def _clean_entry(entry: Any) -> Dict[str, Any]:
    return {
        "id": entry.full_id,
        "title": _format_text_field(entry.title.as_text()),
        "authors": _format_authors(entry.authors),
        "abstract": _format_text_field(entry.abstract.as_text()) if entry.abstract else "",
        "published": _format_date(entry.year),
        "categories": ", ".join(entry.venue_ids),
        "comment": entry.note if entry.note else "",
        "url": entry.pdf.url if entry.pdf else ""
    }

def _convert_to_year(date_str: str) -> int:
    try:
        return int(date_str[:4])
    except ValueError as e:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD format.") from e

def _has_cyrillic(text: str) -> bool:
    return bool(re.search("[а-яА-Я]", text))

def _parse_query(query: str, paper: Any) -> bool:
    conditions = re.split(r"\s+(AND|OR|ANDNOT)\s+", query)
    result = False
    for i in range(0, len(conditions), 2):
        condition = conditions[i]
        field, value = condition.split(":", 1) if ":" in condition else ("ti", condition)
        value = value.lower().replace('"', '').replace("'", "")
        match field:
            case "ti":
                match_found = value in paper.title.as_text().lower()
            case "au":
                match_found = any(value in str(author).lower() for author in paper.authors)
            case "abs":
                match_found = paper.abstract and value in paper.abstract.as_text().lower()
            case "cat":
                match_found = any(value in cat.lower() for cat in paper.venue_ids)
            case "id":
                match_found = value in paper.full_id.lower()
            case _:
                match_found = False
        if i == 0:
            result = match_found
        else:
            operator = conditions[i - 1]
            if operator == "AND":
                result = result and match_found
            elif operator == "OR":
                result = result or match_found
            elif operator == "ANDNOT":
                result = result and not match_found
    return result

def anthology_search(
    query: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 5,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = "relevance",
    sort_order: Optional[str] = "descending",
    include_abstracts: Optional[bool] = False,
) -> str:
    assert isinstance(query, str), "Error: Your search query must be a string"
    assert isinstance(offset, int), "Error: offset should be an integer"
    assert isinstance(limit, int), "Error: limit should be an integer"
    assert isinstance(sort_by, str), "Error: sort_by should be a string"
    assert isinstance(sort_order, str), "Error: sort_order should be a string"
    assert query.strip(), "Error: Your query should not be empty"
    assert sort_by in SORT_BY_OPTIONS, f"Error: sort_by should be one of {SORT_BY_OPTIONS}"
    assert sort_order in SORT_ORDER_OPTIONS, f"Error: sort_order should be one of {SORT_ORDER_OPTIONS}"
    assert offset >= 0, "Error: offset must be 0 or positive number"
    assert limit < 100, "Error: limit is too large, it should be less than 100"
    assert limit > 0, "Error: limit should be greater than 0"
    assert not _has_cyrillic(query), "Error: use only Latin script for queries"
    assert include_abstracts is not None, "Error: include_abstracts must be bool"

    anthology = Anthology.from_repo()
    anthology.load_all()
    all_papers = list(anthology.papers())
    all_papers = [paper for paper in all_papers if paper.abstract and str(paper.abstract).strip()]

    if start_date or end_date:
        start_year = _convert_to_year(start_date) if start_date else 1900
        end_year = _convert_to_year(end_date) if end_date else datetime.now().year
        all_papers = [paper for paper in all_papers if start_year <= int(paper.year) <= end_year]

    filtered_papers = [paper for paper in all_papers if _parse_query(query, paper)]

    if sort_by == "published":
        filtered_papers.sort(key=lambda x: int(x.year), reverse=(sort_order == "descending"))
    
    paged_papers = filtered_papers[offset: offset + limit]
    clean_entries = [_clean_entry(entry) for entry in paged_papers]
    
    return json.dumps(
        {
            "total_count": len(filtered_papers),
            "returned_count": len(paged_papers),
            "offset": offset,
            "results": clean_entries,
        },
        ensure_ascii=False,
    )
