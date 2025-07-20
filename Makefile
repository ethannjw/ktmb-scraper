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
	@echo "  make build"
	@echo "  make search DATE=2025-01-15 DIRECTION=jb_to_sg"
	@echo "  make monitor DATE=2025-01-15 SEATS=2"
	@echo "  make weekend START=2025-01-01 END=2025-01-31"
	@echo "  make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search 2025-01-15 jb_to_sg'"

# Build targets
build: ## Build the Docker image
	@echo "Building KTMB scraper Docker image..."
	docker-compose build
	@echo "✅ Docker image built successfully!"

build-no-cache: ## Build the Docker image without cache
	@echo "Building KTMB scraper Docker image (no cache)..."
	docker-compose build --no-cache
	@echo "✅ Docker image built successfully!"

clean: ## Clean up Docker images and containers
	@echo "Cleaning up Docker resources..."
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Run targets
run: ## Run the scraper with default settings
	@echo "Running KTMB scraper..."
	export PYTHONPATH=.
	source .venv/bin/activate
	python monitor.py 

search: ## Search for a specific date (DATE=2025-01-15 DIRECTION=jb_to_sg)
	@if [ -z "$(DATE)" ]; then \
		echo "❌ Error: DATE is required. Usage: make search DATE=2025-08-15 DIRECTION=jb-to-sg"; \
		exit 1; \
	fi
	@echo "🔍 Searching for date: $(DATE), direction: $(DIRECTION)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --date $(DATE) --direction $(DIRECTION)

weekend: ## Search all weekends in date range (START=2025-01-01 END=2025-01-31)
	@if [ -z "$(START)" ] || [ -z "$(END)" ]; then \
		echo "❌ Error: START and END dates are required. Usage: make weekend START=2025-01-01 END=2025-01-31"; \
		exit 1; \
	fi
	@echo "🏖️ Searching weekends from $(START) to $(END)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --start-date $(START) --end-date $(END) --weekend-only
