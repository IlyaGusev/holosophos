.PHONY: black style validate test install serve

install:
	uv pip install -e .[dev]

black:
	uv run black holosophos --line-length 100
	uv run black tests --line-length 100

validate:
	uv run black holosophos --line-length 100
	uv run black tests --line-length 100
	uv run flake8 holosophos
	uv run flake8 tests
	uv run mypy holosophos --strict --explicit-package-bases
	uv run mypy tests --strict --explicit-package-bases

test:
	uv run pytest -s