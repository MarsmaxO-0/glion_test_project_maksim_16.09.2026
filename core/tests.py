from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import ContactMessage, Lawyer, Practice, PracticeGroup, PressItem


class ContentMixin:
    @classmethod
    def setUpTestData(cls):
        group = PracticeGroup.objects.create(order=1, number='01', title_ru='Споры', title_en='Disputes')
        cls.practice = Practice.objects.create(
            key='arb', group=group, order=1, title_ru='Арбитраж', title_en='Arbitration',
            summary_ru='Описание', summary_en='Summary')
        cls.lawyer = Lawyer.objects.create(
            slug='ivanov', order=1, group=Lawyer.PRESIDIUM, on_home=True, photo_url='https://example.com/p.jpg',
            name_ru='Иванов Иван Иванович', name_en='Ivan I. Ivanov',
            position_ru='Председатель', position_en='Chairman', short_role_ru='Председатель', short_role_en='Chairman',
            kicker_ru='Президиум', kicker_en='Presidium', role_ru='Председатель коллегии', role_en='Chairman',
            registry_ru='77/1', registry_en='77/1', bio_ru=['Абзац один.'], bio_en=['Paragraph one.'],
            extra_title_ru='Проекты', extra_title_en='Matters', extra_ru=['Проект.'], extra_en=['Matter.'],
            specialisation_ru=['Арбитраж'], specialisation_en=['Arbitration'],
            awards_ru=['Грамота'], awards_en=['Certificate'], news_ru=[['01.01.2024', 'Новость']], news_en=[['01.01.2024', 'News']])
        cls.lawyer.practices.add(cls.practice)
        PressItem.objects.create(date='2026-03-17', title_ru='Заголовок', title_en='Headline', source_ru='RT', source_en='RT',
                                 url='https://example.com/a', on_home=True)


class PagesTest(ContentMixin, TestCase):
    def test_root_redirects_to_russian(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/ru/')

    def test_all_pages_render_in_both_languages(self):
        names = ['home', 'practices', 'team', 'cases', 'ip', 'press', 'contacts']
        for lang in ('ru', 'en'):
            with translation.override(lang):
                for name in names:
                    with self.subTest(lang=lang, page=name):
                        resp = self.client.get(reverse(f'core:{name}'))
                        self.assertEqual(resp.status_code, 200)
                        self.assertContains(resp, f'<html lang="{lang}">')

    def test_home_shows_presidium_in_active_language(self):
        self.assertContains(self.client.get('/ru/'), 'Иванов Иван Иванович')
        self.assertContains(self.client.get('/en/'), 'Ivan I. Ivanov')

    def test_lawyer_page(self):
        resp = self.client.get('/en/team/ivanov/')
        self.assertContains(resp, 'Paragraph one.')
        self.assertContains(resp, 'Matters')
        self.assertContains(resp, 'Certificate')
        self.assertEqual(self.client.get('/en/team/nobody/').status_code, 404)

    def test_practice_panel_lists_lawyers(self):
        resp = self.client.get('/ru/practices/?open=arb')
        self.assertContains(resp, 'id="panel-arb"')
        self.assertContains(resp, '/ru/team/ivanov/')

    def test_press_falls_back_to_saved_items(self):
        with self.settings(PRESS_FEED_ENABLED=False):
            resp = self.client.get('/en/press/')
        self.assertContains(resp, 'Headline')
        self.assertContains(resp, 'Showing the saved list')

    def test_language_switch_keeps_page(self):
        resp = self.client.get('/ru/team/ivanov/')
        self.assertContains(resp, 'href="/en/team/ivanov/"')


class ContactFormTest(ContentMixin, TestCase):
    def test_valid_message_is_saved(self):
        resp = self.client.post('/ru/contacts/', {'name': 'Анна', 'contact': '+7 900 000-00-00', 'message': 'Вопрос'})
        self.assertRedirects(resp, '/ru/contacts/?sent=1#contact-form', fetch_redirect_response=False)
        msg = ContactMessage.objects.get()
        self.assertEqual(msg.language, 'ru')
        self.assertEqual(msg.name, 'Анна')

    def test_invalid_message_is_rejected(self):
        resp = self.client.post('/en/contacts/', {'name': '', 'contact': '', 'message': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Please check the fields.')
        self.assertFalse(ContactMessage.objects.exists())

    def test_honeypot_blocks_bots(self):
        self.client.post('/en/contacts/', {'name': 'Bot', 'contact': 'x', 'message': 'y', 'website': 'http://spam'})
        self.assertFalse(ContactMessage.objects.exists())
