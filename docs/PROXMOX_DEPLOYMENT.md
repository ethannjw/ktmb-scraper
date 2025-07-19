# KTMB Scraper Proxmox Deployment Guide

This guide covers deploying the KTMB scraper in various Proxmox environments.

## 🎯 Quick Start (LXC Container)

### 1. Create LXC Container

1. **In Proxmox Web UI**:
   - Go to your node → LXC Containers
   - Click "Create CT"
   - Choose Ubuntu 22.04 template
   - Set container ID (e.g., 100)
   - Set hostname: `ktmb-scraper`
   - Set password for root user

2. **Resource Allocation**:
   - Memory: 2048 MB
   - Storage: 10 GB
   - CPU: 2 cores
   - Enable "Docker" in Features tab

3. **Network**:
   - Bridge: `vmbr0`
   - IP: DHCP or static IP
   - Gateway: Your network gateway

### 2. Install Docker

```bash
# Connect to container
pct enter 100

# Update system
apt update && apt upgrade -y

# Install Docker
apt install -y docker.io docker-compose

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Verify installation
docker --version
docker-compose --version
```

### 3. Deploy the Scraper

```bash
# Clone the project
git clone <your-repo-url> /opt/ktmb-scraper
cd /opt/ktmb-scraper/ktmb-scraper

# Build the Docker image
make build

# Test the scraper
make search DATE=2025-01-15 DIRECTION=jb_to_sg
```

## 🖥️ VM Deployment

### 1. Create VM

1. **In Proxmox Web UI**:
   - Go to your node → VMs
   - Click "Create VM"
   - Choose Ubuntu 22.04 Server ISO
   - Set VM ID (e.g., 200)
   - Set name: `ktmb-scraper-vm`

2. **VM Configuration**:
   - Memory: 2048 MB
   - Storage: 20 GB
   - CPU: 2 cores
   - Network: Bridge `vmbr0`

### 2. Install Docker in VM

```bash
# SSH into VM
ssh user@vm-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install -y docker-compose
```

### 3. Deploy Scraper

```bash
# Clone and deploy (same as LXC)
git clone <your-repo-url> /opt/ktmb-scraper
cd /opt/ktmb-scraper/ktmb-scraper
make build
make search DATE=2025-01-15 DIRECTION=jb_to_sg
```

## 🔄 Automated Deployment Script

Create a deployment script for easy setup:

```bash
#!/bin/bash
# deploy-ktmb-scraper.sh

set -e

echo "🚀 Deploying KTMB Scraper..."

# Install dependencies
apt update
apt install -y git docker.io docker-compose

# Enable Docker
systemctl enable docker
systemctl start docker

# Clone repository
if [ ! -d "/opt/ktmb-scraper" ]; then
    git clone <your-repo-url> /opt/ktmb-scraper
fi

cd /opt/ktmb-scraper/ktmb-scraper

# Build Docker image
echo "📦 Building Docker image..."
make build

# Create output directory
mkdir -p /opt/ktmb-scraper/output

# Test deployment
echo "🧪 Testing deployment..."
make search DATE=2025-01-15 DIRECTION=jb_to_sg

echo "✅ Deployment completed successfully!"
```

## ⏰ Scheduling and Automation

### Using Cron Jobs

```bash
# Edit crontab
crontab -e

# Add scheduled jobs
# Daily check at 8 AM
0 8 * * * cd /opt/ktmb-scraper/ktmb-scraper && make search DATE=2025-01-15 DIRECTION=jb_to_sg

# Monitor every 6 hours
0 */6 * * * cd /opt/ktmb-scraper/ktmb-scraper && make monitor DATE=2025-01-15 SEATS=2 INTERVAL=300

# Weekend search every Friday
0 9 * * 5 cd /opt/ktmb-scraper/ktmb-scraper && make weekend START=2025-01-01 END=2025-01-31
```

### Using Systemd Timers

