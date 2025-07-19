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
	docker-compose run --rm ktmb-scraper python ktmb_search.py --help

search: ## Search for a specific date (DATE=2025-01-15 DIRECTION=jb_to_sg)
	@if [ -z "$(DATE)" ]; then \
		echo "❌ Error: DATE is required. Usage: make search DATE=2025-08-15 DIRECTION=jb-to-sg"; \
		exit 1; \
	fi
	@echo "🔍 Searching for date: $(DATE), direction: $(DIRECTION)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --date $(DATE) --direction $(DIRECTION)

monitor: ## Monitor until seats become available (DATE=2025-01-15 SEATS=2 INTERVAL=300)
	@if [ -z "$(DATE)" ]; then \
		echo "❌ Error: DATE is required. Usage: make monitor DATE=2025-01-15 SEATS=2 INTERVAL=300"; \
		exit 1; \
	fi
	@echo "👀 Monitoring for $(SEATS) seats on $(DATE) (checking every $(INTERVAL)s)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --date $(DATE) --monitor --target-seats $(SEATS) --check-interval $(INTERVAL)

weekend: ## Search all weekends in date range (START=2025-01-01 END=2025-01-31)
	@if [ -z "$(START)" ] || [ -z "$(END)" ]; then \
		echo "❌ Error: START and END dates are required. Usage: make weekend START=2025-01-01 END=2025-01-31"; \
		exit 1; \
	fi
	@echo "🏖️ Searching weekends from $(START) to $(END)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --start-date $(START) --end-date $(END) --weekend-only

friday: ## Search all Fridays in a month (YEAR=2025 MONTH=1)
	@if [ -z "$(YEAR)" ] || [ -z "$(MONTH)" ]; then \
		echo "❌ Error: YEAR and MONTH are required. Usage: make friday YEAR=2025 MONTH=1"; \
		exit 1; \
	fi
	@echo "📅 Searching all Fridays in $(MONTH)/$(YEAR)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --friday-only --year $(YEAR) --month $(MONTH)

sunday: ## Search all Sundays in a month (YEAR=2025 MONTH=1)
	@if [ -z "$(YEAR)" ] || [ -z "$(MONTH)" ]; then \
		echo "❌ Error: YEAR and MONTH are required. Usage: make sunday YEAR=2025 MONTH=1"; \
		exit 1; \
	fi
	@echo "📅 Searching all Sundays in $(MONTH)/$(YEAR)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py --sunday-only --year $(YEAR) --month $(MONTH)

custom: ## Run with custom arguments (ARGS="--date 2025-01-15 --telegram-token YOUR_TOKEN")
	@if [ -z "$(ARGS)" ]; then \
		echo "❌ Error: ARGS is required. Usage: make custom ARGS='--date 2025-01-15 --telegram-token YOUR_TOKEN'"; \
		exit 1; \
	fi
	@echo "⚙️ Running custom command: $(ARGS)"
	docker-compose run --rm ktmb-scraper python ktmb_search.py $(ARGS)

# Service targets
monitor-service: ## Run the pre-configured monitoring service
	@echo "🔄 Running monitoring service..."
	docker-compose run --rm ktmb-monitor

weekend-service: ## Run the pre-configured weekend search service
	@echo "🏖️ Running weekend search service..."
	docker-compose run --rm ktmb-weekend-search

# Scheduling targets
schedule-cron: ## Setup cron job (SCHEDULE='0 8 * * *' COMMAND='search 2025-01-15 jb_to_sg')
	@if [ -z "$(SCHEDULE)" ] || [ -z "$(COMMAND)" ]; then \
		echo "❌ Error: SCHEDULE and COMMAND are required."; \
		echo "Usage: make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search 2025-01-15 jb_to_sg'"; \
		exit 1; \
	fi
	@echo "⏰ Setting up cron job..."
	@echo "Schedule: $(SCHEDULE)"
	@echo "Command: $(COMMAND)"
	@(crontab -l 2>/dev/null; echo "$(SCHEDULE) cd $(PWD) && make $(COMMAND)") | crontab -
	@echo "✅ Cron job added successfully!"

schedule-systemd: ## Setup systemd timer (NAME=daily-check SCHEDULE=daily COMMAND='search 2025-01-15 jb_to_sg')
	@if [ -z "$(NAME)" ] || [ -z "$(SCHEDULE)" ] || [ -z "$(COMMAND)" ]; then \
		echo "❌ Error: NAME, SCHEDULE, and COMMAND are required."; \
		echo "Usage: make schedule-systemd NAME=daily-check SCHEDULE=daily COMMAND='search 2025-01-15 jb_to_sg'"; \
		exit 1; \
	fi
	@echo "⏰ Setting up systemd timer: ktmb-$(NAME)"
	@echo "[Unit]" | sudo tee /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "Description=KTMB Scraper - $(NAME)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "After=network.target" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "[Service]" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "Type=oneshot" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "User=$(USER)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "WorkingDirectory=$(PWD)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "ExecStart=make $(COMMAND)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "StandardOutput=journal" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "StandardError=journal" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "[Install]" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "WantedBy=multi-user.target" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).service > /dev/null
	@echo "[Unit]" | sudo tee /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "Description=KTMB Scraper Timer - $(NAME)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "Requires=ktmb-$(NAME).service" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "[Timer]" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "$(SCHEDULE)" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "Persistent=true" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "[Install]" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@echo "WantedBy=timers.target" | sudo tee -a /etc/systemd/system/ktmb-$(NAME).timer > /dev/null
	@sudo systemctl daemon-reload
	@sudo systemctl enable ktmb-$(NAME).timer
	@sudo systemctl start ktmb-$(NAME).timer
	@echo "✅ Systemd timer setup successfully!"

