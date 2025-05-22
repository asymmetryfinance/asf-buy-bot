# ASF Buy Bot Maintenance Guide

## Service Management

```bash
# Check status
systemctl status asf-buy-bot.service

# Start service
systemctl start asf-buy-bot.service

# Stop service
systemctl stop asf-buy-bot.service

# Restart service
systemctl restart asf-buy-bot.service
```

## Logs

```bash
# View logs (live)
journalctl -fu asf-buy-bot.service

# Recent logs (50 lines)
journalctl -u asf-buy-bot.service -n 50
```

## Monitoring

```bash
# Check bot restart history
cat /root/bot-restarts.log

# Check monitoring runs
cat /root/bot-checks.log
```

## Common Tasks

```bash
# Update from git
cd /root/asf-buy-bot && git pull

# Update dependencies
cd /root/asf-buy-bot && /root/.local/bin/uv pip install -e .

# Edit service config
nano /etc/systemd/system/asf-buy-bot.service
systemctl daemon-reload  # After editing

# Edit environment variables
nano /root/asf-buy-bot/.env
```

## Troubleshooting

- Service won't start: Check logs with `journalctl -u asf-buy-bot.service`
- High memory usage: `htop` to monitor, restart with `systemctl restart asf-buy-bot.service`
- Cron not running: Check with `grep check-bot /var/log/syslog`
