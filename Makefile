.PHONY: help easy-start setup start stop restart logs test test-cov migrate migrate-create clean

DOCKER_COMPOSE = docker-compose
PYTHON = ./venv/bin/python
PYTEST = ./venv/bin/pytest
ALEMBIC = ./venv/bin/alembic

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

easy-start: ## Complete setup and start (Docker-based, one command!)
	@echo "🚀 Easy Start - Setting up everything..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ .env created"; fi
	@$(DOCKER_COMPOSE) up -d --build
	@echo "⏳ Waiting for services to be ready..."
	@sleep 8
	@$(DOCKER_COMPOSE) exec -T app alembic upgrade head
	@echo ""
	@echo "🎉 All done! Application is running!"
	@echo "📌 API Docs: http://localhost:8000/docs"
	@echo "📌 Health: http://localhost:8000/health"
	@echo "📌 Flower: http://localhost:5555"

setup: ## Setup for local testing (creates venv, installs test deps)
	@python3 -m venv venv
	@$(PYTHON) -m pip install -r requirements.txt -q
	@echo "✅ Local environment ready for testing"

start: ## Start containers
	@$(DOCKER_COMPOSE) up -d
	@echo "✅ Started! API: http://localhost:8000/docs"

dev-services: ## Start only services (for local PyCharm debug)
	@$(DOCKER_COMPOSE) up -d postgres redis rabbitmq celery-worker celery-beat
	@echo "✅ Services started (postgres, redis, rabbitmq, celery)"
	@echo "💡 Now run app locally: make dev-app"

dev-app: ## Run app locally (after dev-services)
	@echo "🔥 Starting app locally on port 8000..."
	@$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

stop: ## Stop containers
	@$(DOCKER_COMPOSE) stop

restart: ## Restart containers
	@$(DOCKER_COMPOSE) restart

logs: ## Show logs
	@$(DOCKER_COMPOSE) logs -f

migrate: ## Run database migrations (Docker-based)
	@$(DOCKER_COMPOSE) exec -T app alembic upgrade head

migrate-create: ## Create new migration (make migrate-create MSG="message")
	@$(DOCKER_COMPOSE) exec -T app alembic revision --autogenerate -m "$(MSG)"

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

