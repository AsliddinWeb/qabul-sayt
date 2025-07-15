# apps/dashboard/views/abituriyent.py - Simplified version

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils import timezone

from apps.users.models import AbituriyentProfile
from apps.users.forms import AbituriyentProfileForm
from apps.regions.models import Region, District
from apps.applications.models import Application
from apps.diploms.models import Diplom, TransferDiplom
from .decorators import role_required

from apps.diploms.forms import DiplomForm, TransferDiplomForm
from apps.applications.models import ApplicationStatus
from apps.applications.forms import ApplicationForm, QuickApplicationForm
from apps.programs.models import Program


@login_required
@role_required(['abituriyent'])
def abituriyent_dashboard(request):
    """Abituriyent dashboard"""
    user = request.user
    profile = get_user_profile(user)
    dashboard_data = get_dashboard_data(user, profile)

    context = {
        'user': user,
        'profile': profile,
        'today': timezone.now().date(),
        'profile_completion_percentage': dashboard_data['profile_completion_percentage'],
        'can_apply': dashboard_data['can_apply'],
        'diplom_exists': dashboard_data['diplom_exists'],
        'applications_count': dashboard_data['applications_count'],
        'applications': dashboard_data['applications'][:3],
        'current_step': dashboard_data['current_step'],
        'next_action': dashboard_data['next_action'],
        'quick_stats': dashboard_data['quick_stats'],
        'active_class': 'abituriyent_home',
    }

    return render(request, 'dashboard/abituriyent/home.html', context)


@login_required
@role_required(['abituriyent'])
def passport_view(request):
    """Passport view - qo'lda to'ldirish uchun soddalashtirilgan"""
    user = request.user
    profile = get_user_profile(user)

    # Get regions for select options
    regions = Region.objects.prefetch_related('districts').order_by('name')

    # Initialize form variable
    form = None

    if request.method == 'POST':
        # Handle form submission
        try:
            if profile:
                form = AbituriyentProfileForm(request.POST, request.FILES, instance=profile)
            else:
                form = AbituriyentProfileForm(request.POST, request.FILES)
                form.instance.user = user

            if form.is_valid():
                # Save profile
                profile = form.save(commit=False)
                profile.user = user
                profile.save()

                # Update user full name
                user.full_name = profile.get_full_name()
                user.save(update_fields=['full_name'])

                # Clear cache
                clear_user_cache(user)

                if hasattr(form.instance, 'pk') and form.instance.pk:
                    messages.success(request, 'Ma\'lumotlar muvaffaqiyatli yangilandi!')
                else:
                    messages.success(request, 'Ma\'lumotlar muvaffaqiyatli saqlandi!')

                return redirect('dashboard:abituriyent_diplom')
            else:
                # Show form errors - form ma'lumotlarini saqlash uchun redirect qilmaymiz
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field, {}).label or field
                    for error in errors:
                        messages.error(request, f'{field_label}: {error}')

        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
            # Exception holatida ham form ma'lumotlarini saqlash uchun
            if not form:
                if profile:
                    form = AbituriyentProfileForm(request.POST, request.FILES, instance=profile)
                else:
                    form = AbituriyentProfileForm(request.POST, request.FILES)

    else:
        # GET request - show form
        form = AbituriyentProfileForm(instance=profile) if profile else AbituriyentProfileForm()

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'regions': regions,
        'completion_percentage': calculate_profile_completion(profile) if profile else 0,
        'active_class': 'abituriyent_passport',
    }

    return render(request, 'dashboard/abituriyent/passport.html', context)


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


# Utility functions
def get_user_profile(user):
    """Get user profile with caching"""
    cache_key = f'user_profile_{user.id}'
    profile = cache.get(cache_key)

    if profile is None:
        try:
            profile = user.abituriyent_profile
        except AbituriyentProfile.DoesNotExist:
            profile = None

        cache.set(cache_key, profile, 300)

    return profile


def get_dashboard_data(user, profile):
    """Get dashboard data"""
    cache_key = f'dashboard_data_{user.id}'
    dashboard_data = cache.get(cache_key)

    if dashboard_data is None:
        # Check diplom existence
        diplom_exists = (
            Diplom.objects.filter(user=user).exists() or
            TransferDiplom.objects.filter(user=user).exists()
        )

        # Get applications
        applications = Application.objects.select_related(
            'program', 'branch', 'education_form', 'education_level'
        ).filter(user=user).order_by('-created_at')

        applications_count = applications.count()
        profile_completion = calculate_profile_completion(profile)
        current_step, next_action = get_current_step_and_action(
            profile, diplom_exists, applications_count
        )
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

        cache.set(cache_key, dashboard_data, 120)

    return dashboard_data


