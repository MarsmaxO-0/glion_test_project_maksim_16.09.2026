"""Minimal Telegram Bot API client (notifications, backup delivery). No extra dependencies."""
import json
import logging
import mimetypes
import urllib.request
import uuid
from pathlib import Path

from django.conf import settings

log = logging.getLogger(__name__)
API = 'https://api.telegram.org/bot{token}/{method}'


def enabled():
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_ADMIN_CHAT_ID)


def _call(method, data=None, files=None, timeout=30):
    url = API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    if files:
        boundary = uuid.uuid4().hex
        body = b''
        for k, v in (data or {}).items():
            body += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, path in files.items():
            path = Path(path)
            ctype = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{path.name}"\r\n'
                     f'Content-Type: {ctype}\r\n\r\n').encode() + path.read_bytes() + b'\r\n'
        body += f'--{boundary}--\r\n'.encode()
        req = urllib.request.Request(url, data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    else:
        req = urllib.request.Request(url, data=json.dumps(data or {}).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def send_message(text, chat_id=None):
    """Send a text message to the admin chat. Never raises: notification failures must not break the site."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return False
    try:
        _call('sendMessage', {'chat_id': chat_id or settings.TELEGRAM_ADMIN_CHAT_ID, 'text': text[:4000],
                              'disable_web_page_preview': True})
        return True
    except Exception as exc:
        log.warning('telegram: could not send message: %s', exc)
        return False


def send_document(path, caption='', chat_id=None):
    if not settings.TELEGRAM_BOT_TOKEN:
        return False
    try:
        _call('sendDocument', {'chat_id': chat_id or settings.TELEGRAM_ADMIN_CHAT_ID, 'caption': caption[:1000]},
              files={'document': path}, timeout=120)
        return True
    except Exception as exc:
        log.warning('telegram: could not send document: %s', exc)
        return False
