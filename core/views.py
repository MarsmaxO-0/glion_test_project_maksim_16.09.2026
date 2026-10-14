from django.shortcuts import get_object_or_404, redirect, render
from django.utils import translation

from . import press as press_feed
from .forms import ContactForm
from .models import (
    Case, IpArea, Lawyer, Practice, PracticeGroup, PracticeHighlight, PressItem, Publication, ResearchItem,
)
from .ui import CONTACTS, strings


def _render(request, template, nav, **ctx):
    request.nav_active = nav
    return render(request, template, ctx)


def home(request):
    return _render(
        request, 'core/home.html', 'home',
        highlights=PracticeHighlight.objects.all(),
        presidium=Lawyer.objects.filter(on_home=True),
        cases=Case.objects.filter(on_home=True).order_by('home_order'),
        press=PressItem.objects.filter(on_home=True)[:3],
        ip_areas=IpArea.objects.filter(on_home=True),
    )


def practices(request):
    groups = PracticeGroup.objects.prefetch_related('practices__lawyers')
    open_key = request.GET.get('open', '')
    return _render(request, 'core/practices.html', 'practices', groups=groups, open_key=open_key)


def team(request):
    lawyers = list(Lawyer.objects.all())
    groups = [(key, [l for l in lawyers if l.group == key]) for key, _ in Lawyer.GROUPS]
    return _render(request, 'core/team.html', 'team', groups=groups)


def lawyer(request, slug):
    person = get_object_or_404(Lawyer, slug=slug)
    lang = (translation.get_language() or 'ru')[:2]
    ui = strings(lang)
    sections = [(ui['lawyer']['bio'], person.t('bio', lang))]
    if person.t('extra', lang):
        sections.append((person.t('extra_title', lang), person.t('extra', lang)))
    return _render(
        request, 'core/lawyer.html', 'team',
        person=person, sections=sections,
        awards_title=person.t('awards_title', lang) or ui['lawyer']['awards'],
        # Non-award side lists (services, languages) have no medal icon.
        awards_with_icon=not person.t('awards_title', lang),
    )


def cases(request):
    return _render(request, 'core/cases.html', 'cases', cases=Case.objects.all())


def ip_centre(request):
    director = Lawyer.objects.filter(slug='entin').first()
    return _render(
        request, 'core/ip.html', 'ip',
        areas=[a for a in IpArea.objects.all() if a.full_ru],
        director=director,
    )


def press(request):
    lang = (translation.get_language() or 'ru')[:2]
    items, status = press_feed.press_items(lang, strings(lang))
    return _render(
        request, 'core/press.html', 'press',
        items=items, status=status,
        publications=Publication.objects.all(),
        research=ResearchItem.objects.all(),
    )


def contacts(request):
    lang = (translation.get_language() or 'ru')[:2]
    ui = strings(lang)['contacts']
    labels = {'name': ui['form_name'], 'contact': ui['form_contact'], 'message': ui['form_message']}
    if request.method == 'POST':
        form = ContactForm(request.POST, labels=labels)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.language = lang
            msg.save()
            return redirect(f"{request.path}?sent=1#contact-form")
    else:
        form = ContactForm(labels=labels)
    return _render(
        request, 'core/contacts.html', 'contacts',
        form=form, sent=request.GET.get('sent') == '1',
        map_url=CONTACTS[f'map_{lang}'],
    )
