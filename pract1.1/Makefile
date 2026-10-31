.PHONY: run test lint demo

run:
	python3 src/main.py

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

lint:
	flake8 --max-line-length=80 --max-complexity=10 src tests

demo:
	scripts/stage2_params.sh
	scripts/stage2_errors.sh
	scripts/stage2_script_features.sh
	scripts/stage3_vfs_variants.sh
	scripts/stage3_vfs_errors.sh
	scripts/stage3_in_memory.sh
	scripts/stage3_all_commands.sh
