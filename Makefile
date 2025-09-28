.PHONY: install black validate test

install:
	uv pip install -e .[dev]

black:
	uv run black holosophos tests reports --line-length 100

validate:
	uv run black holosophos tests reports --line-length 100
	uv run flake8 holosophos tests reports
	uv run mypy holosophos tests reports --strict --explicit-package-bases

test:
	uv run pytest -s
