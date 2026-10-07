# ==============================================================================
# UdyamNiti Developer & Judge Convenience Makefile
# ==============================================================================

.PHONY: help up up-d down restart build logs logs-backend logs-frontend logs-celery \
        seed migrate wait-for-db shell-backend shell-frontend shell-db shell-redis \
        test test-backend test-frontend test-e2e reset clean

help:
	@echo "======================================================================"
	@echo "                      UdyamNiti CLI Shortcuts                         "
	@echo "======================================================================"
	@echo "  make up            : Start all services in the foreground"
	@echo "  make up-d          : Start all services in detached (background) mode"
	@echo "  make build         : Build or rebuild container images and start"
	@echo "  make down          : Stop all running containers"
	@echo "  make restart       : Restart all running containers"
	@echo "  make logs          : Stream logs from all running services"
	@echo "  make logs-backend  : Stream logs from Django API"
	@echo "  make logs-frontend : Stream logs from React Vite frontend"
	@echo "  make logs-celery   : Stream logs from Celery async worker"
	@echo "  make seed          : Re-run statutory scheme & ABC Engineering seed data"
	@echo "  make migrate       : Apply Django database schema migrations"
	@echo "  make shell-backend : Open an interactive Django shell"
	@echo "  make shell-db      : Connect to PostgreSQL with psql"
	@echo "  make test          : Run backend and frontend automated test suites"
	@echo "  make reset         : Wipe volumes and cleanly rebuild from scratch"
	@echo "======================================================================"

# Start all services with logs attached
up:
	docker-compose up

# Start in background (detached)
up-d:
	docker-compose up -d

# Build images and start
build:
	docker-compose up --build

# Stop all services gracefully
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# Stream logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-celery:
	docker-compose logs -f celery

logs-minio:
	docker-compose logs -f minio

# Database and Seed Data Operations
seed:
	docker-compose exec backend python manage.py seed_data

migrate:
	docker-compose exec backend python manage.py migrate

wait-for-db:
	docker-compose exec backend python manage.py wait_for_db

# Interactive Shells
shell-backend:
	docker-compose exec backend python manage.py shell

shell-frontend:
	docker-compose exec frontend sh

shell-db:
	docker-compose exec db psql -U udyamniti -d udyamniti

shell-redis:
	docker-compose exec redis redis-cli

# Test Suites
test: test-backend test-frontend

test-backend:
	docker-compose exec backend pytest -v

test-frontend:
	docker-compose exec frontend npm run test

# Complete Clean Reset (Deletes persistent volumes and restarts)
reset:
	docker-compose down -v
	docker-compose up --build

# Clean temporary Python cache artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
