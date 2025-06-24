# apps/dashboard/views/__init__.py
from .main import main_dashboard
from .abituriyent import (
    abituriyent_dashboard,
    passport_view,
    load_districts,
    diplom_page,
    transfer_diplom_page,
    apply_page,
    application_status,
    application_history,
    quick_apply,
    withdraw_application,
    load_programs
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
    'transfer_diplom_page',
    'load_districts',
    'operator_dashboard',
    'marketing_dashboard',
    'mini_admin_dashboard',
    'admin_dashboard',
    'apply_page',
    'application_status',
    'application_history',
    'quick_apply',
    'withdraw_application',
    'load_programs',
]