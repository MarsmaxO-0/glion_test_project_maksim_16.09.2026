from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.api import chat_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_api, name='chat_api'),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=True,
)

# Uploaded photos in development (nginx serves /media/ in production).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
