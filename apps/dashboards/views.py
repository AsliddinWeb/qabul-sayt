# apps/dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from functools import wraps

from apps.users.models import User, AbituriyentProfile, PhoneVerification
from apps.regions.models import Region, District


# ======================== DECORATORS ========================
def role_required(allowed_roles):
    """Role-based access decorator"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role not in allowed_roles:
                messages.error(request, "Bu sahifaga kirish huquqingiz yo'q")
                return redirect('dashboard:main')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# ======================== MAIN DASHBOARD ROUTING ========================
@login_required
def main_dashboard(request):
    """Asosiy dashboard - role bo'yicha yo'naltirish"""
    user = request.user

    # Role-based routing
    role_urls = {
        'abituriyent': 'dashboard:abituriyent',
        'operator': 'dashboard:operator',
        'marketing': 'dashboard:marketing',
        'mini_admin': 'dashboard:mini_admin',
        'admin': 'dashboard:admin'
    }

    target_url = role_urls.get(user.role, 'dashboard:abituriyent')
    return redirect(target_url)


# ======================== ABITURIYENT DASHBOARD ========================
@login_required
@role_required(['abituriyent'])
def abituriyent_dashboard(request):
    """Abituriyent dashboard"""
    user = request.user

    # Profile olish yoki yaratish
    try:
        profile = user.abituriyent_profile
    except AbituriyentProfile.DoesNotExist:
        profile = None

    context = {
        'user': user,
        'profile': profile,
        'profile_completion': profile.check_profile_completion() if profile else False,
        'applications': get_user_applications(user),
        'recent_notifications': get_notifications(user),
        'next_steps': get_next_steps(profile) if profile else ['Profilingizni yarating'],
        'quick_stats': get_abituriyent_stats(user)
    }

    return render(request, 'dashboard/abituriyent.html', context)


def get_user_applications(user):
    """Foydalanuvchi arizalari (placeholder)"""
    # Bu yerda Application model bo'lsa, shundan foydalaning
    return []


def get_notifications(user):
    """Bildirishnomalar (placeholder)"""
    notifications = [
        {'message': 'Profilingizni to\'ldiring', 'type': 'warning', 'date': timezone.now()},
        {'message': 'Yangi imkoniyatlar mavjud', 'type': 'info', 'date': timezone.now() - timedelta(days=1)}
    ]
    return notifications[:5]  # Faqat 5 tasi


def get_next_steps(profile):
    """Keyingi qadamlar"""
    if not profile:
        return ["Profilingizni yarating"]

    steps = []
    if not profile.check_profile_completion():
        if not profile.last_name or not profile.first_name:
            steps.append("Shaxsiy ma'lumotlaringizni to'ldiring")
        if not profile.image:
            steps.append("3x4 rasmingizni yuklang")
        if not profile.passport_file:
            steps.append("Pasport nusxasini yuklang")
        if not profile.region or not profile.district:
            steps.append("Manzil ma'lumotlarini to'ldiring")
    else:
        steps.append("Arizangizni topshiring")

    return steps


def get_abituriyent_stats(user):
    """Abituriyent statistikalari"""
    try:
        profile = user.abituriyent_profile
        completion_percentage = 0

        if profile:
            required_fields = 10  # Jami majburiy fieldlar soni
            filled_fields = sum([
                bool(profile.last_name),
                bool(profile.first_name),
                bool(profile.other_name),
                bool(profile.birth_date),
                bool(profile.passport_series),
                bool(profile.pinfl),
                bool(profile.gender),
                bool(profile.region),
                bool(profile.district),
                bool(profile.image)
            ])
            completion_percentage = (filled_fields / required_fields) * 100

        return {
            'profile_completion': completion_percentage,
            'applications_count': 0,  # Application model bo'lsa, hisoblang
            'notifications_count': len(get_notifications(user))
        }
    except:
        return {
            'profile_completion': 0,
            'applications_count': 0,
            'notifications_count': 0
        }


# ======================== OPERATOR DASHBOARD ========================
@login_required
@role_required(['operator'])
def operator_dashboard(request):
    """Operator dashboard"""
    user = request.user

    context = {
        'user': user,
        'stats': get_operator_stats(user),
        'pending_applications': get_pending_applications(),
        'today_processed': get_today_processed(user),
        'quick_actions': get_operator_quick_actions(),
        'recent_activities': get_operator_activities(user)
    }

    return render(request, 'dashboard/operator.html', context)


def get_operator_stats(user):
    """Operator statistikalari"""
    try:
        profile = user.operator_profile
        today = timezone.now().date()

        return {
            'total_processed': profile.handled_applications,
            'today_processed': 0,  # Bugungi ko'rib chiqilganlar (Application modeldan)
            'pending_count': get_pending_applications_count(),
            'avg_processing_time': '15 min',
            'performance_rating': getattr(profile, 'performance_rating', 0)
        }
    except:
        return {
            'total_processed': 0,
            'today_processed': 0,
            'pending_count': 0,
            'avg_processing_time': 'N/A',
            'performance_rating': 0
        }


def get_pending_applications():
    """Ko'rib chiqilishi kerak bo'lgan arizalar"""
    # Application model bo'lsa, pending statusdagilarni qaytaring
    return []


def get_pending_applications_count():
    """Kutilayotgan arizalar soni"""
    return 0  # Application.objects.filter(status='pending').count()


def get_today_processed(user):
    """Bugun ko'rib chiqilganlar"""
    today = timezone.now().date()
    # Application model bo'lsa, bugun processed bo'lganlarni qaytaring
    return []


