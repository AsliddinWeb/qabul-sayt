# apps/dashboard/urls.py - Cleaned version
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.main_dashboard, name='main'),

    # Abituriyent main pages
    path('abituriyent/', views.abituriyent_dashboard, name='abituriyent'),
    path('abituriyent/passport/', views.passport_view, name='abituriyent_passport'),
    path('abituriyent/profile/', views.passport_view, name='abituriyent_profile'),  # Alias
    
    # Document pages
    path('abituriyent/diplom/', views.diplom_page, name='abituriyent_diplom'),
    path('abituriyent/transfer-diplom/', views.transfer_diplom_page, name='abituriyent_transfer_diplom'),

    # Application pages
    path('abituriyent/apply/', views.apply_page, name='abituriyent_apply'),
    path('abituriyent/status/', views.application_status, name='abituriyent_status'),
    path('abituriyent/history/', views.application_history, name='abituriyent_history'),
    path('abituriyent/quick-apply/', views.quick_apply, name='abituriyent_quick_apply'),

    # Application actions
    path('abituriyent/withdraw/', views.withdraw_application, name='abituriyent_withdraw'),

    # Essential AJAX endpoints only
    path('abituriyent/ajax/load-districts/', views.load_districts, name='abituriyent_load_districts'),
    path('abituriyent/ajax/load-programs/', views.load_programs, name='abituriyent_load_programs'),

    # Other dashboards
    path('operator/', views.operator_dashboard, name='operator'),
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('mini-admin/', views.mini_admin_dashboard, name='mini_admin'),
    path('admin/', views.admin_dashboard, name='admin'),
]