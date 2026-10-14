"""Telegram assistant: answers questions with the same knowledge as the site chat.

    python manage.py telegram_bot        # long-polls the Bot API until stopped

Runs as the systemd service `klishin-bot` on the server. Conversation
history is kept in memory per chat (last 20 turns); every question and
answer is stored in ChatLog with session_key "tg:<chat id>".
"""
import html
import logging
import re
import time
from collections import defaultdict, deque

import anthropic
from django.conf import settings
from django.core.management.base import BaseCommand

from core import chat
from core.models import ChatLog
from core.telegram import _call
from core.ui import CONTACTS, strings

log = logging.getLogger(__name__)

HISTORY_TURNS = 20
RATE_LIMIT = 20          # messages per chat per hour
CYRILLIC = re.compile('[а-яА-ЯёЁ]')


def detect_lang(text, telegram_code=''):
    if CYRILLIC.search(text or ''):
        return 'ru'
    if text and re.search('[a-zA-Z]', text):
        return 'en'
    return 'ru' if (telegram_code or 'ru').startswith('ru') else 'en'


def to_telegram_html(text, site_url):
    """Claude's light Markdown -> Telegram HTML; relative site links become absolute."""
    out = html.escape(text)
    out = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', out)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        if url.startswith('/'):
            url = site_url.rstrip('/') + url
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'
    out = re.sub(r'\[([^\]]+)\]\(((?:/|https?://)[^)\s]+)\)', link, out)
    out = re.sub(r'^\s*[-*•]\s+', '• ', out, flags=re.M)
    return out


def greeting(lang):
    ui = strings(lang)['chat']
    tips = '\n'.join(f'• {q}' for q in ui['suggestions'])
    return f"{ui['hello']}\n\n{tips}"


def contacts_text(lang):
    ui = strings(lang)
    c = ui['contacts']
    return (f"{ui['brand']}\n{' '.join(c['address'])}\n"
            + '\n'.join(CONTACTS['phones']) + f"\n{CONTACTS['email']}\n{ui['hours']}\n{settings.SITE_URL}")


class Bot:
    def __init__(self, token):
        self.token = token
        self.history = defaultdict(lambda: deque(maxlen=HISTORY_TURNS))
        self.stamps = defaultdict(lambda: deque())
        self.offset = None

    def api(self, method, data):
        old = settings.TELEGRAM_BOT_TOKEN
        settings.TELEGRAM_BOT_TOKEN = self.token
        try:
            return _call(method, data, timeout=45)
        finally:
            settings.TELEGRAM_BOT_TOKEN = old

    def send(self, chat_id, text, html_mode=True):
        data = {'chat_id': chat_id, 'text': text[:4000], 'disable_web_page_preview': True}
        if html_mode:
            data['parse_mode'] = 'HTML'
        try:
            self.api('sendMessage', data)
        except Exception as exc:
            log.warning('telegram_bot: send failed (%s), retrying as plain text', exc)
            data.pop('parse_mode', None)
            try:
                self.api('sendMessage', data)
            except Exception as exc2:
                log.error('telegram_bot: send failed: %s', exc2)

    def allowed(self, chat_id):
        now = time.time()
        q = self.stamps[chat_id]
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return False
        q.append(now)
        return True

    def handle(self, update):
        msg = update.get('message') or update.get('edited_message')
        if not msg or 'text' not in msg:
            return
        chat_id = msg['chat']['id']
        text = msg['text'].strip()
        # Commands carry no language signal: fall back to the Telegram UI language.
        lang = detect_lang('' if text.startswith('/') else text, (msg.get('from') or {}).get('language_code', ''))
        err = strings(lang)

        if text.startswith('/start') or text.startswith('/help'):
            self.history[chat_id].clear()
            return self.send(chat_id, greeting(lang), html_mode=False)
        if text.startswith('/contacts') or text.startswith('/contact'):
            return self.send(chat_id, contacts_text(lang), html_mode=False)
        if text.startswith('/new'):
            self.history[chat_id].clear()
            return self.send(chat_id, '🆕', html_mode=False)
        if text.startswith('/'):
            return self.send(chat_id, greeting(lang), html_mode=False)
        if not self.allowed(chat_id):
            return self.send(chat_id, 'Слишком много вопросов за час, попробуйте позже.' if lang == 'ru'
                             else 'Too many questions this hour, please try again later.', html_mode=False)

        hist = self.history[chat_id]
        hist.append({'role': 'user', 'content': text[:chat.MAX_MESSAGE_CHARS]})
        turns = chat.clean_history(list(hist))
        try:
            reply = chat.ask(turns, lang)
        except anthropic.RateLimitError:
            hist.pop()
            return self.send(chat_id, 'Сервис перегружен, попробуйте через минуту.' if lang == 'ru'
                             else 'The service is busy, please try again in a minute.', html_mode=False)
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
            log.error('telegram_bot: Claude call failed: %s', exc)
            hist.pop()
            return self.send(chat_id, contacts_text(lang), html_mode=False)
        if not reply:
            hist.pop()
            reply = 'На этот вопрос я ответить не могу. Лучше обсудить его с адвокатом коллегии.' if lang == 'ru' \
                else 'I cannot answer that one. It is best discussed with an advocate of the association.'
        else:
            hist.append({'role': 'assistant', 'content': reply})
        ChatLog.objects.create(session_key=f'tg:{chat_id}', language=lang, question=text, answer=reply)
        self.send(chat_id, to_telegram_html(reply, settings.SITE_URL))

    def run(self):
        me = self.api('getMe', {})['result']
        log.info('telegram_bot: running as @%s', me.get('username'))
        while True:
            try:
                data = {'timeout': 30, 'allowed_updates': ['message']}
                if self.offset is not None:
                    data['offset'] = self.offset
                for update in self.api('getUpdates', data).get('result', []):
                    self.offset = update['update_id'] + 1
                    try:
                        self.handle(update)
                    except Exception as exc:  # never let one bad update stop the loop
                        log.exception('telegram_bot: failed to handle update: %s', exc)
            except Exception as exc:
                log.warning('telegram_bot: polling error: %s', exc)
                time.sleep(5)


class Command(BaseCommand):
    help = 'Run the Telegram assistant bot (long polling).'

    def handle(self, *args, **options):
        token = settings.TELEGRAM_ASSISTANT_TOKEN or settings.TELEGRAM_BOT_TOKEN
        if not token:
            self.stderr.write('TELEGRAM_BOT_TOKEN is not set')
            raise SystemExit(1)
        if not chat.enabled():
            self.stderr.write('ANTHROPIC_API_KEY is not set')
            raise SystemExit(1)
        Bot(token).run()