```bash
# Create service file
sudo nano /etc/systemd/system/ktmb-scraper.service

[Unit]
Description=KTMB Scraper Service
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/ktmb-scraper/ktmb-scraper
ExecStart=/usr/bin/make search DATE=2025-01-15 DIRECTION=jb_to_sg
User=root

# Create timer file
sudo nano /etc/systemd/system/ktmb-scraper.timer

[Unit]
Description=Run KTMB Scraper daily
Requires=ktmb-scraper.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target

# Enable and start
sudo systemctl enable ktmb-scraper.timer
sudo systemctl start ktmb-scraper.timer
```

## 📊 Monitoring and Logs

### View Logs

```bash
# Container logs
docker-compose logs ktmb-scraper

# Follow logs in real-time
docker-compose logs -f ktmb-scraper

# View output files
ls -la /opt/ktmb-scraper/output/
cat /opt/ktmb-scraper/output/ktmb_*.json
```

### Health Checks

```bash
# Check container status
docker ps

# Test scraper functionality
cd /opt/ktmb-scraper/ktmb-scraper
make test

# Check resource usage
docker stats ktmb-scraper
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# /opt/ktmb-scraper/ktmb-scraper/.env
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=60000
MIN_AVAILABLE_SEATS=2
CHECK_INTERVAL=300
```

### Custom Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  ktmb-scraper:
    build: .
    container_name: ktmb-scraper-prod
    volumes:
      - ./output:/app/output
      - ./.env:/app/.env:ro
    environment:
      - PLAYWRIGHT_HEADLESS=true
      - PLAYWRIGHT_TIMEOUT=60000
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🛡️ Security Considerations

### LXC Container Security

```bash
# Limit container resources
# In Proxmox Web UI → LXC Container → Resources
# Set memory and CPU limits

# Use unprivileged containers
# Enable "Unprivileged container" in container options
```

### Network Security

```bash
# Restrict network access if needed
# In Proxmox Web UI → LXC Container → Network
# Set firewall rules or use isolated network
```

### Docker Security

```bash
# Run as non-root user (already configured in Dockerfile)
# Use read-only volumes where possible
# Regular security updates
apt update && apt upgrade -y
```

## 🔄 Backup Strategy

### Backup Output Data

```bash
#!/bin/bash
# backup-ktmb-data.sh

BACKUP_DIR="/backup/ktmb-scraper"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup output files
tar -czf $BACKUP_DIR/ktmb-output-$DATE.tar.gz /opt/ktmb-scraper/output/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "ktmb-output-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/ktmb-output-$DATE.tar.gz"
```

### Automated Backup

```bash
# Add to crontab
0 2 * * * /opt/ktmb-scraper/backup-ktmb-data.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Docker Permission Issues**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **Playwright Browser Issues**:
   ```bash
   # Rebuild with browser dependencies
   make build-no-cache
   ```

3. **Network Connectivity**:
   ```bash
   # Test connectivity
   make test
   
   # Check DNS
   nslookup shuttleonline.ktmb.com.my
   ```

4. **Resource Issues**:
   ```bash
   # Check resource usage
   docker stats
   free -h
   df -h
   ```

### Debug Mode

```bash
# Run with browser visible
make debug DATE=2025-01-15 DIRECTION=jb_to_sg

# Access container shell
make shell
```

## 📈 Performance Optimization

### Resource Tuning

```bash
# Adjust Docker resource limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### Monitoring Setup

```bash
# Install monitoring tools
apt install -y htop iotop

# Monitor system resources
htop
iotop
```

## 🎯 Production Checklist

- [ ] LXC container or VM created with sufficient resources
- [ ] Docker and Docker Compose installed
- [ ] KTMB scraper deployed and tested
- [ ] Environment variables configured
- [ ] Scheduled jobs set up
- [ ] Backup strategy implemented
- [ ] Monitoring and logging configured
- [ ] Security measures applied
- [ ] Documentation updated

## 📞 Support

For issues or questions:
1. Check the logs: `make logs`
2. Test connectivity: `make test`
3. Review this deployment guide
4. Check the main README.md for usage examples 