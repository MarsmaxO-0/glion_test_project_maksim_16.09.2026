#!/usr/bin/env bash
# Runs every 2 minutes from a systemd timer: checks the site, restarts it if
# it does not answer, and reports to Telegram (when configured).
set -u
ENV_FILE=/etc/klishin.env
STATE=/var/tmp/klishin-watchdog.state   # outside /run/klishin, which systemd wipes on restart
set -a; . "$ENV_FILE"; set +a
HOST=$(echo "${DJANGO_ALLOWED_HOSTS:-localhost}" | cut -d, -f1)

notify() {
  [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_ADMIN_CHAT_ID:-}" ] || return 0
  curl -fsS -m 10 -o /dev/null "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_ADMIN_CHAT_ID}" --data-urlencode "text=$1" || true
}

# Ask gunicorn directly through its socket: nginx may legitimately answer 404/301 for a bare IP after HTTPS setup.
check() { curl -fsS -m 15 -o /dev/null --unix-socket /run/klishin/gunicorn.sock -H "Host: $HOST" http://localhost/healthz/; }

if check; then
  if [ -f "$STATE" ]; then
    rm -f "$STATE"
    notify "✅ ${HOST}: сайт снова отвечает."
  fi
  exit 0
fi

echo "health check failed; restarting klishin"
systemctl restart klishin
sleep 5
if check; then
  notify "⚠️ ${HOST}: сайт не отвечал, перезапустил gunicorn — снова работает."
  exit 0
fi
if [ ! -f "$STATE" ]; then
  mkdir -p "$(dirname "$STATE")"; date > "$STATE"
  notify "🔴 ${HOST}: сайт не отвечает даже после перезапуска. Проверьте: journalctl -u klishin -n 50"
fi
exit 1
