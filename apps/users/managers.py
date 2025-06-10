# apps/users/managers.py

from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import models
import re


class UserQuerySet(models.QuerySet):
    """Custom QuerySet for User model"""

    def active(self):
        """Faol foydalanuvchilar"""
        return self.filter(is_active=True)

    def inactive(self):
        """Nofaol foydalanuvchilar"""
        return self.filter(is_active=False)

    def verified(self):
        """Tasdiqlangan foydalanuvchilar"""
        return self.filter(is_verified=True)

    def unverified(self):
        """Tasdiqlanmagan foydalanuvchilar"""
        return self.filter(is_verified=False)

    def blocked(self):
        """Bloklangan foydalanuvchilar"""
        return self.filter(is_blocked=True)

    def unblocked(self):
        """Bloklanmagan foydalanuvchilar"""
        return self.filter(is_blocked=False)

    def by_role(self, role):
        """Rol bo'yicha filtrlash"""
        return self.filter(role=role)

    def abituriyents(self):
        """Abituriyentlar"""
        return self.filter(role='abituriyent')

    def operators(self):
        """Operatorlar"""
        return self.filter(role='operator')

    def marketing_staff(self):
        """Marketing xodimlari"""
        return self.filter(role='marketing')

    def mini_admins(self):
        """Mini adminlar"""
        return self.filter(role='mini_admin')

    def admins(self):
        """Adminlar"""
        return self.filter(role='admin')

    def staff_members(self):
        """Xodimlar (admin panel kirish huquqi bor)"""
        return self.filter(is_staff=True)

    def management_users(self):
        """Boshqaruv foydalanuvchilari (admin va mini_admin)"""
        return self.filter(role__in=['admin', 'mini_admin'])

    def recently_joined(self, days=7):
        """Yaqinda qo'shilgan foydalanuvchilar"""
        from_date = timezone.now() - timedelta(days=days)
        return self.filter(date_joined__gte=from_date)

    def recently_active(self, days=30):
        """Yaqinda faol bo'lgan foydalanuvchilar"""
        from_date = timezone.now() - timedelta(days=days)
        return self.filter(last_login__gte=from_date)

    def with_failed_attempts(self, min_attempts=1):
        """Muvaffaqiyatsiz kirish urinishlari bo'lgan"""
        return self.filter(failed_login_attempts__gte=min_attempts)

    def search_by_phone(self, phone):
        """Telefon raqami bo'yicha qidirish"""
        return self.filter(phone__icontains=phone)

    def search_by_name(self, name):
        """Ism bo'yicha qidirish"""
        return self.filter(full_name__icontains=name)

    def search(self, query):
        """Umumiy qidiruv (telefon va ism bo'yicha)"""
        return self.filter(
            models.Q(phone__icontains=query) |
            models.Q(full_name__icontains=query)
        )


