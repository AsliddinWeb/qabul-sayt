# apps/dashboard/views/__init__.py
from .main import main_dashboard
from .abituriyent import (
    abituriyent_dashboard,
    passport_view,
    search_passport_data,
    save_passport_data
)
from .operator import operator_dashboard
from .marketing import marketing_dashboard
from .mini_admin import mini_admin_dashboard
from .admin import admin_dashboard
from .api import get_user_stats_ajax, update_profile_completion

__all__ = [
    'main_dashboard',
    'abituriyent_dashboard',
    'passport_view',
    'search_passport_data',
    'save_passport_data',
    'operator_dashboard',
    'marketing_dashboard',
    'mini_admin_dashboard',
    'admin_dashboard',
    'get_user_stats_ajax',
    'update_profile_completion',
]