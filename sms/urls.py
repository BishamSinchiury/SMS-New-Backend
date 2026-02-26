from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Specialized App Routes
    path('api/v1/orgs/', include('Org.urls')),
    
    # Core/Auth Routes (Keep last if it includes greedy patterns, though router usually handles it)
    # This exposes: /api/v1/auth/..., /api/v1/users/, /api/v1/people/
    path('api/v1/', include('Users.urls')),
    path('api/v1/academic/', include('academic.urls')),
    path('api/v1/people/', include('people.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
