# apps/dashboard/views/api.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .abituriyent import get_abituriyent_stats
from .operator import get_operator_stats
from .marketing import get_conversion_stats


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