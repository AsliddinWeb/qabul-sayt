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
        # Exempt URLs
        exempt_urls = [
            reverse('users:phone_auth'),
            reverse('users:verify_code'),
            reverse('users:resend_code'),
            reverse('users:logout'),
            reverse('home:home_page'),  # Home sahifa ham exempt
            '/admin/',  # Admin panel ham exempt
        ]

        # Prefix'lar
        exempt_prefixes = [
            '/static/',
            '/media/',
            '/admin/',
        ]

        # Agar user authenticated va verified emas
        if (request.user.is_authenticated and
                not request.user.is_verified and
                request.path not in exempt_urls):

            # Prefix tekshirish
            is_exempt = any(request.path.startswith(prefix) for prefix in exempt_prefixes)

            if not is_exempt:
                messages.warning(
                    request,
                    "Tizimdan to'liq foydalanish uchun telefon raqamingizni tasdiqlang!"
                )
                return redirect('users:phone_auth')

        return self.get_response(request)


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