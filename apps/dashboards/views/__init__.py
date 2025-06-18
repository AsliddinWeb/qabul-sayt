# apps/dashboard/views/__init__.py
from .main import main_dashboard
from .abituriyent import (
   abituriyent_dashboard,
   passport_view,
   search_passport_data,
   save_passport_data,
   load_districts,
   applications_ajax,
   profile_completion_ajax,
   dashboard_stats_ajax,
   diplom_page,
)
from .operator import operator_dashboard
from .marketing import marketing_dashboard
from .mini_admin import mini_admin_dashboard
from .admin import admin_dashboard

__all__ = [
   'main_dashboard',
   'abituriyent_dashboard',
   'passport_view',
   'diplom_page',
   'search_passport_data',
   'save_passport_data',
   'load_districts',
   'applications_ajax',
   'profile_completion_ajax',
   'dashboard_stats_ajax',
   'operator_dashboard',
   'marketing_dashboard',
   'mini_admin_dashboard',
   'admin_dashboard',
]