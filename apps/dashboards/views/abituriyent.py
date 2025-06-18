# apps/dashboard/views/abituriyent.py - Optimized version
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.contrib import messages
from django.template.loader import render_to_string
import json

from apps.users.models import AbituriyentProfile
from apps.users.forms import AbituriyentProfileForm, PassportSearchForm
from apps.regions.models import Region, District
from apps.applications.models import Application
from apps.diploms.models import Diplom, TransferDiplom
from .decorators import role_required


@login_required
@role_required(['abituriyent'])
def abituriyent_dashboard(request):
    """Optimized Abituriyent dashboard with better performance and UX"""
    user = request.user

    # Get or create profile with caching
    profile = get_user_profile(user)

    # Get all necessary data in optimized queries
    dashboard_data = get_dashboard_data(user, profile)

    context = {
        'user': user,
        'profile': profile,
        'today': timezone.now().date(),

        # Progress data
        'profile_completion_percentage': dashboard_data['profile_completion_percentage'],
        'can_apply': dashboard_data['can_apply'],

        # Status data
        'diplom_exists': dashboard_data['diplom_exists'],
        'applications_count': dashboard_data['applications_count'],
        'applications': dashboard_data['applications'][:3],  # Only first 3 for preview

        # Steps and navigation
        'current_step': dashboard_data['current_step'],
        'next_action': dashboard_data['next_action'],

        # Quick stats
        'quick_stats': dashboard_data['quick_stats'],

        'active_class': 'abituriyent_home',
    }

    return render(request, 'dashboard/abituriyent/home.html', context)


def get_user_profile(user):
    """Get user profile with caching"""
    cache_key = f'user_profile_{user.id}'
    profile = cache.get(cache_key)

    if profile is None:
        try:
            profile = user.abituriyent_profile
        except AbituriyentProfile.DoesNotExist:
            profile = None

        # Cache for 5 minutes
        cache.set(cache_key, profile, 300)

    return profile


def get_dashboard_data(user, profile):
    """Get all dashboard data in optimized way"""
    cache_key = f'dashboard_data_{user.id}'
    dashboard_data = cache.get(cache_key)

    if dashboard_data is None:
        # Check diplom existence
        diplom_exists = (
                Diplom.objects.filter(user=user).exists() or
                TransferDiplom.objects.filter(user=user).exists()
        )

        # Get applications with related data
        applications = Application.objects.select_related(
            'program', 'branch', 'education_form', 'education_level'
        ).filter(user=user).order_by('-created_at')

        applications_count = applications.count()

        # Calculate profile completion
        profile_completion = calculate_profile_completion(profile)

        # Determine current step and next action
        current_step, next_action = get_current_step_and_action(
            profile, diplom_exists, applications_count
        )

        # Check if user can apply
        can_apply = profile is not None and diplom_exists

        dashboard_data = {
            'profile_completion_percentage': profile_completion,
            'diplom_exists': diplom_exists,
            'applications_count': applications_count,
            'applications': list(applications),
            'can_apply': can_apply,
            'current_step': current_step,
            'next_action': next_action,
            'quick_stats': {
                'profile_completion': profile_completion,
                'documents_uploaded': int(bool(profile)) + int(diplom_exists),
                'applications_submitted': applications_count,
            }
        }

        # Cache for 2 minutes (shorter cache for dynamic data)
        cache.set(cache_key, dashboard_data, 120)

    return dashboard_data


def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    if not profile:
        return 0

    # Required fields for profile completion
    required_fields = [
        profile.last_name,
        profile.first_name,
        profile.other_name,
        profile.birth_date,
        profile.passport_series,
        profile.pinfl,
        profile.gender,
        profile.region_id,
        profile.district_id,
        profile.address,
        profile.image,
        profile.passport_file,
    ]

    filled_fields = sum(1 for field in required_fields if field)
    total_fields = len(required_fields)

    return int((filled_fields / total_fields) * 100)


def get_current_step_and_action(profile, diplom_exists, applications_count):
    """Determine current step and next action"""
    if not profile:
        return 'passport', {
            'title': 'Passport ma\'lumotlari',
            'description': 'Shaxsiy ma\'lumotlaringizni kiriting',
            'url': 'dashboard:abituriyent:passport',
            'button_text': 'Boshlash',
            'button_class': 'btn-primary'
        }

    if not diplom_exists:
        return 'diplom', {
            'title': 'Ta\'lim hujjati',
            'description': 'Diplom yoki transfer hujjatini yuklang',
            'url': 'dashboard:abituriyent:diplom',
            'button_text': 'Yuklash',
            'button_class': 'btn-warning'
        }

    if applications_count == 0:
        return 'application', {
            'title': 'Ariza topshirish',
            'description': 'Yo\'nalishlarga ariza topshiring',
            'url': 'dashboard:abituriyent:application',
            'button_text': 'Topshirish',
            'button_class': 'btn-success'
        }

    return 'completed', {
        'title': 'Jarayon yakunlandi',
        'description': 'Barcha bosqichlar bajarildi',
        'url': 'dashboard:abituriyent:applications',
        'button_text': 'Arizalarni ko\'rish',
        'button_class': 'btn-info'
    }


