PYTHON ?= python3
export PYTHONPATH := src

.PHONY: run test demo compare clean

run:
	$(PYTHON) -m depgraph $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	./run.sh -p express -a -o examples/express.png
	./run.sh -p react -a -o examples/react.png
	./run.sh -p axios -a -o examples/axios.png

compare:
	./scripts/compare.sh $(PKG)

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
