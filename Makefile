.PHONY = run analyze 

run:
# TODO: Fix file handling to allow execution from root of project
	cd src/backend && ../../.venv/bin/python3 app.py &
	cd src/frontend && npm run dev

analyze:
	cd src/backend && ../../.venv/bin/mypy *.py