# apps/users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.utils import timezone
import random
import logging

from .models import User, PhoneVerification
from .forms import PhoneForm, VerifyCodeForm
from .utils import send_verification_code, send_notification_sms

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Asosiy sahifa"""
    template_name = 'home/home.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:phone_auth')

        user = request.user
        if user.is_admin_role:
            return redirect('admin:index')
        elif user.is_mini_admin:
            return render(request, 'dashboard/mini_admin.html')
        elif user.is_operator:
            return render(request, 'dashboard/operator.html')
        elif user.is_marketing:
            return render(request, 'dashboard/marketing.html')
        elif user.is_abituriyent:
            return render(request, 'dashboard/abituriyent/home.html')

        return super().get(request, *args, **kwargs)


class PhoneAuthView(FormView):
    """Telefon raqam orqali kirish/ro'yxatdan o'tish"""
    template_name = 'auth/phone_auth.html'
    form_class = PhoneForm

    def dispatch(self, request, *args, **kwargs):
        # Agar user allaqachon login qilgan bo'lsa
        if request.user.is_authenticated:
            return redirect('users:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone = form.cleaned_data.get('phone')

        # Foydalanuvchi mavjudmi tekshirish
        user_exists = User.objects.filter(phone=phone).exists()

        # SMS kod yuborish mumkinligini tekshirish
        can_send, message = PhoneVerification.can_send_code(phone)

        if not can_send:
            messages.error(self.request, message)
            return self.form_invalid(form)

        # Eski kodlarni bekor qilish
        PhoneVerification.objects.filter(phone=phone, is_used=False).update(is_used=True)

        # Yangi kod yaratish
        code = str(random.randint(1000, 9999))

        verification = PhoneVerification.objects.create(
            phone=phone,
            code=code
        )

        # SMS yuborish
        sms_sent = send_verification_code(phone, code)

        if sms_sent:
            logger.info(f"Verification code sent to {phone}")
        else:
            logger.error(f"Failed to send verification code to {phone}")
            messages.warning(
                self.request,
                "SMS yuborishda xatolik. Kod konsolda ko'rsatilgan (dev mode)."
            )

        # Session ga telefon raqamni saqlash
        self.request.session['auth_phone'] = phone
        self.request.session['user_exists'] = user_exists

        if user_exists:
            messages.info(self.request, f"{phone} raqamiga SMS kod yuborildi. Kodni kiriting.")
        else:
            messages.success(
                self.request,
                f"Yangi hisob yaratilmoqda! {phone} raqamiga SMS kod yuborildi."
            )

        return redirect('users:verify_code')


class VerifyCodeView(FormView):
    """SMS kodni tasdiqlash"""
    template_name = 'auth/verify_code.html'
    form_class = VerifyCodeForm

    def dispatch(self, request, *args, **kwargs):
        # Session da telefon raqam bormi tekshirish
        if 'auth_phone' not in request.session:
            return redirect('users:phone_auth')
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['phone'] = self.request.session.get('auth_phone')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.request.session.get('auth_phone')
        context['phone'] = phone
        context['masked_phone'] = self._mask_phone(phone)
        context['user_exists'] = self.request.session.get('user_exists', False)
        return context

    def form_valid(self, form):
        phone = form.cleaned_data.get('phone')
        code = form.cleaned_data.get('code')

        # Kodni tekshirish
        is_valid, message = PhoneVerification.verify_code(phone, code)

        if not is_valid:
            messages.error(self.request, message)
            return self.form_invalid(form)

        # Foydalanuvchini olish yoki yaratish
        try:
            user = User.objects.get(phone=phone)
            created = False

            # Agar user mavjud bo'lsa va tasdiqlanmagan bo'lsa
            if not user.is_verified:
                user.is_verified = True
                user.save()
        except User.DoesNotExist:
            # Yangi user yaratish
            user = User.objects.create_user(
                phone=phone,
                is_verified=True,
                role='abituriyent',
                is_active=True
            )
            created = True

        # Agar yangi yaratilgan bo'lmasa, verifikatsiya qilish
        if not created and not user.is_verified:
            user.is_verified = True
            user.save()

        # Login qilish
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, user)

        # Session tozalash
        if 'auth_phone' in self.request.session:
            del self.request.session['auth_phone']
        if 'user_exists' in self.request.session:
            del self.request.session['user_exists']

        if created:
            messages.success(
                self.request,
                "Tabriklaymiz! Ro'yxatdan muvaffaqiyatli o'tdingiz. Profilingizni to'ldiring."
            )
            # Yangi foydalanuvchi - profil to'ldirish sahifasiga
            if user.is_abituriyent:
                return redirect('dashboard:main')
        else:
            # Login haqida bildirishnoma
            send_notification_sms(phone, 'login_alert')

            messages.success(self.request, f"Xush kelibsiz, {user.full_name or user.phone}!")

        return redirect('dashboard:main')

    def _mask_phone(self, phone):
        """Telefon raqamni maskalash: +998901234567 -> +998 90 *** ** 67"""
        if phone and len(phone) >= 13:
            return f"{phone[:7]} *** ** {phone[-2:]}"
        return phone


class ResendCodeView(View):
    """SMS kodni qayta yuborish"""

    def post(self, request):
        phone = request.session.get('auth_phone')

        if not phone:
            return redirect('users:phone_auth')

        # Yangi kod yuborish mumkinligini tekshirish
        can_send, message = PhoneVerification.can_send_code(phone)

        if can_send:
            # Eski kodlarni bekor qilish
            PhoneVerification.objects.filter(phone=phone, is_used=False).update(is_used=True)

            # Yangi kod yaratish
            code = str(random.randint(1000, 9999))

            verification = PhoneVerification.objects.create(
                phone=phone,
                code=code
            )

            # SMS yuborish
            sms_sent = send_verification_code(phone, code)

            if sms_sent:
                messages.success(request, "Yangi kod yuborildi!")
                logger.info(f"Resent verification code to {phone}")
            else:
                messages.warning(
                    request,
                    "SMS yuborishda xatolik. Kod konsolda ko'rsatilgan (dev mode)."
                )
                logger.error(f"Failed to resend verification code to {phone}")
        else:
            messages.error(request, message)

        return redirect('users:verify_code')


class LogoutView(View):
    """Logout view"""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        logout(request)
        messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz!")
        return redirect('users:phone_auth')


class CompleteProfileView(TemplateView):
    """Profil to'ldirish sahifasi"""
    template_name = 'users/complete_profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        # Faqat abituriyentlar uchun
        if not user.is_abituriyent:
            return redirect('users:home')
        # Profil to'liq bo'lsa home ga yo'naltirish
        if hasattr(user, 'abituriyent_profile'):
            profile = user.abituriyent_profile
            if profile.check_profile_completion():
                return redirect('users:home')
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context