def get_operator_quick_actions():
    """Operator tezkor amallar"""
    return [
        {'title': 'Yangi arizalarni ko\'rish', 'url': '#', 'icon': 'file-text', 'count': 5},
        {'title': 'Statistikani ko\'rish', 'url': '#', 'icon': 'bar-chart', 'count': None},
        {'title': 'Hisobotni yuklash', 'url': '#', 'icon': 'download', 'count': None},
        {'title': 'Foydalanuvchilar', 'url': '#', 'icon': 'users',
         'count': User.objects.filter(role='abituriyent').count()}
    ]


def get_operator_activities(user):
    """Operator faoliyatlari"""
    return [
        {'action': 'Ariza ko\'rib chiqildi', 'time': timezone.now() - timedelta(minutes=15)},
        {'action': 'Yangi foydalanuvchi ro\'yxatdan o\'tdi', 'time': timezone.now() - timedelta(minutes=30)},
        {'action': 'Profil tasdiqlandi', 'time': timezone.now() - timedelta(hours=1)}
    ]


# ======================== MARKETING DASHBOARD ========================
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


# ======================== MINI ADMIN DASHBOARD ========================
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


# ======================== ADMIN DASHBOARD ========================
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


# ======================== ADDITIONAL UTILITY FUNCTIONS ========================
@login_required
def get_user_stats_ajax(request):
    """AJAX orqali foydalanuvchi statistikalarini olish"""
    user = request.user

    stats = {
        'profile_completion': 0,
        'applications_count': 0,
        'notifications_count': 0
    }

    if user.role == 'abituriyent':
        stats = get_abituriyent_stats(user)
    elif user.role == 'operator':
        stats = get_operator_stats(user)
    elif user.role == 'marketing':
        stats = get_conversion_stats()

    return JsonResponse(stats)


@login_required
def update_profile_completion(request):
    """Profile completion holatini yangilash"""
    if request.user.role == 'abituriyent':
        try:
            profile = request.user.abituriyent_profile
            completion = profile.check_profile_completion()
            return JsonResponse({
                'success': True,
                'completion': completion,
                'percentage': get_abituriyent_stats(request.user)['profile_completion']
            })
        except:
            return JsonResponse({'success': False, 'error': 'Profil topilmadi'})

    return JsonResponse({'success': False, 'error': 'Noto\'g\'ri rol'})