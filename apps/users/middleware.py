# apps/users/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings


class PhoneVerificationMiddleware:
    """
    Tasdiqlanmagan foydalanuvchilarni telefon tasdiqlash sahifasiga yo'naltirish
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bu URL'larga kirish uchun tasdiqlash shart emas
        exempt_urls = [
            reverse('users:phone_auth'),
            reverse('users:verify_code'),
            reverse('users:resend_code'),
            reverse('users:logout'),
            reverse('users:home'),  # Home sahifa uchun ham ruxsat
        ]

        # Static va media fayllar
        exempt_prefixes = [
            '/static/',
            '/media/',
            '/admin/',
            '/api/',  # API uchun agar kerak bo'lsa
        ]

        # Foydalanuvchi login qilgan va tasdiqlanmagan bo'lsa
        if request.user.is_authenticated and not request.user.is_verified:

            # Istisno URL'larni tekshirish
            if request.path not in exempt_urls:
                # Prefix'larni tekshirish
                is_exempt = any(request.path.startswith(prefix) for prefix in exempt_prefixes)

                if not is_exempt:
                    # Telefon tasdiqlash sahifasiga yo'naltirish
                    messages.warning(
                        request,
                        "Tizimdan to'liq foydalanish uchun telefon raqamingizni tasdiqlang!"
                    )
                    return redirect('users:phone_auth')

        response = self.get_response(request)
        return response


class RoleBasedAccessMiddleware:
    """
    Rol asosida kirish huquqlarini boshqarish
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Foydalanuvchi login qilgan bo'lsa
        if request.user.is_authenticated:

            # Admin panel uchun faqat admin rollar
            if request.path.startswith('/admin/'):
                if not (request.user.is_admin_role or request.user.is_superuser):
                    messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
                    return redirect('users:home')

            # Dashboard sahifalar uchun rol tekshirish
            elif request.path.startswith('/dashboard/'):
                # Bu yerda har bir dashboard sahifa uchun rol tekshirish
                if request.path.startswith('/dashboard/admin/') and not request.user.is_admin_role:
                    messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
                    return redirect('users:home')

                elif request.path.startswith('/dashboard/mini-admin/') and not request.user.is_mini_admin:
                    messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
                    return redirect('users:home')

                elif request.path.startswith('/dashboard/operator/') and not request.user.is_operator:
                    messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
                    return redirect('users:home')

                elif request.path.startswith('/dashboard/marketing/') and not request.user.is_marketing:
                    messages.error(request, "Bu sahifaga kirish huquqingiz yo'q!")
                    return redirect('users:home')

        response = self.get_response(request)
        return response


class SecurityMiddleware:
    """
    Xavfsizlik uchun qo'shimcha middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Foydalanuvchi faol emasligini tekshirish
        if request.user.is_authenticated and not request.user.is_active:
            messages.error(request, "Hisobingiz faol emas. Administrator bilan bog'laning.")
            return redirect('users:logout')

        response = self.get_response(request)
        return response