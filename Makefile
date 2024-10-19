install:
	pip install -r requirements.txt

install-dev: install
	pip install -e ".[dev]"

lint:
	flake8 app tests config

unit:
	pytest -sv tests/unit -p no:warnings

coverage:
	coverage run -m pytest tests/unit --junitxml=build/test.xml -v
	coverage report
	coverage xml -i -o build/coverage.xml

run:
	uvicorn app_loader:app --reload
