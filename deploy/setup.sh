#!/usr/bin/env bash
# One-shot installer for an Ubuntu 22.04 / 24.04 server (run as root).
#
#   curl -fsSL https://raw.githubusercontent.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026/claude/new-session-q98ffc/deploy/setup.sh | bash
#
# Installs system packages, clones the repository into /opt/klishin, creates a
# virtualenv, loads the site content, and runs the site with gunicorn behind
# nginx on port 80. Safe to re-run: it updates the code and restarts services.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026.git}"
BRANCH="${BRANCH:-claude/new-session-q98ffc}"
APP_DIR=/opt/klishin
ENV_FILE=/etc/klishin.env
SERVER_NAME="${SERVER_NAME:-_}"   # domain name, or "_" to answer on the bare IP

if [ "$(id -u)" -ne 0 ]; then echo "Run as root (sudo -i)"; exit 1; fi

echo "==> System packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q python3 python3-venv python3-pip git nginx

echo "==> Code"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch -q origin "$BRANCH"
  git -C "$APP_DIR" checkout -q "$BRANCH"
  git -C "$APP_DIR" reset -q --hard "origin/$BRANCH"
else
  git clone -q --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

echo "==> Python environment"
[ -d "$APP_DIR/.venv" ] || python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q --upgrade pip
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt" gunicorn

echo "==> Settings file $ENV_FILE"
if [ ! -f "$ENV_FILE" ]; then
  SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
  IP=$(curl -fsS -4 https://api.ipify.org || hostname -I | awk '{print $1}')
  cat > "$ENV_FILE" <<ENV
DJANGO_SECRET_KEY=$SECRET
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=$IP,localhost,127.0.0.1
# Claude API key for the site assistant (leave empty to hide the chat):
ANTHROPIC_API_KEY=
ENV
  chmod 600 "$ENV_FILE"
  echo "    created $ENV_FILE (edit it to add ANTHROPIC_API_KEY or a domain)"
fi

echo "==> Database and static files"
set -a; . "$ENV_FILE"; set +a
cd "$APP_DIR"
FIRST_RUN=0; [ -f db.sqlite3 ] || FIRST_RUN=1
.venv/bin/python manage.py migrate --noinput -v0
[ "$FIRST_RUN" = 1 ] && .venv/bin/python manage.py loaddata site_content -v0 && echo "    site content loaded"
.venv/bin/python manage.py collectstatic --noinput -v0
chown -R www-data:www-data "$APP_DIR"

echo "==> gunicorn service"
cat > /etc/systemd/system/klishin.service <<UNIT
[Unit]
Description=Klishin & Partners website (gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$APP_DIR/.venv/bin/gunicorn klishin.wsgi:application --bind unix:/run/klishin.sock --workers 3 --timeout 120
RuntimeDirectory=klishin
Restart=always

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable -q klishin
systemctl restart klishin

echo "==> nginx"
cat > /etc/nginx/sites-available/klishin <<NGINX
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name $SERVER_NAME;
    client_max_body_size 10m;

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public";
    }
    location / {
        proxy_pass http://unix:/run/klishin.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
NGINX
ln -sf /etc/nginx/sites-available/klishin /etc/nginx/sites-enabled/klishin
rm -f /etc/nginx/sites-enabled/default
nginx -t -q
systemctl enable -q nginx
systemctl reload nginx

echo
echo "Done. The site answers on http://$(grep -o 'DJANGO_ALLOWED_HOSTS=[^,]*' "$ENV_FILE" | cut -d= -f2)/"
echo "Next: edit $ENV_FILE (nano $ENV_FILE) to add ANTHROPIC_API_KEY, then: systemctl restart klishin"
echo "Admin user: cd $APP_DIR && set -a && . $ENV_FILE && set +a && .venv/bin/python manage.py createsuperuser"
