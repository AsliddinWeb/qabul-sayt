# apps/dashboard/views/abituriyent.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.users.models import AbituriyentProfile
from .decorators import role_required

# GovData service orqali ma'lumot olish
from apps.users.govdata import PassportDataService


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

    return render(request, 'dashboard/abituriyent/home.html', context)


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


@login_required
@role_required(['abituriyent'])
def passport_view(request):
    """Passport ma'lumotlarini qidirish va tahrirlash"""
    user = request.user

    # Profile olish
    try:
        profile = user.abituriyent_profile
    except AbituriyentProfile.DoesNotExist:
        # Profile yo'q bo'lsa, None qaytarish
        profile = None

    context = {
        'user': user,
        'profile': profile,
    }

    return render(request, 'dashboard/abituriyent/passport.html', context)


@login_required
@role_required(['abituriyent'])
@require_http_methods(["POST"])
def search_passport_data(request):
    """Passport ma'lumotlarini API dan qidirish"""
    passport_series = request.POST.get('passport_series', '').upper()
    birth_date = request.POST.get('birth_date', '')

    if not passport_series or not birth_date:
        return JsonResponse({
            'success': False,
            'error': 'Passport seriya va tug\'ilgan sanani kiriting'
        })

    result = PassportDataService.get_passport_info(passport_series, birth_date)

    if result['success']:
        return JsonResponse({
            'success': True,
            'data': result['data']
        })
    else:
        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Ma\'lumot topilmadi')
        })


@login_required
@role_required(['abituriyent'])
@require_http_methods(["POST"])
def save_passport_data(request):
    """Passport ma'lumotlarini saqlash"""
    user = request.user

    # Majburiy maydonlarni tekshirish
    required_fields = ['last_name', 'first_name', 'other_name', 'birth_date',
                       'passport_series', 'pinfl', 'gender']

    for field in required_fields:
        if not request.POST.get(field):
            return JsonResponse({
                'success': False,
                'error': f'{field} maydoni to\'ldirilishi shart!'
            })

    try:
        profile = user.abituriyent_profile
    except AbituriyentProfile.DoesNotExist:
        # Yangi profil yaratish - barcha majburiy maydonlar bilan
        try:
            from datetime import datetime

            profile = AbituriyentProfile.objects.create(
                user=user,
                last_name=request.POST.get('last_name', '').upper(),
                first_name=request.POST.get('first_name', '').upper(),
                other_name=request.POST.get('other_name', '').upper(),
                birth_date=request.POST.get('birth_date'),
                passport_series=request.POST.get('passport_series', '').upper(),
                pinfl=request.POST.get('pinfl', ''),
                gender=request.POST.get('gender', ''),
                nationality=request.POST.get('nationality', "O'zbek")
            )
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Profil yaratishda xatolik: {str(e)}'
            })

    # Mavjud profilni yangilash
    profile.last_name = request.POST.get('last_name', '').upper()
    profile.first_name = request.POST.get('first_name', '').upper()
    profile.other_name = request.POST.get('other_name', '').upper()
    profile.birth_date = request.POST.get('birth_date', '')
    profile.passport_series = request.POST.get('passport_series', '').upper()
    profile.pinfl = request.POST.get('pinfl', '')
    profile.gender = request.POST.get('gender', '')

    # Qo'shimcha ma'lumotlar
    if hasattr(profile, 'nationality'):
        profile.nationality = request.POST.get('nationality', "O'zbek")

    try:
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Ma\'lumotlar muvaffaqiyatli saqlandi'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Saqlashda xatolik: {str(e)}'
        })