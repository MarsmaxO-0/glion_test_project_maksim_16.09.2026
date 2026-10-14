"""Download lawyers' external photos (photo_url) into the media folder.

    python manage.py fetch_photos          # only lawyers without an uploaded photo
    python manage.py fetch_photos --force  # re-download everything
"""
import urllib.request
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import Lawyer


class Command(BaseCommand):
    help = "Download lawyers' photos from photo_url into MEDIA_ROOT/team/."

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Replace photos that are already uploaded.')

    def handle(self, *args, **options):
        done = failed = 0
        for lawyer in Lawyer.objects.exclude(photo_url=''):
            if lawyer.photo and not options['force']:
                continue
            try:
                req = urllib.request.Request(lawyer.photo_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                    'Referer': 'https://klishin.ru/',
                })
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
            except Exception as exc:  # network errors, 404s
                failed += 1
                self.stderr.write(f'{lawyer.slug}: {exc}')
                continue
            ext = PurePosixPath(unquote(urlparse(lawyer.photo_url).path)).suffix.lower() or '.jpg'
            lawyer.photo.save(f'{lawyer.slug}{ext}', ContentFile(data), save=True)
            done += 1
            self.stdout.write(f'{lawyer.slug}: saved {lawyer.photo.name} ({len(data) // 1024} KB)')
        self.stdout.write(f'{done} photo(s) saved, {failed} failed')
        if failed:
            raise SystemExit(1)
