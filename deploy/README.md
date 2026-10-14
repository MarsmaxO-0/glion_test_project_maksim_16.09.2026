# Deploying to a Linux server

Tested on Ubuntu 24.04 (DigitalOcean droplet). Everything is done by
`deploy/setup.sh`, which is safe to re-run to update the site.

## First install

Open the server console as root and run:

```sh
curl -fsSL https://raw.githubusercontent.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026/claude/new-session-q98ffc/deploy/setup.sh | bash
```

The script installs Python, nginx and git, clones the repository into
`/opt/klishin`, loads the site content into SQLite, collects static files, and
starts gunicorn (systemd service `klishin`) behind nginx on port 80. If the
repository is private, pass a GitHub token:

```sh
curl -fsSL https://TOKEN@raw.githubusercontent.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026/claude/new-session-q98ffc/deploy/setup.sh \
  | REPO_URL=https://TOKEN@github.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026.git bash
```

## Settings

All secrets live in `/etc/klishin.env` (created on first run):

```
DJANGO_SECRET_KEY=...        generated automatically
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=1.2.3.4,example.com
ANTHROPIC_API_KEY=sk-ant-... enables the chat assistant
```

After editing it: `systemctl restart klishin`.

## Telegram notifications, backups, monitoring

1. In Telegram open **@BotFather**, send `/newbot`, follow the prompts and copy the token.
2. Open **@userinfobot** (or write anything to your new bot and open
   `https://api.telegram.org/bot<TOKEN>/getUpdates`) to find your numeric chat id.
3. Put both into `/etc/klishin.env`:

```
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_ADMIN_CHAT_ID=123456789
```

4. `systemctl restart klishin`.

You then receive: every new enquiry from the contact form, the daily backup
archive (03:30 server time, also kept in `/var/backups/klishin`, last 14), and
watchdog alerts. The watchdog (`deploy/watchdog.sh`, every 2 minutes)
restarts gunicorn if `/healthz/` stops answering and reports the outcome.

For alerts when the whole server is down, add the site to a free external
monitor such as UptimeRobot (https://uptimerobot.com): monitor type HTTP(s),
URL `https://your-domain/healthz/`, interval 5 minutes.

Manual backup: `systemctl start klishin-backup` · Restore: stop the site,
unpack the archive into `/opt/klishin` (it contains `db.sqlite3` and `media/`),
`chown -R www-data:www-data /opt/klishin`, start the site.

## Maintenance mode

```sh
touch /opt/klishin/MAINTENANCE     # visitors see the "under maintenance" page (admin keeps working)
rm /opt/klishin/MAINTENANCE        # back to normal
```

## Spam protection

The contact form has a honeypot field and a slide-puzzle captcha (generated on the server, no third-party service). To add
Cloudflare Turnstile as well, create a widget at
https://dash.cloudflare.com/?to=/:account/turnstile and set
`TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` in `/etc/klishin.env`.

## Everyday commands

| Task | Command |
|------|---------|
| Update to the latest code | re-run the `curl ... \| bash` line above |
| Restart the site | `systemctl restart klishin` |
| See errors | `journalctl -u klishin -n 50` |
| Create an admin user | `cd /opt/klishin && set -a && . /etc/klishin.env && set +a && .venv/bin/python manage.py createsuperuser` |
| Back up the database | copy `/opt/klishin/db.sqlite3` |

## Domain and HTTPS

Point the domain's A record at the server IP, add the domain to
`DJANGO_ALLOWED_HOSTS` in `/etc/klishin.env`, re-run the installer with
`SERVER_NAME=example.com`, then obtain a certificate:

```sh
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d example.com
```