@login_required
@role_required(['abituriyent'])
def applications_ajax(request):
    """AJAX endpoint for loading applications"""
    try:
        applications = Application.objects.select_related(
            'program', 'branch', 'education_form'
        ).filter(user=request.user).order_by('-created_at')[:5]

        html = render_to_string(
            'dashboard/abituriyent/partials/applications_list.html',
            {'applications': applications},
            request=request
        )

        return JsonResponse({
            'success': True,
            'html': html,
            'count': applications.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@role_required(['abituriyent'])
def passport_view(request):
    """Optimized passport view with better error handling"""
    user = request.user
    profile = get_user_profile(user)

    # Get regions with districts (optimized)
    regions = Region.objects.prefetch_related(
        Prefetch('districts', queryset=District.objects.order_by('name'))
    ).order_by('name')

    if request.method == 'POST':
        return handle_passport_form(request, user, profile)

    # GET request
    form = AbituriyentProfileForm(instance=profile) if profile else AbituriyentProfileForm()
    search_form = PassportSearchForm()

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'search_form': search_form,
        'regions': regions,
        'completion_percentage': calculate_profile_completion(profile) if profile else 0,

        'active_class': 'abituriyent_passport',
    }

    return render(request, 'dashboard/abituriyent/passport.html', context)


def handle_passport_form(request, user, profile):
    """Handle passport form submission"""
    try:
        if profile:
            form = AbituriyentProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = AbituriyentProfileForm(request.POST, request.FILES)
            form.instance.user = user

        if form.is_valid():
            # Process and save form
            profile = form.save(commit=False)

            # Normalize data
            profile.last_name = profile.last_name.upper().strip()
            profile.first_name = profile.first_name.upper().strip()
            profile.other_name = profile.other_name.upper().strip()
            profile.passport_series = profile.passport_series.upper().strip()

            profile.save()

            # Update user full name
            user.full_name = profile.get_full_name()
            user.save(update_fields=['full_name'])

            # Clear cache
            clear_user_cache(user)

            messages.success(request, 'Ma\'lumotlar muvaffaqiyatli saqlandi!')
            return redirect('dashboard:abituriyent:home')
        else:
            # Form has errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')

    except Exception as e:
        messages.error(request, f'Xatolik yuz berdi: {str(e)}')

    return redirect('dashboard:abituriyent:passport')


@login_required
@role_required(['abituriyent'])
@require_http_methods(["POST"])
def search_passport_data(request):
    """Search passport data from GovData API with better error handling"""
    form = PassportSearchForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'error': 'Form ma\'lumotlari noto\'g\'ri'
        })

    try:
        passport_series = form.cleaned_data['passport_series']
        birth_date = form.cleaned_data['birth_date'].strftime('%Y-%m-%d')

        # Import and use GovData service
        from apps.users.govdata import PassportDataService

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

    except ImportError:
        return JsonResponse({
            'success': False,
            'error': 'GovData xizmati mavjud emas'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Xatolik yuz berdi: {str(e)}'
        })


@login_required
@role_required(['abituriyent'])
@require_http_methods(["POST"])
def save_passport_data(request):
    """Save passport data with comprehensive validation"""
    user = request.user

    # Validate required fields
    validation_result = validate_passport_data(request.POST, request.FILES)
    if not validation_result['valid']:
        return JsonResponse({
            'success': False,
            'error': validation_result['error']
        })

    try:
        profile = get_user_profile(user)

        if profile:
            form = AbituriyentProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = AbituriyentProfileForm(request.POST, request.FILES)
            form.instance.user = user

        if form.is_valid():
            # Process API photo if provided
            api_photo_url = request.POST.get('api_photo_url')
            if api_photo_url and not request.FILES.get('image'):
                process_api_photo(form, api_photo_url, user)

            # Save profile
            profile = form.save(commit=False)

            # Normalize data
            profile.last_name = profile.last_name.upper().strip()
            profile.first_name = profile.first_name.upper().strip()
            profile.other_name = profile.other_name.upper().strip()
            profile.passport_series = profile.passport_series.upper().strip()

            profile.save()

            # Update user
            user.full_name = profile.get_full_name()
            user.save(update_fields=['full_name'])

            # Clear cache
            clear_user_cache(user)

            return JsonResponse({
                'success': True,
                'message': 'Ma\'lumotlar muvaffaqiyatli saqlandi',
                'redirect_url': '/dashboard/abituriyent/'
            })
        else:
            errors = []
            for field, error_list in form.errors.items():
                field_label = form.fields.get(field, {}).label or field
                for error in error_list:
                    errors.append(f'{field_label}: {error}')

            return JsonResponse({
                'success': False,
                'error': '; '.join(errors)
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Saqlashda xatolik: {str(e)}'
        })


