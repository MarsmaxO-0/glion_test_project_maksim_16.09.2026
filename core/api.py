import json
import logging

import anthropic
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from . import chat
from .models import ChatLog

log = logging.getLogger(__name__)

CHAT_LIMIT_PER_HOUR = 20


def _over_limit(request):
    """At most CHAT_LIMIT_PER_HOUR questions per browser session (or IP when there is no session)."""
    if not request.session.session_key:
        request.session.save()
    key = f"chat-rate:{request.session.session_key or request.META.get('REMOTE_ADDR', '')}"
    count = cache.get(key, 0)
    if count >= CHAT_LIMIT_PER_HOUR:
        return True
    cache.set(key, count + 1, 3600)
    return False


ERRORS = {
    'ru': {
        'disabled': 'Чат временно недоступен.',
        'bad': 'Не удалось прочитать сообщение.',
        'busy': 'Слишком много запросов, попробуйте через минуту.',
        'fail': 'Не удалось получить ответ. Позвоните нам: +7 (495) 974-73-10.',
        'refused': 'На этот вопрос я ответить не могу. Лучше обсудить его с адвокатом коллегии.',
    },
    'en': {
        'disabled': 'The chat is temporarily unavailable.',
        'bad': 'Could not read the message.',
        'busy': 'Too many requests, please try again in a minute.',
        'fail': 'Could not get an answer. Call us: +7 (495) 974-73-10.',
        'refused': 'I cannot answer that one. It is best discussed with an advocate of the association.',
    },
}


@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except ValueError:
        payload = None
    lang = 'en' if (payload or {}).get('lang') == 'en' else 'ru'
    err = ERRORS[lang]
    if not chat.enabled():
        return JsonResponse({'error': err['disabled']}, status=503)
    if not isinstance(payload, dict):
        return JsonResponse({'error': err['bad']}, status=400)
    history = chat.clean_history(payload.get('messages') or [])
    if not history:
        return JsonResponse({'error': err['bad']}, status=400)
    if _over_limit(request):
        return JsonResponse({'error': err['busy']}, status=429)
    try:
        reply = chat.ask(history, lang)
    except anthropic.RateLimitError as exc:
        log.warning('chat: rate limited by the Claude API: %s', exc)
        return JsonResponse({'error': err['busy']}, status=429)
    except anthropic.AuthenticationError as exc:
        log.error('chat: the Claude API rejected ANTHROPIC_API_KEY: %s', exc)
        return JsonResponse({'error': err['fail']}, status=502)
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
        log.error('chat: Claude API call failed: %s', exc)
        return JsonResponse({'error': err['fail']}, status=502)
    if reply is None:
        reply = err['refused']
    if not request.session.session_key:
        request.session.save()
    ChatLog.objects.create(
        session_key=request.session.session_key or '', language=lang,
        question=history[-1]['content'], answer=reply,
    )
    return JsonResponse({'reply': reply})