def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    if not profile:
        return 0

    required_fields = [
        profile.last_name, profile.first_name, profile.other_name,
        profile.birth_date, profile.passport_series, profile.pinfl,
        profile.gender, profile.region_id, profile.district_id,
        profile.address, profile.image
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
            'url': 'dashboard:abituriyent_passport',
            'button_text': 'Boshlash',
            'button_class': 'btn-primary'
        }

    if not diplom_exists:
        return 'diplom', {
            'title': 'Ta\'lim hujjati',
            'description': 'Diplom yoki transfer hujjatini yuklang',
            'url': 'dashboard:abituriyent_diplom',
            'button_text': 'Yuklash',
            'button_class': 'btn-warning'
        }

    if applications_count == 0:
        return 'application', {
            'title': 'Ariza topshirish',
            'description': 'Yo\'nalishlarga ariza topshiring',
            'url': 'dashboard:abituriyent_apply',
            'button_text': 'Topshirish',
            'button_class': 'btn-success'
        }

    return 'completed', {
        'title': 'Jarayon yakunlandi',
        'description': 'Barcha bosqichlar bajarildi',
        'url': 'dashboard:abituriyent_apply',
        'button_text': 'Arizalarni ko\'rish',
        'button_class': 'btn-info'
    }


def clear_user_cache(user):
    """Clear user-related cache"""
    cache_keys = [
        f'user_profile_{user.id}',
        f'dashboard_data_{user.id}',
    ]

    for key in cache_keys:
        cache.delete(key)


# Existing views (keep as they are)
@login_required
@role_required(['abituriyent'])
def diplom_page(request):
    """Diplom page"""
    user = request.user
    profile = get_user_profile(user)

    if hasattr(user, 'transfer_diplom') and user.transfer_diplom:
        return redirect('dashboard:abituriyent_transfer_diplom')

    try:
        diplom = Diplom.objects.get(user=user)
        is_edit = True
    except Diplom.DoesNotExist:
        diplom = None
        is_edit = False

    if request.method == 'POST':
        if is_edit:
            form = DiplomForm(request.POST, request.FILES, instance=diplom)
            success_message = "Diplom ma'lumotlari muvaffaqiyatli yangilandi!"
        else:
            form = DiplomForm(request.POST, request.FILES)
            success_message = "Diplom ma'lumotlari muvaffaqiyatli saqlandi!"

        if form.is_valid():
            diplom_obj = form.save(commit=False)
            diplom_obj.user = user
            diplom_obj.save()

            messages.success(request, success_message)
            return redirect('dashboard:abituriyent_apply')
        else:
            messages.error(request, "Ma'lumotlarni to'ldirishda xatolik yuz berdi.")
    else:
        if is_edit:
            form = DiplomForm(instance=diplom)
        else:
            form = DiplomForm()

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'diplom': diplom,
        'is_edit': is_edit,
        'active_class': 'abituriyent_diplom',
    }

    return render(request, 'dashboard/abituriyent/diplom.html', context)


@login_required
@role_required(['abituriyent'])
def transfer_diplom_page(request):
    """Transfer diplom page"""
    user = request.user
    profile = get_user_profile(user)

    if hasattr(user, 'diplom') and user.diplom:
        return redirect('dashboard:abituriyent_diplom')

    try:
        transfer_diplom = TransferDiplom.objects.get(user=user)
        is_edit = True
    except TransferDiplom.DoesNotExist:
        transfer_diplom = None
        is_edit = False

    if request.method == 'POST':
        if is_edit:
            form = TransferDiplomForm(request.POST, request.FILES, instance=transfer_diplom)
            success_message = "Perevod diplomi ma'lumotlari muvaffaqiyatli yangilandi!"
        else:
            form = TransferDiplomForm(request.POST, request.FILES)
            success_message = "Perevod diplomi ma'lumotlari muvaffaqiyatli saqlandi!"

        if form.is_valid():
            transfer_diplom_obj = form.save(commit=False)
            transfer_diplom_obj.user = user
            transfer_diplom_obj.save()

            messages.success(request, success_message)
            return redirect('dashboard:abituriyent_apply')
        else:
            messages.error(request, "Ma'lumotlarni to'ldirishda xatolik yuz berdi.")
    else:
        if is_edit:
            form = TransferDiplomForm(instance=transfer_diplom)
        else:
            form = TransferDiplomForm()

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'transfer_diplom': transfer_diplom,
        'is_edit': is_edit,
        'active_class': 'abituriyent_transfer_diplom',
    }

    return render(request, 'dashboard/abituriyent/transfer_diplom.html', context)


