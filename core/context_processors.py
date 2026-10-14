from django.urls import translate_url
from django.utils import translation

from . import chat
from .ui import CONTACTS, strings, tel_href


def site(request):
    lang = (translation.get_language() or 'ru')[:2]
    path = request.get_full_path()
    return {
        'lang': lang,
        'ui': strings(lang),
        'contacts': CONTACTS,
        'phone_hrefs': [(p, tel_href(p)) for p in CONTACTS['phones']],
        'lang_urls': {code: translate_url(path, code) for code in ('ru', 'en')},
        'nav_active': getattr(request, 'nav_active', ''),
        'chat_enabled': chat.enabled(),
    }
