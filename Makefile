.DEFAULT_GOAL := req

.PHONY: install
install:
	pip install -r requirements.txt
	pre-commit install

.PHONY: format
format:
	ruff format . --target-version py312

.PHONY: lint
lint:
	ruff check --fix --exit-non-zero-on-fix .

.PHONY: req
req:
	pip freeze > requirements.txt

.PHONY: gen_migration
gen_migration:
	alembic revision --autogenerate -m $(msg)

.PHONY: db_upgrade
db_upgrade:
	alembic upgrade head
