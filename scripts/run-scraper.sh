#!/bin/bash

# KTMB Scraper Docker Runner Script
# This script makes it easy to run the scraper with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build                    Build the Docker image"
    echo "  search [DATE] [DIRECTION] Search for a specific date"
    echo "  monitor [DATE] [SEATS]   Monitor until seats become available"
    echo "  weekend [START] [END]    Search all weekends in date range"
    echo "  friday [YEAR] [MONTH]    Search all Fridays in a month"
    echo "  sunday [YEAR] [MONTH]    Search all Sundays in a month"
    echo "  custom [ARGS...]         Run with custom arguments"
    echo "  help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 search 2025-01-15 jb_to_sg"
    echo "  $0 monitor 2025-01-15 2"
    echo "  $0 weekend 2025-01-01 2025-01-31"
    echo "  $0 friday 2025 1"
    echo "  $0 custom --date 2025-01-15 --telegram-token YOUR_TOKEN"
    echo ""
    echo "Directions: jb_to_sg (JB to Singapore) or sg_to_jb (Singapore to JB)"
}

# Function to build the Docker image
build_image() {
    print_info "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully!"
}

# Function to search for a specific date
search_date() {
    local date=$1
    local direction=${2:-"jb_to_sg"}
    
    if [[ -z "$date" ]]; then
        print_error "Date is required for search command"
        show_usage
        exit 1
    fi
    
    print_info "Searching for date: $date, direction: $direction"
    docker-compose run --rm ktmb-scraper python ktmb_search.py --date "$date" --direction "$direction"
}

# Function to monitor for seats
monitor_seats() {
    local date=$1
    local seats=${2:-2}
    local interval=${3:-300}
    
    if [[ -z "$date" ]]; then
        print_error "Date is required for monitor command"
        show_usage
        exit 1
    fi
    
    print_info "Monitoring for $seats seats on $date (checking every ${interval}s)"
    docker-compose run --rm ktmb-scraper python ktmb_search.py --date "$date" --monitor --target-seats "$seats" --check-interval "$interval"
}

# Function to search weekends
search_weekends() {
    local start_date=$1
    local end_date=$2
    
    if [[ -z "$start_date" || -z "$end_date" ]]; then
        print_error "Start and end dates are required for weekend search"
        show_usage
        exit 1
    fi
    
    print_info "Searching weekends from $start_date to $end_date"
    docker-compose run --rm ktmb-scraper python ktmb_search.py --start-date "$start_date" --end-date "$end_date" --weekend-only
}

# Function to search Fridays
search_fridays() {
    local year=$1
    local month=$2
    
    if [[ -z "$year" || -z "$month" ]]; then
        print_error "Year and month are required for Friday search"
        show_usage
        exit 1
    fi
    
    print_info "Searching all Fridays in $month/$year"
    docker-compose run --rm ktmb-scraper python ktmb_search.py --friday-only --year "$year" --month "$month"
}

# Function to search Sundays
search_sundays() {
    local year=$1
    local month=$2
    
    if [[ -z "$year" || -z "$month" ]]; then
        print_error "Year and month are required for Sunday search"
        show_usage
        exit 1
    fi
    
    print_info "Searching all Sundays in $month/$year"
    docker-compose run --rm ktmb-scraper python ktmb_search.py --sunday-only --year "$year" --month "$month"
}

# Function to run custom command
run_custom() {
    if [[ $# -eq 0 ]]; then
        print_error "Custom command requires arguments"
        show_usage
        exit 1
    fi
    
    print_info "Running custom command: $*"
    docker-compose run --rm ktmb-scraper python ktmb_search.py "$@"
}

# Main script logic
case "${1:-help}" in
    "build")
        build_image
        ;;
    "search")
        search_date "$2" "$3"
        ;;
    "monitor")
        monitor_seats "$2" "$3" "$4"
        ;;
    "weekend")
        search_weekends "$2" "$3"
        ;;
    "friday")
        search_fridays "$2" "$3"
        ;;
    "sunday")
        search_sundays "$2" "$3"
        ;;
    "custom")
        shift
        run_custom "$@"
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 