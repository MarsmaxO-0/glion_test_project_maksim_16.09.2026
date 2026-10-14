# Klishin & Partners — law firm website

Website of the Moscow bar collegium "Klishin & Partners" (klishin.ru), built
with **Django 6 / Python 3.13**, plain **HTML, CSS and JavaScript**, and a
**SQLite** database. Russian and English versions share one content model.

## Features

- Pages: home, practices (16 areas in 4 groups with expandable lawyer panels),
  team, 15 lawyer biographies, track record, IP Centre, press centre, contacts.
- Two languages with URL prefixes (`/ru/…`, `/en/…`) and a RU / EN switch that
  keeps the current page. Content is stored in paired `*_ru` / `*_en` fields.
- Press centre reads the public klishin.ru feed server-side, caches it for
  24 hours and falls back to the saved items in the database.
- Contact form that stores enquiries in SQLite (with a honeypot field).
- Site assistant: a chat widget powered by Claude that knows the site's content
  (pages, practices, lawyers, contacts) and a short Russian-law reference, and
  points visitors to the right practice and advocate. Conversations are logged
  in the admin.
- Django admin for every content type: lawyers, practices, cases, press items,
  publications, research items, IP Centre areas and received messages.
- Responsive layout, scroll-reveal animations, mobile navigation.

## Project layout

| Path | Purpose |
|------|---------|
| `klishin/` | Django project: settings, root URL configuration. |
| `core/models.py` | Content models (`Lawyer`, `Practice`, `Case`, `PressItem`, …). |
| `core/views.py`, `core/urls.py` | Page views and routes. |
| `core/ui.py` | Fixed page copy and interface strings in both languages. |
| `core/press.py` | Live press feed with caching and database fallback. |
| `core/chat.py`, `core/api.py` | Claude call and the `/api/chat/` endpoint for the assistant. |
| `core/knowledge.py`, `core/legal_notes.py` | The assistant's system prompt: site description built from the database plus the Russian-law reference. |
| `static/js/chat.js`, `core/templates/core/_chat.html` | The chat widget. |
| `core/templates/core/` | Page templates; `templates/base.html` is the shared layout. |
| `static/css/site.css`, `static/js/site.js` | Styles and behaviour. |
| `core/fixtures/site_content.json` | All site content, loaded into SQLite with `loaddata`. |
| `tools/build_fixture.py` | Regenerates the fixture from the original prototype. |
| `prototype/` | The original static prototype the site was built from. |

## Running locally

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata site_content
python manage.py createsuperuser        # optional, for /admin/
python manage.py runserver
```

Open <http://127.0.0.1:8000/> (redirects to `/ru/`; English is at `/en/`).
The admin is at <http://127.0.0.1:8000/admin/>.

Run the tests with:

```sh
python manage.py test
```

## Configuration

Environment variables (all optional):

| Variable | Default | Meaning |
|----------|---------|---------|
| `DJANGO_SECRET_KEY` | development key | Secret key for production. |
| `DJANGO_DEBUG` | `1` | Set to `0` in production. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated host list. |
| `PRESS_FEED_ENABLED` | `1` | Set to `0` to show only the saved press items. |
| `PRESS_FEED_URL` | klishin.ru WordPress API | Source of the live news feed. |
| `ANTHROPIC_API_KEY` | empty | Claude API key. The chat widget appears only when it is set. |
| `CHAT_MODEL` | `claude-opus-5-5` | Model used by the assistant. |

## Site assistant

Set the key before starting the server and the "Ask a question" button appears
on every page:

```sh
export ANTHROPIC_API_KEY=sk-ant-...      # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python manage.py runserver
```

The assistant answers in the visitor's language, links to site pages, explains
basic legal terms from `core/legal_notes.py`, and declines to give advice on a
specific case, directing the visitor to the relevant practice and the contact
form instead. Edit `core/legal_notes.py` to extend the legal reference and
`core/knowledge.py` to change the assistant's rules. Questions and answers are
stored in the admin under "Chat logs".

Lawyer photos are loaded from klishin.ru and the map is a Yandex Maps embed, so
those parts need network access to render.
