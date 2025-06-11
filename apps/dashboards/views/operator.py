# apps/dashboard/views/operator.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User
from .decorators import role_required


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