"""Live press feed from klishin.ru with a 24-hour cache and a database fallback."""
import json
import logging
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone as dj_tz

from .models import PressItem

log = logging.getLogger(__name__)

CACHE_KEY = 'press-feed-v1'

OUTLETS = [
    ('rt.com', 'RT'), ('ria.ru', 'РИА Новости'), ('1prime.ru', 'ПРАЙМ'), ('gazeta.ru', 'Газета.Ru'),
    ('kommersant.ru', 'Коммерсантъ'), ('rbc.ru', 'РБК'), ('vedomosti.ru', 'Ведомости'),
    ('rg.ru', 'Российская газета'), ('tass.ru', 'ТАСС'), ('iz.ru', 'Известия'),
    ('interfax.ru', 'Интерфакс'), ('lenta.ru', 'Lenta.ru'), ('pravo.ru', 'Право.ru'),
    ('rapsinews.ru', 'РАПСИ'), ('forbes.ru', 'Forbes'), ('banki.ru', 'Банки.ру'),
]

TAG_RE = re.compile(r'<[^>]+>')
LINK_RE = re.compile(r'<a[^>]+href=["\'](https?://[^"\']+)["\']', re.I)


def _strip(html):
    return re.sub(r'\s+', ' ', unescape(TAG_RE.sub('', html or ''))).strip()


def _external(html):
    links = [u for u in LINK_RE.findall(html or '') if 'klishin.ru' not in u]
    if not links:
        return None
    for url in links:
        host = (urlparse(url).hostname or '').removeprefix('www.')
        for outlet, name in OUTLETS:
            if host == outlet or host.endswith('.' + outlet):
                return {'url': url, 'source': name}
    host = urlparse(links[0]).hostname or ''
    return {'url': links[0], 'source': host.removeprefix('www.')}


def _parse(posts):
    items = []
    for p in posts:
        try:
            date = datetime.fromisoformat(p['date'])
        except (KeyError, ValueError):
            continue
        content = (p.get('content') or {}).get('rendered', '')
        excerpt = (p.get('excerpt') or {}).get('rendered', '')
        ext = _external(content) or _external(excerpt)
        items.append({
            'date': date.strftime('%d.%m.%Y'),
            'title': _strip((p.get('title') or {}).get('rendered', '')),
            'text': _strip(excerpt)[:220],
            'url': ext['url'] if ext else p.get('link', ''),
            'source': ext['source'] if ext else 'klishin.ru',
        })
    return items


def fetch_live():
    """Return (items, fetched_at) from the cache or the network; None when unavailable."""
    if not settings.PRESS_FEED_ENABLED:
        return None
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached or None
    try:
        req = urllib.request.Request(settings.PRESS_FEED_URL, headers={'User-Agent': 'klishin-site/1.0'})
        with urllib.request.urlopen(req, timeout=settings.PRESS_FEED_TIMEOUT) as resp:
            posts = json.loads(resp.read().decode('utf-8'))
        items = _parse(posts)
    except Exception as exc:  # network errors, bad JSON, unexpected payload
        log.info('press feed unavailable: %s', exc)
        items = []
    result = (items, datetime.now(timezone.utc)) if items else None
    # Cache misses too, so an unreachable feed is not retried on every request.
    cache.set(CACHE_KEY, result or False, settings.PRESS_FEED_TTL if result else 600)
    return result


def press_items(lang, ui):
    """Items for the press page plus the status line underneath them."""
    live = fetch_live()
    if live:
        items, at = live
        local = dj_tz.localtime(at)
        fmt = '%d.%m.%Y, %H:%M'
        return items, ui['press']['status_live'].format(time=local.strftime(fmt))
    saved = [{
        'date': p.date.strftime('%d.%m.%Y'),
        'title': p.t('title', lang),
        'text': p.t('text', lang),
        'url': p.url,
        'source': p.t('source', lang),
    } for p in PressItem.objects.all()]
    return saved, ui['press']['status_saved']
