# apps/dashboard/views/mini_admin.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from apps.regions.models import Region
from .decorators import role_required


@login_required
@role_required(['mini_admin'])
def mini_admin_dashboard(request):
    """Mini Admin dashboard"""
    user = request.user

    context = {
        'user': user,
        'region_stats': get_mini_admin_region_stats(user),
        'user_management': get_mini_admin_user_stats(),
        'system_alerts': get_mini_admin_alerts(),
        'recent_activities': get_mini_admin_activities(),
        'pending_tasks': get_mini_admin_tasks()
    }

    return render(request, 'dashboard/mini_admin.html', context)


def get_mini_admin_region_stats(user):
    """Mini admin hududiy statistikalari"""
    try:
        profile = user.mini_admin_profile
        # Agar MiniAdminProfile'da managed_regions bo'lsa
        if hasattr(profile, 'managed_regions'):
            managed_regions = profile.managed_regions.all()
        else:
            managed_regions = Region.objects.all()[:3]  # Placeholder

        return {
            'managed_regions_count': managed_regions.count(),
            'total_users_in_regions': User.objects.filter(
                abituriyent_profile__region__in=managed_regions
            ).count() if managed_regions else 0,
            'pending_applications': 0  # Application model bo'yicha
        }
    except:
        return {
            'managed_regions_count': 0,
            'total_users_in_regions': 0,
            'pending_applications': 0
        }


def get_mini_admin_user_stats():
    """Mini admin foydalanuvchi statistikalari"""
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    blocked_users = User.objects.filter(is_blocked=True).count()
    new_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()

    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'blocked_users': blocked_users,
        'new_today': new_today,
        'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0
    }


def get_mini_admin_alerts():
    """Mini admin ogohlantirishlari"""
    blocked_count = User.objects.filter(is_blocked=True).count()
    failed_attempts = User.objects.filter(failed_login_attempts__gt=0).count()

    alerts = []
    if blocked_count > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{blocked_count} ta foydalanuvchi bloklangan',
            'action_url': '#'
        })

    if failed_attempts > 0:
        alerts.append({
            'type': 'info',
            'message': f'{failed_attempts} ta foydalanuvchida login muammolari',
            'action_url': '#'
        })

    return alerts


def get_mini_admin_activities():
    """Mini admin so'nggi faoliyatlar"""
    return [
        {'action': 'Yangi operator tayinlandi', 'time': timezone.now() - timedelta(minutes=30)},
        {'action': 'Tizim sozlamalari yangilandi', 'time': timezone.now() - timedelta(hours=2)},
        {'action': 'Hisobot yaratildi', 'time': timezone.now() - timedelta(hours=4)}
    ]


def get_mini_admin_tasks():
    """Mini admin vazifalari"""
    return [
        {'task': 'Bloklangan foydalanuvchilarni ko\'rib chiqish', 'priority': 'high',
         'count': User.objects.filter(is_blocked=True).count()},
        {'task': 'Yangi arizalarni tasdiqlash', 'priority': 'medium', 'count': 0},
        {'task': 'Haftalik hisobot tayyorlash', 'priority': 'low', 'count': 1}
    ]