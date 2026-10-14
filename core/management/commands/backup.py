"""Back up the database and uploaded files.

    python manage.py backup              # writes BACKUP_DIR/klishin-YYYYmmdd-HHMM.tar.gz, keeps the last BACKUP_KEEP
    python manage.py backup --no-upload  # skip sending the archive to Telegram

The SQLite file is copied with the online backup API, so it is consistent
even while the site is running. If TELEGRAM_BOT_TOKEN and
TELEGRAM_ADMIN_CHAT_ID are set, the archive is also sent to that chat, which
keeps a copy outside the server.
"""
import sqlite3
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from core import telegram


class Command(BaseCommand):
    help = 'Back up db.sqlite3 and media/ into a tar.gz, prune old copies, send to Telegram.'

    def add_arguments(self, parser):
        parser.add_argument('--no-upload', action='store_true')

    def handle(self, *args, **options):
        out_dir = Path(settings.BACKUP_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M')
        archive = out_dir / f'klishin-{stamp}.tar.gz'

        with tempfile.TemporaryDirectory() as tmp:
            db_copy = Path(tmp) / 'db.sqlite3'
            db_name = str(settings.DATABASES['default']['NAME'])
            if 'memory' in db_name:  # test database: dump SQL instead of copying a file
                connection.ensure_connection()
                db_copy = Path(tmp) / 'db.sql'
                db_copy.write_text('\n'.join(connection.connection.iterdump()), encoding='utf-8')
            else:
                src = sqlite3.connect(db_name)
                dst = sqlite3.connect(db_copy)
                with dst:
                    src.backup(dst)  # SQLite online backup: consistent while the site runs
                src.close(); dst.close()
            with tarfile.open(archive, 'w:gz') as tar:
                tar.add(db_copy, arcname=db_copy.name)
                media = Path(settings.MEDIA_ROOT)
                if media.exists():
                    tar.add(media, arcname='media')
        size_kb = archive.stat().st_size // 1024
        self.stdout.write(f'wrote {archive} ({size_kb} KB)')

        old = sorted(out_dir.glob('klishin-*.tar.gz'))[:-settings.BACKUP_KEEP]
        for f in old:
            f.unlink()
        if old:
            self.stdout.write(f'removed {len(old)} old backup(s)')

        if not options['no_upload'] and telegram.enabled():
            ok = telegram.send_document(archive, caption=f'Backup {stamp} · {size_kb} KB')
            self.stdout.write('sent to Telegram' if ok else 'Telegram upload failed (see log)')
