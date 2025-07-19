#!/bin/bash

# KTMB Scraper Scheduler Script
# This script helps set up automated scheduling for the scraper

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
    echo "  setup-cron [SCHEDULE] [COMMAND]  Setup cron job"
    echo "  setup-systemd [NAME] [SCHEDULE] [COMMAND] Setup systemd timer"
    echo "  list-jobs                         List current scheduled jobs"
    echo "  remove-job [JOB_ID]              Remove a scheduled job"
    echo "  help                              Show this help message"
    echo ""
    echo "Schedule formats:"
    echo "  Cron: '0 8 * * *' (daily at 8 AM)"
    echo "  Systemd: 'daily', 'weekly', 'monthly' or 'OnCalendar=*-*-* 08:00:00'"
    echo ""
    echo "Examples:"
    echo "  $0 setup-cron '0 8 * * *' 'search 2025-01-15 jb_to_sg'"
    echo "  $0 setup-cron '0 */6 * * *' 'monitor 2025-01-15 2'"
    echo "  $0 setup-systemd 'ktmb-daily' 'daily' 'search 2025-01-15 jb_to_sg'"
    echo "  $0 list-jobs"
    echo "  $0 remove-job 1"
}

# Function to setup cron job
setup_cron() {
    local schedule=$1
    local command=$2
    
    if [[ -z "$schedule" || -z "$command" ]]; then
        print_error "Schedule and command are required for cron setup"
        show_usage
        exit 1
    fi
    
    # Get the full path to the run script
    local script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-scraper.sh"
    
    # Create cron job entry
    local cron_entry="$schedule cd $(dirname "$script_path") && $script_path $command"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
    
    print_success "Cron job added successfully!"
    print_info "Schedule: $schedule"
    print_info "Command: $command"
    print_info "To view cron jobs: crontab -l"
}

# Function to setup systemd timer
setup_systemd() {
    local name=$1
    local schedule=$2
    local command=$3
    
    if [[ -z "$name" || -z "$schedule" || -z "$command" ]]; then
        print_error "Name, schedule, and command are required for systemd setup"
        show_usage
        exit 1
    fi
    
    # Get the full path to the run script
    local script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run-scraper.sh"
    local project_dir="$(dirname "$script_path")"
    
    # Create service file
    local service_file="/etc/systemd/system/ktmb-$name.service"
    cat > "$service_file" << EOF
[Unit]
Description=KTMB Scraper - $name
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$project_dir
ExecStart=$script_path $command
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Create timer file
    local timer_file="/etc/systemd/system/ktmb-$name.timer"
    cat > "$timer_file" << EOF
[Unit]
Description=KTMB Scraper Timer - $name
Requires=ktmb-$name.service

[Timer]
$schedule
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    # Reload systemd and enable timer
    sudo systemctl daemon-reload
    sudo systemctl enable "ktmb-$name.timer"
    sudo systemctl start "ktmb-$name.timer"
    
    print_success "Systemd timer setup successfully!"
    print_info "Service: ktmb-$name.service"
    print_info "Timer: ktmb-$name.timer"
    print_info "Schedule: $schedule"
    print_info "Command: $command"
    print_info "To check status: sudo systemctl status ktmb-$name.timer"
}

# Function to list current jobs
list_jobs() {
    echo "=== Cron Jobs ==="
    crontab -l 2>/dev/null | grep -E "(ktmb|run-scraper)" || echo "No cron jobs found"
    
    echo ""
    echo "=== Systemd Timers ==="
    systemctl list-timers --user 2>/dev/null | grep ktmb || echo "No systemd timers found"
    
    echo ""
    echo "=== All Systemd Timers ==="
    sudo systemctl list-timers 2>/dev/null | grep ktmb || echo "No systemd timers found"
}

# Function to remove a job
remove_job() {
    local job_id=$1
    
    if [[ -z "$job_id" ]]; then
        print_error "Job ID is required for removal"
        show_usage
        exit 1
    fi
    
    # For cron jobs, job_id is the line number
    if [[ "$job_id" =~ ^[0-9]+$ ]]; then
        print_info "Removing cron job at line $job_id"
        crontab -l 2>/dev/null | sed "${job_id}d" | crontab -
        print_success "Cron job removed!"
    else
        # For systemd timers, job_id is the timer name
        print_info "Removing systemd timer: ktmb-$job_id"
        sudo systemctl stop "ktmb-$job_id.timer"
        sudo systemctl disable "ktmb-$job_id.timer"
        sudo rm -f "/etc/systemd/system/ktmb-$job_id.service"
        sudo rm -f "/etc/systemd/system/ktmb-$job_id.timer"
        sudo systemctl daemon-reload
        print_success "Systemd timer removed!"
    fi
}

# Function to create example schedules
create_examples() {
    print_info "Creating example schedule configurations..."
    
    # Example 1: Daily morning check
    echo "Example 1: Daily morning check at 8 AM"
    echo "  $0 setup-cron '0 8 * * *' 'search 2025-01-15 jb_to_sg'"
    echo ""
    
    # Example 2: Every 6 hours monitoring
    echo "Example 2: Monitor every 6 hours"
    echo "  $0 setup-cron '0 */6 * * *' 'monitor 2025-01-15 2'"
    echo ""
    
    # Example 3: Weekend search every Friday
    echo "Example 3: Weekend search every Friday at 9 AM"
    echo "  $0 setup-cron '0 9 * * 5' 'weekend 2025-01-01 2025-01-31'"
    echo ""
    
    # Example 4: Systemd daily timer
    echo "Example 4: Systemd daily timer"
    echo "  $0 setup-systemd 'daily-check' 'daily' 'search 2025-01-15 jb_to_sg'"
    echo ""
    
    # Example 5: Custom systemd schedule
    echo "Example 5: Custom systemd schedule (every 4 hours)"
    echo "  $0 setup-systemd 'monitor-4h' 'OnCalendar=*:0/4' 'monitor 2025-01-15 2'"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "setup-cron")
        setup_cron "$2" "$3"
        ;;
    "setup-systemd")
        setup_systemd "$2" "$3" "$4"
        ;;
    "list-jobs")
        list_jobs
        ;;
    "remove-job")
        remove_job "$2"
        ;;
    "examples")
        create_examples
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