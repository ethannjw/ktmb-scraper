# KTMB Scraper Makefile
# Provides easy commands for building and running the scraper with Docker

.PHONY: help build clean run search monitor weekend friday sunday custom schedule-cron schedule-systemd list-jobs remove-job logs shell test

# Default target
help: ## Show this help message
	@echo "KTMB Scraper - Available Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make run-continuous"
	@echo "  make weekend YEAR=2025 MONTH=10 TIMESLOT=evening"

# Build targets
build: ## Build the Docker image
	@echo "Building KTMB scraper Docker image..."
	docker compose build
	@echo "✅ Docker image built successfully!"

build-no-cache: ## Build the Docker image without cache
	@echo "Building KTMB scraper Docker image (no cache)..."
	docker compose build --no-cache
	@echo "✅ Docker image built successfully!"

clean: ## Clean up Docker images and containers
	@echo "Cleaning up Docker resources..."
	docker-compose down --rmi local --volumes
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Run targets
run-continuous:
	@echo "Running KTMB scraper..."
	python -u monitor.py --continuous --interval 60

search-date:
	@echo "🔍 Searching for date: $(DATE), direction: $(DIRECTION)"
	python monitor.py --date $(DATE) --direction $(DIRECTION)

weekend: 
	@echo "🏖️ Searching weekends in year $(YEAR) month $(MONTH) time slot $(TIMESLOT)"
	python monitor.py --weekends --year $(YEAR) --month $(MONTH) --time-slots $(TIMESLOT)
