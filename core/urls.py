from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('apps.users.urls')),

    # Home
    path('', include('apps.pages.urls')),

    # Auth
    path('auth/', include('apps.users.urls')),

    # Dashboard
    path('dashboard/', include('apps.dashboards.urls')),

    # Regions
    path('regions/', include('apps.regions.urls')),

    # Application api
    path('applications/', include('apps.applications.urls')),

]


# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