@login_required
@role_required(['abituriyent'])
def apply_page(request):
    """Ariza sahifasi"""
    user = request.user
    profile = get_user_profile(user)

    try:
        application = Application.objects.get(user=user)
        is_edit = True

        if application.status == ApplicationStatus.ACCEPTED:
            messages.info(request, "Sizning arizangiz allaqachon qabul qilingan.")

    except Application.DoesNotExist:
        application = None
        is_edit = False

    # Check user has diplomas
    user_diplomas = Diplom.objects.filter(user=user)
    user_transfer_diplomas = TransferDiplom.objects.filter(user=user)

    if not user_diplomas.exists() and not user_transfer_diplomas.exists():
        messages.warning(request, "Ariza topshirishdan oldin avval diplom ma'lumotlarini kiriting.")
        return redirect('dashboard:abituriyent_diplom')

    if request.method == 'POST':
        if is_edit:
            form = ApplicationForm(request.POST, request.FILES, instance=application, user=user)
            success_message = "Ariza ma'lumotlari muvaffaqiyatli yangilandi!"
        else:
            form = ApplicationForm(request.POST, request.FILES, user=user)
            success_message = "Arizangiz muvaffaqiyatli topshirildi!"

        if form.is_valid():
            application_obj = form.save(commit=False)
            application_obj.user = user

            if not is_edit:
                application_obj.status = ApplicationStatus.PENDING

            application_obj.save()
            messages.success(request, success_message)
            return redirect('dashboard:abituriyent_apply')
        else:
            messages.error(request, "Ma'lumotlarni to'ldirishda xatolik yuz berdi.")
    else:
        if is_edit:
            form = ApplicationForm(instance=application, user=user)
        else:
            form = ApplicationForm(user=user)

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'application': application,
        'is_edit': is_edit,
        'active_class': 'abituriyent_apply',
        'user_diplomas': user_diplomas,
        'user_transfer_diplomas': user_transfer_diplomas,
    }

    return render(request, 'dashboard/abituriyent/apply.html', context)


@login_required
def load_programs(request):
    """AJAX - Yo'nalishlarni yuklash"""
    branch_id = request.GET.get('branch_id')
    education_level_id = request.GET.get('education_level_id')
    education_form_id = request.GET.get('education_form_id')

    programs = []

    if branch_id and education_level_id and education_form_id:
        programs_queryset = Program.objects.filter(
            branch_id=branch_id,
            education_level_id=education_level_id,
            education_form_id=education_form_id,
        ).order_by('name')

        programs = [
            {'id': program.id, 'name': program.name}
            for program in programs_queryset
        ]

    return JsonResponse({'programs': programs})


@login_required
@role_required(['abituriyent'])
def application_status(request):
    """Ariza holatini ko'rish sahifasi"""
    user = request.user
    profile = get_user_profile(user)

    try:
        application = Application.get_user_application(user)
        if not application:
            messages.info(request, "Sizda hali ariza mavjud emas.")
            return redirect('dashboard:abituriyent_apply')
    except Application.DoesNotExist:
        messages.info(request, "Sizda hali ariza mavjud emas.")
        return redirect('dashboard:abituriyent_apply')

    context = {
        'user': user,
        'profile': profile,
        'application': application,
        'active_class': 'abituriyent_status',
    }

    return render(request, 'dashboard/abituriyent/application_status.html', context)


@login_required
@role_required(['abituriyent'])
def withdraw_application(request):
    """Arizani bekor qilish"""
    if request.method == 'POST':
        user = request.user

        try:
            application = Application.objects.get(user=user)

            if application.can_be_reviewed:
                application.delete()
                messages.success(request, "Arizangiz muvaffaqiyatli bekor qilindi.")
            else:
                messages.error(request, "Bu arizani bekor qilib bo'lmaydi.")

        except Application.DoesNotExist:
            messages.error(request, "Ariza topilmadi.")

    return redirect('dashboard:abituriyent')


@login_required
@role_required(['abituriyent'])
def application_history(request):
    """Ariza tarixi"""
    user = request.user
    profile = get_user_profile(user)

    applications = Application.objects.filter(user=user).order_by('-created_at')

    context = {
        'user': user,
        'profile': profile,
        'applications': applications,
        'active_class': 'abituriyent_history',
    }

    return render(request, 'dashboard/abituriyent/application_history.html', context)


@login_required
@role_required(['abituriyent'])
def quick_apply(request):
    """Tezkor ariza topshirish"""
    user = request.user
    profile = get_user_profile(user)

    if hasattr(user, 'application'):
        messages.info(request, "Sizda allaqachon ariza mavjud.")
        return redirect('dashboard:abituriyent_apply')

    if not Diplom.objects.filter(user=user).exists():
        messages.warning(request, "Tezkor ariza uchun avval diplom ma'lumotlarini kiriting.")
        return redirect('dashboard:abituriyent_diplom')

    if request.method == 'POST':
        form = QuickApplicationForm(request.POST, user=user)

        if form.is_valid():
            application = form.save()
            messages.success(request, "Tezkor arizangiz topshirildi!")
            return redirect('dashboard:abituriyent_apply')
    else:
        form = QuickApplicationForm(user=user)

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'active_class': 'abituriyent_quick_apply',
    }

    return render(request, 'dashboard/abituriyent/quick_apply.html', context)