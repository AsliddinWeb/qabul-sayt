# apps/regions/urls.py

from django.urls import path
from . import views

app_name = 'regions'

urlpatterns = [
    path('', views.get_regions, name='get_regions'),
    path('districts/', views.get_districts, name='get_districts'),
    path('<int:region_id>/', views.get_region_with_districts, name='get_region_with_districts'),
]