def validate_passport_data(post_data, files_data):
    """Validate passport form data"""
    required_fields = {
        'last_name': 'Familiya',
        'first_name': 'Ism',
        'other_name': 'Otasining ismi',
        'birth_date': 'Tug\'ilgan sana',
        'passport_series': 'Passport seriya',
        'pinfl': 'PINFL',
        'gender': 'Jinsi',
        'region': 'Viloyat',
        'district': 'Tuman',
        'address': 'Yashash manzili'
    }

    # Check required fields
    for field, field_name in required_fields.items():
        value = post_data.get(field, '').strip()
        if not value:
            return {
                'valid': False,
                'error': f'{field_name} maydoni to\'ldirilishi shart!'
            }

    # Check image requirement
    uploaded_image = files_data.get('image')
    api_photo_url = post_data.get('api_photo_url', '').strip()

    if not uploaded_image and not api_photo_url:
        return {
            'valid': False,
            'error': '3x4 rasm yuklanishi yoki API dan olinishi shart!'
        }

    return {'valid': True}


def process_api_photo(form, api_photo_url, user):
    """Process photo from API URL"""
    try:
        import requests
        from django.core.files.base import ContentFile
        import uuid
        from django.conf import settings
        import os

        if api_photo_url.startswith('/media/'):
            # Local media file
            file_path = os.path.join(settings.MEDIA_ROOT, api_photo_url.replace('/media/', ''))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_content = ContentFile(f.read())
                    filename = f"passport_photos/{user.id}_{uuid.uuid4().hex[:8]}.jpg"
                    form.instance.image.save(filename, file_content, save=False)

        elif api_photo_url.startswith('http'):
            # Remote URL
            response = requests.get(api_photo_url, timeout=10, stream=True)
            response.raise_for_status()

            file_extension = api_photo_url.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                file_extension = 'jpg'

            filename = f"passport_photos/{user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            file_content = ContentFile(response.content)
            form.instance.image.save(filename, file_content, save=False)

    except Exception as e:
        print(f"Error processing API photo: {e}")


@login_required
@role_required(['abituriyent'])
@require_http_methods(["GET"])
def load_districts(request):
    """Load districts by region via AJAX"""
    region_id = request.GET.get('region_id')

    if not region_id:
        return JsonResponse({
            'success': False,
            'error': 'Region ID kiritilmagan'
        })

    try:
        districts = District.objects.filter(
            region_id=region_id
        ).values('id', 'name').order_by('name')

        return JsonResponse({
            'success': True,
            'districts': list(districts)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def clear_user_cache(user):
    """Clear all user-related cache"""
    cache_keys = [
        f'user_profile_{user.id}',
        f'dashboard_data_{user.id}',
    ]

    for key in cache_keys:
        cache.delete(key)


# Additional utility views
@login_required
@role_required(['abituriyent'])
def profile_completion_ajax(request):
    """Get profile completion status via AJAX"""
    try:
        profile = get_user_profile(request.user)
        completion = calculate_profile_completion(profile)

        return JsonResponse({
            'success': True,
            'completion_percentage': completion,
            'is_complete': completion == 100
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@role_required(['abituriyent'])
def dashboard_stats_ajax(request):
    """Get dashboard statistics via AJAX"""
    try:
        profile = get_user_profile(request.user)
        dashboard_data = get_dashboard_data(request.user, profile)

        return JsonResponse({
            'success': True,
            'stats': dashboard_data['quick_stats'],
            'current_step': dashboard_data['current_step']
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@role_required(['abituriyent'])
def diplom_page(request):
    """Diplom page"""
    user = request.user
    profile = get_user_profile(user)


    if request.method == 'POST':
        pass


    context = {
        'user': user,
        'profile': profile,

        'active_class': 'abituriyent_diplom',
    }

    return render(request, 'dashboard/abituriyent/diplom.html', context)

