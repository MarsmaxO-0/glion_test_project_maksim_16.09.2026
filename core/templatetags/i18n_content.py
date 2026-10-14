from django import template
from django.utils import translation

register = template.Library()


@register.filter
def tr(obj, field):
    """``{{ practice|tr:"title" }}`` → the field in the active language."""
    lang = (translation.get_language() or 'ru')[:2]
    return obj.t(field, lang)


@register.filter
def get(mapping, key):
    try:
        return mapping[key]
    except (KeyError, TypeError, IndexError):
        return ''
