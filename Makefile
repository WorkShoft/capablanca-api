tidyup:
	isort **/*.py
	autoflake --recursive . --remove-all-unused-imports --in-place
	black .
	find . -name "*~" -type f -delete
