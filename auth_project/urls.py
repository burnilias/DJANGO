from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse, Http404
import os

def frontend_view(request, file_path=''):
    """Serve files from the frontend/ directory at the site root."""
    frontend_dir = settings.BASE_DIR / 'frontend'
    if not file_path:
        file_path = 'index.html'
    # Security: prevent directory traversal
    full_path = os.path.normpath(os.path.join(str(frontend_dir), file_path))
    if not full_path.startswith(str(frontend_dir)):
        raise Http404
    if not os.path.isfile(full_path):
        raise Http404
    return serve(request, path=file_path, document_root=str(frontend_dir))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += [
        re_path(r'^(?P<file_path>(?:css|js|html|img)/.*)$', frontend_view),
        re_path(r'^(?P<file_path>index\.html)$', frontend_view),
        path('', frontend_view, {'file_path': ''}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all for frontend routes (React Router handles these)
urlpatterns += [
    re_path(r'^(?!api/|admin/|media/).*$', frontend_view, {'file_path': ''}),
]
