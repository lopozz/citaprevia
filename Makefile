.PHONY: quality style

quality:
	ruff check .
	ruff format --check .

style:
	ruff format .
	ruff check --fix .

pip-solve:
	pip install --upgrade pip
	pip-compile
	pip install -r requirements.txt