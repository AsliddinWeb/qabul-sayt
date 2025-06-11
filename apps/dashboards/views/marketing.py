# apps/dashboard/views/marketing.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, AbituriyentProfile
from .decorators import role_required


@login_required
@role_required(['marketing'])
def marketing_dashboard(request):
    """Marketing dashboard"""
    user = request.user

    context = {
        'user': user,
        'campaigns': get_active_campaigns(),
        'conversion_stats': get_conversion_stats(),
        'top_regions': get_top_regions(),
        'monthly_targets': get_monthly_targets(),
        'user_analytics': get_marketing_analytics()
    }

    return render(request, 'dashboard/marketing.html', context)


def get_active_campaigns():
    """Faol kampaniyalar"""
    return [
        {'name': 'Yoz qabuli 2024', 'status': 'active', 'leads': 150, 'conversion': 12.5},
        {'name': 'Telegram reklama', 'status': 'active', 'leads': 89, 'conversion': 8.3},
        {'name': 'Instagram kampaniya', 'status': 'paused', 'leads': 67, 'conversion': 15.2}
    ]


def get_conversion_stats():
    """Konversiya statistikalari"""
    total_users = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()
    completed_profiles = AbituriyentProfile.objects.filter(
        last_name__isnull=False,
        first_name__isnull=False,
        passport_series__isnull=False
    ).count()

    return {
        'total_visitors': total_users * 3,  # Approximation
        'registrations': total_users,
        'verified_users': verified_users,
        'completed_applications': completed_profiles,
        'conversion_rate': (completed_profiles / total_users * 100) if total_users > 0 else 0
    }


def get_top_regions():
    """Top viloyatlar"""
    top_regions = AbituriyentProfile.objects.values(
        'region__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    return [
        {'name': region['region__name'] or 'Noma\'lum', 'count': region['count']}
        for region in top_regions
    ]


def get_monthly_targets():
    """Oylik maqsadlar"""
    current_month_users = User.objects.filter(
        date_joined__month=timezone.now().month,
        date_joined__year=timezone.now().year
    ).count()

    target = 500
    completion = (current_month_users / target * 100) if target > 0 else 0

    return {
        'target_applications': target,
        'current_applications': current_month_users,
        'completion_percentage': completion,
        'days_remaining': 30 - timezone.now().day
    }


def get_marketing_analytics():
    """Marketing analitikasi"""
    # Oxirgi 7 kunlik registratsiya statistikasi
    daily_registrations = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=6 - i)
        count = User.objects.filter(date_joined__date=date).count()
        daily_registrations.append({
            'date': date.strftime('%m-%d'),
            'count': count
        })

    return {
        'daily_registrations': daily_registrations,
        'total_users': User.objects.count(),
        'verified_percentage': (User.objects.filter(
            is_verified=True).count() / User.objects.count() * 100) if User.objects.count() > 0 else 0
    }