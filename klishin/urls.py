from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from core.api import chat_api
from core.sitemaps import SITEMAPS
from core.views import healthz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_api, name='chat_api'),
    path('healthz/', healthz, name='healthz'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('robots.txt', lambda r: HttpResponse(
        f"User-agent: *\nDisallow: /admin/\nDisallow: /api/\nSitemap: {settings.SITE_URL.rstrip('/')}/sitemap.xml\n",
        content_type='text/plain')),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=True,
)

# Uploaded photos in development (nginx serves /media/ in production).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = 'core.views.server_error'