class UserManager(BaseUserManager):
    """User model uchun asosiy manager"""

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _validate_phone(self, phone):
        """Telefon raqam formatini tekshirish"""
        phone_pattern = r'^\+998\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValidationError("Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak")
        return phone

    def _create_user(self, phone, password=None, **extra_fields):
        """Asosiy user yaratish funksiyasi"""
        if not phone:
            raise ValueError("Telefon raqam kiritilishi shart")

        # Telefon raqamni validatsiya qilish
        phone = self._validate_phone(phone)

        # User yaratish
        user = self.model(phone=phone, **extra_fields)

        # Parol bo'lsa set qilish, bo'lmasa unusable qilish
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish (parolsiz ham ishlaydi)"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'abituriyent')

        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        """Superuser yaratish (parol majburiy)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak.')
        if not password:
            raise ValueError('Superuser uchun parol kiritilishi shart.')

        return self._create_user(phone, password, **extra_fields)

    def create_abituriyent(self, phone, full_name=None, **extra_fields):
        """Abituriyent yaratish (parolsiz)"""
        extra_fields.setdefault('role', 'abituriyent')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if full_name:
            extra_fields['full_name'] = full_name

        return self.create_user(phone, None, **extra_fields)

    def create_operator(self, phone, full_name, password, **extra_fields):
        """Operator yaratish (parol majburiy)"""
        if not full_name:
            raise ValueError("Operator uchun to'liq ism kiritilishi shart")
        if not password:
            raise ValueError("Operator uchun parol kiritilishi shart")

        extra_fields.setdefault('role', 'operator')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_verified', True)
        extra_fields['full_name'] = full_name

        return self._create_user(phone, password, **extra_fields)

    def create_marketing(self, phone, full_name, password, **extra_fields):
        """Marketing xodimi yaratish (parol majburiy)"""
        if not full_name:
            raise ValueError("Marketing xodimi uchun to'liq ism kiritilishi shart")
        if not password:
            raise ValueError("Marketing xodimi uchun parol kiritilishi shart")

        extra_fields.setdefault('role', 'marketing')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_verified', True)
        extra_fields['full_name'] = full_name

        return self._create_user(phone, password, **extra_fields)

    def create_mini_admin(self, phone, full_name, password, **extra_fields):
        """Mini admin yaratish (parol majburiy)"""
        if not full_name:
            raise ValueError("Mini admin uchun to'liq ism kiritilishi shart")
        if not password:
            raise ValueError("Mini admin uchun parol kiritilishi shart")

        extra_fields.setdefault('role', 'mini_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_verified', True)
        extra_fields['full_name'] = full_name

        return self._create_user(phone, password, **extra_fields)

    def create_admin(self, phone, full_name, password, **extra_fields):
        """Admin yaratish (parol majburiy)"""
        if not full_name:
            raise ValueError("Admin uchun to'liq ism kiritilishi shart")
        if not password:
            raise ValueError("Admin uchun parol kiritilishi shart")

        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields['full_name'] = full_name

        return self._create_user(phone, password, **extra_fields)

    # QuerySet metodlarini manager'ga qo'shish (shortcut)
    def active(self):
        return self.get_queryset().active()

    def inactive(self):
        return self.get_queryset().inactive()

    def verified(self):
        return self.get_queryset().verified()

    def unverified(self):
        return self.get_queryset().unverified()

    def blocked(self):
        return self.get_queryset().blocked()

    def unblocked(self):
        return self.get_queryset().unblocked()

    def by_role(self, role):
        return self.get_queryset().by_role(role)

    def abituriyents(self):
        return self.get_queryset().abituriyents()

    def operators(self):
        return self.get_queryset().operators()

    def marketing_staff(self):
        return self.get_queryset().marketing_staff()

    def mini_admins(self):
        return self.get_queryset().mini_admins()

    def admins(self):
        return self.get_queryset().admins()

    def staff_members(self):
        return self.get_queryset().staff_members()

    def management_users(self):
        return self.get_queryset().management_users()

    def recently_joined(self, days=7):
        return self.get_queryset().recently_joined(days)

    def recently_active(self, days=30):
        return self.get_queryset().recently_active(days)

    def with_failed_attempts(self, min_attempts=1):
        return self.get_queryset().with_failed_attempts(min_attempts)

    def search_by_phone(self, phone):
        return self.get_queryset().search_by_phone(phone)

    def search_by_name(self, name):
        return self.get_queryset().search_by_name(name)

    def search(self, query):
        return self.get_queryset().search(query)


class ActiveUserManager(UserManager):
    """Faqat faol foydalanuvchilar uchun manager"""

    def get_queryset(self):
        return super().get_queryset().active()


class VerifiedUserManager(UserManager):
    """Faqat tasdiqlangan foydalanuvchilar uchun manager"""

    def get_queryset(self):
        return super().get_queryset().verified()


class StaffUserManager(UserManager):
    """Faqat xodimlar uchun manager"""

    def get_queryset(self):
        return super().get_queryset().staff_members()