list-jobs: ## List current scheduled jobs
	@echo "=== Cron Jobs ==="
	@crontab -l 2>/dev/null | grep -E "(ktmb|make)" || echo "No cron jobs found"
	@echo ""
	@echo "=== Systemd Timers ==="
	@systemctl list-timers --user 2>/dev/null | grep ktmb || echo "No user systemd timers found"
	@echo ""
	@echo "=== All Systemd Timers ==="
	@sudo systemctl list-timers 2>/dev/null | grep ktmb || echo "No systemd timers found"

remove-job: ## Remove a scheduled job (JOB_ID=1 or JOB_ID=daily-check)
	@if [ -z "$(JOB_ID)" ]; then \
		echo "❌ Error: JOB_ID is required. Usage: make remove-job JOB_ID=1"; \
		exit 1; \
	fi
	@if echo "$(JOB_ID)" | grep -q '^[0-9]\+$$'; then \
		echo "🗑️ Removing cron job at line $(JOB_ID)"; \
		crontab -l 2>/dev/null | sed "$(JOB_ID)d" | crontab -; \
		echo "✅ Cron job removed!"; \
	else \
		echo "🗑️ Removing systemd timer: ktmb-$(JOB_ID)"; \
		sudo systemctl stop ktmb-$(JOB_ID).timer; \
		sudo systemctl disable ktmb-$(JOB_ID).timer; \
		sudo rm -f /etc/systemd/system/ktmb-$(JOB_ID).service; \
		sudo rm -f /etc/systemd/system/ktmb-$(JOB_ID).timer; \
		sudo systemctl daemon-reload; \
		echo "✅ Systemd timer removed!"; \
	fi

# Utility targets
logs: ## View container logs
	@echo "📋 Container logs:"
	docker-compose logs ktmb-scraper

logs-follow: ## Follow container logs in real-time
	@echo "📋 Following container logs (Ctrl+C to stop):"
	docker-compose logs -f ktmb-scraper

shell: ## Access container shell
	@echo "🐚 Opening container shell..."
	docker-compose run --rm ktmb-scraper /bin/bash

test: ## Test network connectivity
	@echo "🌐 Testing network connectivity..."
	docker-compose run --rm ktmb-scraper python -c "import requests; print('✅ Network OK:', requests.get('https://shuttleonline.ktmb.com.my').status_code)"

status: ## Show Docker container status
	@echo "📊 Docker container status:"
	docker-compose ps

# Debug targets
debug: ## Run with browser visible (for debugging)
	@echo "🐛 Running in debug mode (browser visible)..."
	docker-compose run --rm -e PLAYWRIGHT_HEADLESS=false ktmb-scraper python ktmb_search.py --date $(DATE) --direction $(DIRECTION)

debug-shell: ## Access container shell with debug environment
	@echo "🐛 Opening debug container shell..."
	docker-compose run --rm -e PLAYWRIGHT_HEADLESS=false ktmb-scraper /bin/bash

# Examples target
examples: ## Show example commands
	@echo "📚 Example Commands:"
	@echo ""
	@echo "Build and run:"
	@echo "  make build"
	@echo "  make search DATE=2025-01-15 DIRECTION=jb_to_sg"
	@echo ""
	@echo "Monitoring:"
	@echo "  make monitor DATE=2025-01-15 SEATS=2 INTERVAL=300"
	@echo "  make monitor-service"
	@echo ""
	@echo "Batch searches:"
	@echo "  make weekend START=2025-01-01 END=2025-01-31"
	@echo "  make friday YEAR=2025 MONTH=1"
	@echo "  make sunday YEAR=2025 MONTH=1"
	@echo ""
	@echo "Custom commands:"
	@echo "  make custom ARGS='--date 2025-01-15 --telegram-token YOUR_TOKEN --telegram-chat-id YOUR_CHAT_ID'"
	@echo ""
	@echo "Scheduling:"
	@echo "  make schedule-cron SCHEDULE='0 8 * * *' COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'"
	@echo "  make schedule-systemd NAME=daily-check SCHEDULE=daily COMMAND='search DATE=2025-01-15 DIRECTION=jb_to_sg'"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs"
	@echo "  make shell"
	@echo "  make test"
	@echo "  make clean" 