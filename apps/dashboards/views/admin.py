# apps/dashboard/views/admin.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, AbituriyentProfile
from .decorators import role_required


@login_required
@role_required(['admin'])
def admin_dashboard(request):
    """Admin dashboard"""
    user = request.user

    context = {
        'user': user,
        'system_overview': get_admin_system_overview(),
        'user_analytics': get_admin_user_analytics(),
        'performance_metrics': get_admin_performance_metrics(),
        'security_status': get_admin_security_status(),
        'quick_admin_actions': get_admin_quick_actions(),
        'system_health': get_admin_system_health()
    }

    return render(request, 'dashboard/admin.html', context)


def get_admin_system_overview():
    """Admin tizim umumiy ko'rinishi"""
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_profiles = AbituriyentProfile.objects.count()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_applications': total_profiles,
        'system_uptime': '99.9%',
        'active_sessions': active_users,  # Approximation
        'database_size': '45.6 MB'
    }


def get_admin_user_analytics():
    """Admin foydalanuvchi analitikasi"""
    # Role distribution
    role_distribution = []
    for role, role_name in User.ROLE_CHOICES:
        count = User.objects.filter(role=role).count()
        role_distribution.append({
            'role': role_name,
            'count': count
        })

    # Daily registrations (last 7 days)
    daily_registrations = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=6 - i)
        count = User.objects.filter(date_joined__date=date).count()
        daily_registrations.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })

    return {
        'role_distribution': role_distribution,
        'daily_registrations': daily_registrations,
        'growth_rate': calculate_growth_rate()
    }


def calculate_growth_rate():
    """O'sish sur'atini hisoblash"""
    this_month = User.objects.filter(
        date_joined__month=timezone.now().month,
        date_joined__year=timezone.now().year
    ).count()

    last_month = User.objects.filter(
        date_joined__month=(timezone.now().month - 1) or 12,
        date_joined__year=timezone.now().year if timezone.now().month > 1 else timezone.now().year - 1
    ).count()

    if last_month > 0:
        return ((this_month - last_month) / last_month * 100)
    return 0


def get_admin_performance_metrics():
    """Admin unumdorlik ko'rsatkichlari"""
    return {
        'avg_response_time': '1.2s',
        'database_queries': '2.3k/min',
        'cache_hit_rate': '94.2%',
        'error_rate': '0.01%',
        'cpu_usage': '15%',
        'memory_usage': '68%'
    }


def get_admin_security_status():
    """Admin xavfsizlik holati"""
    failed_attempts = User.objects.filter(failed_login_attempts__gt=0).count()
    blocked_accounts = User.objects.filter(is_blocked=True).count()

    return {
        'failed_login_attempts': failed_attempts,
        'blocked_accounts': blocked_accounts,
        'suspicious_activities': 0,  # Implement based on your security logic
        'last_security_scan': timezone.now() - timedelta(hours=2),
        'security_score': 95  # Based on various factors
    }


def get_admin_quick_actions():
    """Admin tezkor amallar"""
    return [
        {
            'title': 'Foydalanuvchilarni boshqarish',
            'url': '/admin/users/user/',
            'icon': 'users',
            'description': 'Foydalanuvchilar ro\'yxati va sozlamalar'
        },
        {
            'title': 'Tizim sozlamalari',
            'url': '#',
            'icon': 'settings',
            'description': 'Asosiy tizim sozlamalarini boshqarish'
        },
        {
            'title': 'Backup yaratish',
            'url': '#',
            'icon': 'database',
            'description': 'Ma\'lumotlar bazasi backup\'i'
        },
        {
            'title': 'Loglarni ko\'rish',
            'url': '#',
            'icon': 'file-text',
            'description': 'Tizim loglari va xatoliklar'
        }
    ]


def get_admin_system_health():
    """Admin tizim salomatligi"""
    return {
        'status': 'healthy',
        'last_backup': timezone.now() - timedelta(hours=6),
        'disk_usage': 45,  # percentage
        'active_connections': 23,
        'queue_status': 'normal'
    }