# SuperScout Makefile
# ─────────────────────────────────────────────────────────────────────────────
# Convenience commands for development.
# Run from the superscout/ root directory.
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help install-backend install-frontend dev-backend dev-frontend \
        test-backend build-frontend docker-up docker-down docker-logs clean

# Default target
help: ## Show this help message
	@echo ""
	@echo "  SuperScout — Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────────────
install-backend: ## Install Python backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install Node.js frontend dependencies
	cd frontend && npm install

install: install-backend install-frontend ## Install all dependencies

# ── Development ───────────────────────────────────────────────────────────────
dev-backend: ## Start the FastAPI backend (hot reload)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start the Next.js frontend (dev mode)
	cd frontend && npm run dev

# ── Testing ───────────────────────────────────────────────────────────────────
test-backend: ## Run backend tests
	cd backend && pytest tests/ -v

test: test-backend ## Run all tests

# ── Build ─────────────────────────────────────────────────────────────────────
build-frontend: ## Build the Next.js frontend for production
	cd frontend && npm run build

# ── Docker ────────────────────────────────────────────────────────────────────
docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-up-build: ## Build and start all services with Docker Compose
	docker-compose up -d --build

docker-down: ## Stop all Docker Compose services
	docker-compose down

docker-logs: ## Follow Docker Compose logs
	docker-compose logs -f

docker-db: ## Start only the PostgreSQL database
	docker-compose up db -d

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean: ## Remove Python caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
