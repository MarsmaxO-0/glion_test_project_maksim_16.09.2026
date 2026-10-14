# Klishin & Partners website — project memory for Claude Code

Read this first. It summarises everything built so far so a new session can continue without the old chat.

## What this is
A production website for Klishin & Partners (Moscow bar association, founded 1990), built for the Glion
MSc-HEI2058 assignment "Improve one business with AI". Owner: Maksim (the user). Language of conversation
with the user: Russian; code and docs: English. The user is not a developer: explain terminal steps one
command at a time, never assume git/Python knowledge, and ask for screenshots of errors.

- Live site: https://lawfirmrussia.com (RU at /ru/, EN at /en/), HTTPS via certbot.
- Server: DigitalOcean droplet "test-glion-law-firm", Ubuntu 24.04, IP 164.90.239.23, 1 GB RAM.
  Access only through the DigitalOcean Web Console (root). Code lives in /opt/klishin, secrets in /etc/klishin.env.
- Repository: github.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026, branch `claude/new-session-q98ffc` (the deployed branch).
- Telegram: bot @lawalertsbot serves both admin notifications (enquiries, backups, watchdog) and the public assistant.

## Stack
Django 6 + SQLite, plain HTML/CSS/JS, gunicorn + nginx + systemd. Anthropic SDK for the assistant (model from
settings.CHAT_MODEL, default claude-opus-5-5). Pillow for photo uploads. No JS build step.

Key places:
- `core/models.py` — content models with paired `_ru`/`_en` fields and `.t(field, lang)`; `ContactMessage`, `ChatLog`.
- `core/ui.py` — all fixed page copy and interface strings, both languages. `core/legal_notes.py` — the assistant's law reference.
- `core/knowledge.py` + `core/chat.py` + `core/api.py` — assistant system prompt, Claude call, `/api/chat/`.
- `core/management/commands/` — `telegram_bot` (long-polling assistant), `backup`, `fetch_photos`.
- `core/middleware.py` — maintenance mode (flag file `MAINTENANCE` in project root).
- `templates/base.html`, `core/templates/core/*.html`, `static/css/site.css`, `static/js/{site,chat}.js`.
- `core/fixtures/site_content.json` — all content; regenerate with `python tools/build_fixture.py` from `prototype/`.
- `deploy/setup.sh` — idempotent server installer/updater; `deploy/watchdog.sh`; `deploy/README.md`.
- `docs/` — course deliverables (process rubric). The pitch deck is a claude.ai Slides artifact.

## Everyday commands
Local: `source .venv/bin/activate && python manage.py runserver` (set `ANTHROPIC_API_KEY` first for the chat).
Tests: `python manage.py test` (29 tests, all must pass before pushing).
Deploy/update the server (run in the Web Console):
`curl -fsSL https://raw.githubusercontent.com/MarsmaxO-0/glion_test_project_maksim_16.09.2026/claude/new-session-q98ffc/deploy/setup.sh | bash`
Server services: `klishin` (site), `klishin-bot`, timers `klishin-backup`, `klishin-watchdog`. Logs: `journalctl -u <name> -n 50`.

## Conventions and decisions
- Commit to the branch above and push; the server pulls that branch. Keep `setup.sh` idempotent and safe to re-run.
- Lawyer photos are uploaded in the admin (klishin.ru blocks server downloads); silhouettes shown by default.
- Contact form: honeypot + Cloudflare Turnstile (keys in env). A home-made captcha was tried and rejected.
- Health checks go through gunicorn's unix socket, not nginx (nginx returns 404 for bare-IP hosts after HTTPS).
- The nginx site config is managed by certbot; the installer must not overwrite it.
- Hero animation is MP4/WebM (not the 1.6 MB GIF) for performance.
- Never put secrets in the repo; `.env`-style values live only in `/etc/klishin.env`.

## Open items the user may ask for next
Cloudflare CDN in front of the site, external uptime monitor (UptimeRobot), consultation booking with calendar,
analytics (Yandex.Metrica), Google Search Console sitemap submission, real photos upload, presenting the site to
the firm and recording the response (assignment bonus).
