from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from .models import Lawyer

LANGS = ('ru', 'en')


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8
    names = ['core:home', 'core:practices', 'core:team', 'core:cases', 'core:ip', 'core:press', 'core:contacts']

    def items(self):
        return [(lang, name) for lang in LANGS for name in self.names]

    def location(self, item):
        lang, name = item
        with translation.override(lang):
            return reverse(name)


class LawyerSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return [(lang, l) for lang in LANGS for l in Lawyer.objects.all()]

    def location(self, item):
        lang, lawyer = item
        with translation.override(lang):
            return lawyer.get_absolute_url()


SITEMAPS = {'static': StaticSitemap, 'lawyers': LawyerSitemap}
