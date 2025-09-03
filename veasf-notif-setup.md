# AFCVX-Notif Service Setup Guide

## Step-by-Step Installation

### 1. Clone the Repository

```bash
cd /root
git clone https://github.com/pastelfork/afcvx-notif
cd afcvx-notif
```

### 2. Install Dependencies

```bash
# Install dependencies using uv (assuming same package manager)
/root/.local/bin/uv pip install -e .

# Or if using regular pip:
# pip install -e .
```

### 3. Environment Configuration

```bash
# Copy environment template if it exists
cp .env.example .env

# Edit environment variables
nano .env
```

### 4. Create Systemd Service File

```bash
# Create service file
sudo nano /etc/systemd/system/afcvx-notif.service
```

**Service file content:**

```ini
[Unit]
Description=AFCVX Notification Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/afcvx-notif
Environment=PATH=/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/root/.local/bin/uv run main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable afcvx-notif.service

# Start the service
sudo systemctl start afcvx-notif.service

# Check status
sudo systemctl status afcvx-notif.service
```

### 6. Set Up Monitoring (Optional)

Create a monitoring script similar to your existing bot:

```bash
# Create monitoring script
nano /root/check-afcvx-notif.sh
```

**Monitoring script content:**

```bash
#!/bin/bash

SERVICE_NAME="afcvx-notif.service"
LOG_FILE="/root/afcvx-notif-checks.log"
RESTART_LOG="/root/afcvx-notif-restarts.log"

echo "$(date): Checking $SERVICE_NAME" >> $LOG_FILE

if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): $SERVICE_NAME is not running. Restarting..." >> $RESTART_LOG
    systemctl start $SERVICE_NAME
    echo "$(date): $SERVICE_NAME restarted" >> $RESTART_LOG
else
    echo "$(date): $SERVICE_NAME is running" >> $LOG_FILE
fi
```

```bash
# Make executable
chmod +x /root/check-afcvx-notif.sh

# Add to crontab (check every 5 minutes)
crontab -e
```

**Add this line to crontab:**

```
*/5 * * * * /root/check-afcvx-notif.sh
```

## Service Management Commands

```bash
# Check status
systemctl status afcvx-notif.service

# Start service
systemctl start afcvx-notif.service

# Stop service
systemctl stop afcvx-notif.service

# Restart service
systemctl restart afcvx-notif.service

# View logs (live)
journalctl -fu afcvx-notif.service

# Recent logs (50 lines)
journalctl -u afcvx-notif.service -n 50
```

## Monitoring Commands

```bash
# Check bot restart history
cat /root/afcvx-notif-restarts.log

# Check monitoring runs
cat /root/afcvx-notif-checks.log
```

## Common Maintenance Tasks

```bash
# Update from git
cd /root/afcvx-notif && git pull

# Update dependencies
cd /root/afcvx-notif && /root/.local/bin/uv pip install -e .

# Edit service config
nano /etc/systemd/system/afcvx-notif.service
systemctl daemon-reload  # After editing

# Edit environment variables
nano /root/afcvx-notif/.env
```

## Troubleshooting

- **Service won't start**: Check logs with `journalctl -u afcvx-notif.service`
- **High memory usage**: Monitor with `htop`, restart with `systemctl restart afcvx-notif.service`
- **Cron not running**: Check with `grep check-afcvx-notif /var/log/syslog`
- **Permission issues**: Ensure files are owned by root: `chown -R root:root /root/afcvx-notif`

## Verification Steps

1. **Service is running**: `systemctl is-active afcvx-notif.service` should return "active"
2. **Logs are flowing**: `journalctl -fu afcvx-notif.service` should show activity
3. **Monitoring works**: Check that cron job creates log entries in `/root/afcvx-notif-checks.log`
4. **Auto-restart works**: Stop the service manually and wait 5 minutes to see if it restarts

## Notes

- Adjust the Python path in the service file if using a different Python installation
- Modify the monitoring interval in crontab if needed (currently set to 5 minutes)
- Ensure all required environment variables are set in the `.env` file
- Check that the main entry point is `main.py` (adjust if different)
