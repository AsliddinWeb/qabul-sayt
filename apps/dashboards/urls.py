from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.main_dashboard, name='main'),

    # Role-specific dashboards
    path('abituriyent/', views.abituriyent_dashboard, name='abituriyent'),
    path('operator/', views.operator_dashboard, name='operator'),
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('mini-admin/', views.mini_admin_dashboard, name='mini_admin'),
    path('admin/', views.admin_dashboard, name='admin'),

    # AJAX endpoints
    path('api/user-stats/', views.get_user_stats_ajax, name='user_stats_ajax'),
    path('api/profile-completion/', views.update_profile_completion, name='profile_completion'),
]