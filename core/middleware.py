from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from django.utils import translation

from .ui import strings


class MaintenanceMiddleware:
    """Serve the maintenance page while the flag file exists (admin and health check stay reachable).

    Turn on:  touch /opt/klishin/MAINTENANCE
    Turn off: rm /opt/klishin/MAINTENANCE
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        flag = Path(settings.MAINTENANCE_FILE)
        if flag.exists() and not request.path.startswith(('/admin', '/healthz', settings.STATIC_URL)):
            lang = 'en' if request.path.startswith('/en') else 'ru'
            with translation.override(lang):
                resp = render(request, 'core/maintenance.html', {'ui': strings(lang), 'lang': lang}, status=503)
            resp['Retry-After'] = '600'
            return resp
        return self.get_response(request)
