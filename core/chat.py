"""Claude-powered site assistant."""
import logging

import anthropic
from django.conf import settings
from django.core.cache import cache

from .knowledge import system_prompt

log = logging.getLogger(__name__)

MAX_HISTORY = 20          # messages kept from the client-side history
MAX_MESSAGE_CHARS = 2000
PROMPT_CACHE_KEY = 'chat-system-prompt-{lang}'


def enabled():
    return bool(settings.ANTHROPIC_API_KEY)


def _system(lang):
    """The system prompt is built from the database; keep it stable so the API's prompt cache hits."""
    key = PROMPT_CACHE_KEY.format(lang=lang)
    text = cache.get(key)
    if text is None:
        text = system_prompt(lang)
        cache.set(key, text, settings.CHAT_PROMPT_TTL)
    return text


_client = None


def client():
    """One SDK client per process with a bounded wait: gunicorn kills a worker after 120 s."""
    global _client
    if _client is None or _client.api_key != settings.ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0, max_retries=1)
    return _client


def clean_history(raw):
    """Keep only well-formed alternating user/assistant text turns, ending with a user turn."""
    if not isinstance(raw, list):
        return []
    turns = []
    for m in raw[-MAX_HISTORY:]:
        if not isinstance(m, dict):
            continue
        role, content = m.get('role'), m.get('content')
        if role not in ('user', 'assistant') or not isinstance(content, str) or not content.strip():
            continue
        content = content.strip()[:MAX_MESSAGE_CHARS]
        if turns and turns[-1]['role'] == role:
            turns[-1]['content'] += '\n' + content
        else:
            turns.append({'role': role, 'content': content})
    while turns and turns[0]['role'] != 'user':
        turns.pop(0)
    if not turns or turns[-1]['role'] != 'user':
        return []
    return turns


def ask(history, lang):
    """Return the assistant's reply text for the given conversation."""
    response = client().beta.messages.create(
        model=settings.CHAT_MODEL,
        max_tokens=1024,
        output_config={'effort': 'low'},   # chat: short answers, fast
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',               # a safety decline is re-run on a fallback model
        system=[{'type': 'text', 'text': _system(lang), 'cache_control': {'type': 'ephemeral'}}],
        messages=history,
    )
    if response.stop_reason == 'refusal':
        return None
    return ''.join(b.text for b in response.content if b.type == 'text').strip() or None
