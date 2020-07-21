tidyup:	
	autoflake --recursive . --remove-all-unused-imports --remove-unused-variables --in-place 
	isort **/*.py
	black .
	find . -name "*~" -type f -delete

test:
	pytest api/tests stream_app/tests --cov=api --cov stream_app

testpudb:
	pytest api/tests/ --pudb

testreport:
	pytest --cov-report html:docs/api_coverage --cov=api --cov stream_app api/tests stream_app/tests

coveralls:
	coverage run --source api,stream_app -m pytest api/tests stream_app/tests
	coveralls

erdiagram:
	eralchemy -i postgres:///chess_api_project -o docs/chess_api.pdf

openemacs:
	emacs api api/views.py &

makemigrations:
	./manage.py makemigrations

migrate:
	./manage.py migrate
