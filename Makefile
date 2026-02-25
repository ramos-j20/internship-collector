.PHONY: up down logs scrape migrate restart build

# Start all services in detached mode
up:
	docker-compose up -d

# Stop all services and remove containers
down:
	docker-compose down

# View logs for all services (or specify service e.g., make logs service=api)
logs:
	docker-compose logs -f $(service)

# Trigger manual scrape via Celery or API (example implementation)
scrape:
	docker-compose exec worker celery -A src.worker.app call src.tasks.run_full_scraping_pipeline

# Run database migrations
migrate:
	docker-compose exec api alembic upgrade head

# Rebuild images
build:
	docker-compose build

# Restart all services
restart:
	docker-compose restart
