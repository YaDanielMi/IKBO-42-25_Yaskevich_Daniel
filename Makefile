.PHONY: run test lint

run:
	python3 src/main.py

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

lint:
	flake8 --max-line-length=80 --max-complexity=10 src tests
