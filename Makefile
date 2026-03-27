.PHONY = run analyze mypy bandit pylint flow eslint cleanLog

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

ALOG := $(ROOT_DIR)/analysis.log

run:
# TODO: Fix file handling to allow execution from root of project
	cd src/backend && ../../.venv/bin/python3 app.py &
	cd src/frontend && npm run dev

analyze: pylint mypy bandit eslint flow cleanLog

cleanLog:
	> /path/to/logfile
	
mypy:
	echo "Running mypy over backend" >> $(ALOG)
	cd src/backend && ../../.venv/bin/mypy *.py >> $(ALOG)
bandit:
	echo "Running bandit over backend >>" $(ALOG)
	cd src/backend && ../../.venv/bin/bandit -r *.py --severity-level=high >> $(ALOG)
pylint:
	echo "Running pylint over backend >>" $(ALOG)
	cd src/backend && ../../.venv/bin/pylint *.py >> $(ALOG)
flow:
	echo "Running flow on frontend" >> $(ALOG)
	npm run flow
eslint:
	echo "Running ESLint on frontend" >> $(ALOG)
	npx eslint src/frontend/src/pages/*.jsx >> $(ALOG)
	npx eslint src/frontend/src/*.jsx >> $(ALOG)