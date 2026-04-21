PYTHON=python
PIP=pip
NPM=npm

.PHONY: backend-install frontend-install install migrate backend frontend bootstrap

backend-install:
	$(PIP) install -r "backend/requirements.txt"

frontend-install:
	cd frontend && $(NPM) install

install: backend-install frontend-install

migrate:
	cd backend && alembic -c alembic.ini upgrade head

backend:
	$(PYTHON) -m uvicorn backend.main:app --reload

frontend:
	cd frontend && $(NPM) start

bootstrap: install migrate
	@echo "Dependencies installed and migrations applied."
	@echo "Run backend and frontend in separate terminals."
