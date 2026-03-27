.PHONY = run analyze 

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

ALOG := $(ROOT_DIR)/analysis.log

run:
# TODO: Fix file handling to allow execution from root of project
	cd src/backend && ../../.venv/bin/python3 app.py &
	cd src/frontend && npm run dev

analyze:
	echo "Running mypy over backend" > $(ALOG)
	cd src/backend && ../../.venv/bin/mypy *.py >> $(ALOG)

	echo "Running bandit over backend >>" $(ALOG)
	cd src/backend && ../../.venv/bin/bandit -r *.py --severity-level=high >> $(ALOG)