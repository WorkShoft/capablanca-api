tidyup:
	isort **/*.py
	autoflake --recursive . --remove-all-unused-imports --in-place
	black .
	find . -name "*~" -type f -delete

test:
	pytest --cov-report html:docs/api_coverage --cov=api api/tests/

erdiagram:
	eralchemy -i postgres:///chess_api_project -o docs/chess_api.pdf

openemacs:
	emacs api api/views.py &

makemigrations:
	./manage.py makemigrations

migrate:
	./manage.py migrate
