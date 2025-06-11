# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.main_dashboard, name='main'),

    # Abituriyent URLs
    path('abituriyent/', views.abituriyent_dashboard, name='abituriyent'),
    path('abituriyent/passport/', views.passport_view, name='passport'),

    # AJAX endpoints
    path('api/search-passport/', views.search_passport_data, name='search_passport_data'),
    path('api/save-passport/', views.save_passport_data, name='save_passport_data'),

    # Other dashboards
    path('operator/', views.operator_dashboard, name='operator'),
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('mini-admin/', views.mini_admin_dashboard, name='mini_admin'),
    path('admin/', views.admin_dashboard, name='admin'),

    # API endpoints
    path('api/stats/', views.get_user_stats_ajax, name='user_stats'),
    path('api/profile-completion/', views.update_profile_completion, name='profile_completion'),
]
