.PHONY: help setup start stop restart logs test test-cov migrate migrate-create clean

DOCKER_COMPOSE = docker-compose
PYTHON = ./venv/bin/python
PYTEST = ./venv/bin/pytest
ALEMBIC = ./venv/bin/alembic

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup: ## First-time setup (copy .env, install deps, build)
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ .env created"; fi
	@python3 -m venv venv
	@$(PYTHON) -m pip install -r requirements.txt -q
	@$(DOCKER_COMPOSE) build
	@echo "✅ Setup complete! Run 'make start'"

start: ## Start containers
	@$(DOCKER_COMPOSE) up -d
	@echo "✅ Started! API: http://localhost:8000/docs"

stop: ## Stop containers
	@$(DOCKER_COMPOSE) stop

restart: ## Restart containers
	@$(DOCKER_COMPOSE) restart

logs: ## Show logs
	@$(DOCKER_COMPOSE) logs -f

migrate: ## Run database migrations
	@$(ALEMBIC) upgrade head

migrate-create: ## Create new migration (make migrate-create MSG="message")
	@$(ALEMBIC) revision --autogenerate -m "$(MSG)"

test: ## Run tests
	@$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage
	@$(PYTEST) tests/ --cov=app --cov-report=html
	@echo "✅ Coverage report: htmlcov/index.html"

clean: ## Clean cache files
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@rm -f .coverage celerybeat-schedule* 2>/dev/null || true
	@echo "✅ Cleaned"

.DEFAULT_GOAL := help

