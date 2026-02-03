from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Specialized App Routes
    path('api/v1/orgs/', include('Org.urls')),
    path('api/v1/academics/', include('academics.urls')),
    
    # Core/Auth Routes (Keep last if it includes greedy patterns, though router usually handles it)
    # This exposes: /api/v1/auth/..., /api/v1/users/, /api/v1/people/
    path('api/v1/', include('Users.urls')),
]
