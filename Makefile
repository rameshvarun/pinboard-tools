format:
	pipenv run black *.py

typecheck:
	pipenv run mypy *.py
