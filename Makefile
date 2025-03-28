.PHONY: black style validate test

black:
	black .

validate:
	black . --exclude "./workdir/*"
	flake8 . --exclude "./workdir/*"
	mypy . --strict --explicit-package-bases --exclude "./workdir/*"
