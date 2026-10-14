"""Content models for the Klishin & Partners website.

Every piece of visitor-facing text exists in Russian and English, so the
translatable models keep paired ``*_ru`` / ``*_en`` columns and expose
``t(field, lang)`` to pick the right one (falling back to Russian).
"""
from django.db import models
from django.urls import reverse
from django.utils import translation


class Translatable(models.Model):
    class Meta:
        abstract = True

    def t(self, field, lang=None):
        lang = (lang or translation.get_language() or 'ru')[:2]
        value = getattr(self, f'{field}_{lang}', None)
        if value in (None, '', []):
            value = getattr(self, f'{field}_ru', None)
        return value


class PracticeGroup(Translatable):
    order = models.PositiveSmallIntegerField(default=0)
    number = models.CharField(max_length=4, help_text='Display number, e.g. 01')
    title_ru = models.CharField(max_length=120)
    title_en = models.CharField(max_length=120)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.number} {self.title_ru}'


class Practice(Translatable):
    key = models.SlugField(unique=True)
    group = models.ForeignKey(PracticeGroup, on_delete=models.CASCADE, related_name='practices')
    order = models.PositiveSmallIntegerField(default=0)
    title_ru = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160)
    summary_ru = models.TextField()
    summary_en = models.TextField()
    links_to_ip_centre = models.BooleanField(
        default=False,
        help_text='Render as a link to the IP Centre page instead of an expandable item.',
    )

    class Meta:
        ordering = ['group__order', 'order']

    def __str__(self):
        return self.title_ru


class Lawyer(Translatable):
    PRESIDIUM, ADVOCATES, STAFF = 'presidium', 'advocates', 'staff'
    GROUPS = [
        (PRESIDIUM, 'Presidium'),
        (ADVOCATES, 'Advocates'),
        (STAFF, 'Lawyers and administration'),
    ]

    slug = models.SlugField(unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    group = models.CharField(max_length=12, choices=GROUPS)
    on_home = models.BooleanField(default=False, help_text='Show in the Presidium block on the home page.')
    photo = models.ImageField(upload_to='team/', blank=True, help_text='Uploaded photo (preferred).')
    photo_url = models.URLField(blank=True, help_text='External photo URL, used when no file is uploaded.')
    silhouette = models.BooleanField(default=False, help_text='No photo: show a neutral silhouette.')
    practices = models.ManyToManyField(Practice, blank=True, related_name='lawyers')

    name_ru = models.CharField(max_length=120)
    name_en = models.CharField(max_length=120)
    position_ru = models.CharField(max_length=160, help_text='Caption on the team cards.')
    position_en = models.CharField(max_length=160)
    short_role_ru = models.CharField(max_length=120, help_text='Caption in the practice panels.')
    short_role_en = models.CharField(max_length=120)
    kicker_ru = models.CharField(max_length=60, help_text='Small label above the name on the bio page.')
    kicker_en = models.CharField(max_length=60)
    role_ru = models.CharField(max_length=240, help_text='Subtitle on the bio page.')
    role_en = models.CharField(max_length=240)
    registry_ru = models.CharField(max_length=80, blank=True, help_text='Bar registry number.')
    registry_en = models.CharField(max_length=80, blank=True)

    bio_ru = models.JSONField(default=list, help_text='List of paragraphs.')
    bio_en = models.JSONField(default=list)
    extra_title_ru = models.CharField(max_length=120, blank=True)
    extra_title_en = models.CharField(max_length=120, blank=True)
    extra_ru = models.JSONField(default=list, blank=True, help_text='Paragraphs of the second section.')
    extra_en = models.JSONField(default=list, blank=True)
    specialisation_ru = models.JSONField(default=list, blank=True)
    specialisation_en = models.JSONField(default=list, blank=True)
    awards_title_ru = models.CharField(max_length=120, blank=True)
    awards_title_en = models.CharField(max_length=120, blank=True)
    awards_ru = models.JSONField(default=list, blank=True)
    awards_en = models.JSONField(default=list, blank=True)
    news_ru = models.JSONField(default=list, blank=True, help_text='List of [date, title] pairs.')
    news_en = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name_ru

    def get_absolute_url(self):
        return reverse('core:lawyer', kwargs={'slug': self.slug})

    @property
    def photo_src(self):
        """URL of the photo to show: the uploaded file first, then the external link, else empty."""
        if self.photo:
            return self.photo.url
        return '' if self.silhouette else self.photo_url


class Case(Translatable):
    order = models.PositiveSmallIntegerField(default=0)
    title_ru = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    text_ru = models.TextField()
    text_en = models.TextField()
    on_home = models.BooleanField(default=False)
    home_order = models.PositiveSmallIntegerField(default=0)
    home_title_ru = models.CharField(max_length=200, blank=True)
    home_title_en = models.CharField(max_length=200, blank=True)
    home_text_ru = models.TextField(blank=True)
    home_text_en = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title_ru

    @property
    def number(self):
        return f'{self.order:02d}'


class PracticeHighlight(Translatable):
    """The four practice cards on the home page."""
    order = models.PositiveSmallIntegerField(default=0)
    label_ru = models.CharField(max_length=60)
    label_en = models.CharField(max_length=60)
    title_ru = models.CharField(max_length=120)
    title_en = models.CharField(max_length=120)
    text_ru = models.TextField()
    text_en = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title_ru


class PressItem(Translatable):
    """Saved press items: shown on the home page and whenever the live feed is unavailable."""
    date = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    title_ru = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    text_ru = models.TextField(blank=True)
    text_en = models.TextField(blank=True)
    byline_ru = models.CharField(max_length=160, blank=True, help_text='e.g. Денис Талызин — RT')
    byline_en = models.CharField(max_length=160, blank=True)
    source_ru = models.CharField(max_length=120, blank=True)
    source_en = models.CharField(max_length=120, blank=True)
    url = models.URLField(blank=True)
    on_home = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', 'order']

    def __str__(self):
        return self.title_ru


class Publication(Translatable):
    order = models.PositiveSmallIntegerField(default=0)
    author_ru = models.CharField(max_length=160)
    author_en = models.CharField(max_length=160)
    title_ru = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    url = models.URLField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title_ru


class ResearchItem(Translatable):
    order = models.PositiveSmallIntegerField(default=0)
    title_ru = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160)
    text_ru = models.TextField()
    text_en = models.TextField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title_ru


class IpArea(Translatable):
    """Areas of the Centre for the Legal Protection of IP."""
    order = models.PositiveSmallIntegerField(default=0)
    short_ru = models.CharField(max_length=120, help_text='Wording used on the home page.')
    short_en = models.CharField(max_length=120)
    full_ru = models.CharField(max_length=240, blank=True, help_text='Wording used on the IP Centre page (empty: not shown there).')
    full_en = models.CharField(max_length=240, blank=True)
    on_home = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.short_ru


class ContactMessage(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, default='ru')
    name = models.CharField(max_length=120)
    contact = models.CharField(max_length=160, help_text='Phone or e-mail')
    message = models.TextField()
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} · {self.created:%d.%m.%Y}'


class ChatLog(models.Model):
    """Questions asked to the site assistant and the answers given."""
    created = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=64, blank=True)
    language = models.CharField(max_length=2, default='ru')
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.created:%d.%m.%Y %H:%M} · {self.question[:60]}'
