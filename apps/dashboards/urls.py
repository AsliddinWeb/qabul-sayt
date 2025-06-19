# apps/dashboard/urls.py
from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.main_dashboard, name='main'),

    # Abituriyent URLs
    path('abituriyent/', views.abituriyent_dashboard, name='abituriyent'),
    path('abituriyent/passport/', views.passport_view, name='abituriyent_passport'),
    path('abituriyent/profile/', views.passport_view, name='abituriyent_profile'),

    path('abituriyent/diplom/', views.diplom_page, name='abituriyent_diplom'),
    path('abituriyent/transfer-diplom/', views.transfer_diplom_page, name='abituriyent_transfer_diplom'),

    # Asosiy ariza sahifalari
    path('apply/', views.apply_page, name='abituriyent_apply'),
    path('status/', views.application_status, name='abituriyent_status'),
    path('history/', views.application_history, name='abituriyent_history'),
    path('load-programs/', views.load_programs, name='abituriyent_load_programs'),

    # Tezkor ariza
    path('quick-apply/', views.quick_apply, name='abituriyent_quick_apply'),

    # Ariza amalllari
    path('withdraw/', views.withdraw_application, name='abituriyent_withdraw'),

    # AJAX endpoints
    path('abituriyent/ajax/search-passport/', views.search_passport_data, name='abituriyent_search_passport'),
    path('abituriyent/ajax/save-passport/', views.save_passport_data, name='abituriyent_save_passport'),
    path('abituriyent/ajax/load-districts/', views.load_districts, name='abituriyent_load_districts'),
    path('abituriyent/ajax/applications/', views.applications_ajax, name='abituriyent_applications_ajax'),
    path('abituriyent/ajax/profile-completion/', views.profile_completion_ajax, name='abituriyent_profile_completion'),
    path('abituriyent/ajax/dashboard-stats/', views.dashboard_stats_ajax, name='abituriyent_dashboard_stats'),

    # Other dashboards
    path('operator/', views.operator_dashboard, name='operator'),
    path('marketing/', views.marketing_dashboard, name='marketing'),
    path('mini-admin/', views.mini_admin_dashboard, name='mini_admin'),
    path('admin/', views.admin_dashboard, name='admin'),
]