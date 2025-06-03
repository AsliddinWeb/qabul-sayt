from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count, Q
from django import forms
import datetime

from .models import (
    User,
    AbituriyentProfile,
    OperatorProfile,
    MarketingProfile,
    MiniAdminProfile,
    AdminProfile,
    PhoneVerification
)


class UserCreationForm(forms.ModelForm):
    """Yangi foydalanuvchi yaratish formasi"""
    password1 = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput,
        help_text="Kamida 8 ta belgi bo'lishi kerak"
    )
    password2 = forms.CharField(
        label='Parolni tasdiqlash',
        widget=forms.PasswordInput,
        help_text="Yuqoridagi parolni takrorlang"
    )

    class Meta:
        model = User
        fields = ('phone', 'full_name', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Parollar mos kelmaydi")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Foydalanuvchi ma'lumotlarini o'zgartirish formasi"""
    password = ReadOnlyPasswordHashField(
        label="Parol",
        help_text='Parolni o\'zgartirish uchun '
                  '<a href="../password/">bu havola</a>ni ishlatng.'
    )

    class Meta:
        model = User
        fields = ('phone', 'full_name', 'role', 'is_active', 'is_staff', 'is_verified', 'password')

    def clean_password(self):
        # Password fieldini initial'dan olish, agar bo'lmasa hozirgi parolni qaytarish
        return self.initial.get("password", self.instance.password)


class AbituriyentProfileInline(admin.StackedInline):
    """Abituriyent profili inline"""
    model = AbituriyentProfile
    can_delete = False
    verbose_name_plural = 'Abituriyent ma\'lumotlari'

    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('last_name', 'first_name', 'other_name', 'birth_date', 'gender', 'nationality')
        }),
        ('Hujjat ma\'lumotlari', {
            'fields': ('passport_series', 'pinfl')
        }),
        ('Manzil ma\'lumotlari', {
            'fields': ('region', 'district', 'address')
        }),
        ('Fayllar', {
            'fields': ('image', 'passport_file'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ['created_at', 'updated_at']


class OperatorProfileInline(admin.StackedInline):
    """Operator profili inline"""
    model = OperatorProfile
    can_delete = False
    verbose_name_plural = 'Operator ma\'lumotlari'

    fields = ('shift', 'handled_applications', 'created_at', 'updated_at')
    readonly_fields = ['created_at', 'updated_at']


class MarketingProfileInline(admin.StackedInline):
    """Marketing profili inline"""
    model = MarketingProfile
    can_delete = False
    verbose_name_plural = 'Marketing ma\'lumotlari'

    fields = ('department', 'created_at', 'updated_at')
    readonly_fields = ['created_at', 'updated_at']


class MiniAdminProfileInline(admin.StackedInline):
    """Mini Admin profili inline"""
    model = MiniAdminProfile
    can_delete = False
    verbose_name_plural = 'Mini Admin ma\'lumotlari'

    fields = ('created_at', 'updated_at')
    readonly_fields = ['created_at', 'updated_at']


class AdminProfileInline(admin.StackedInline):
    """Admin profili inline"""
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin ma\'lumotlari'

    fields = ('access_level', 'can_modify_users', 'can_access_reports', 'created_at', 'updated_at')
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Foydalanuvchi admin konfiguratsiyasi"""

    # Forms
    form = UserChangeForm
    add_form = UserCreationForm

    # List display
    list_display = (
        'phone',
        'full_name',
        'role_badge',
        'verification_status',
        'activity_status',
        'block_status',
        'date_joined_short',
        'last_login_short'
    )

    list_display_links = ('phone', 'full_name')

    # Filters
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_verified',
        'is_blocked',
        'date_joined',
        'last_login'
    )

    # Search
    search_fields = ('phone', 'full_name')
    search_help_text = "Telefon raqami yoki to'liq ism bo'yicha qidiring"

    # Ordering
    ordering = ('-date_joined',)

    # Filter horizontal
    filter_horizontal = ()

    # Fieldsets for change form
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('phone', 'full_name', 'role')
        }),
        ('Ruxsatlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified'),
            'classes': ('collapse',)
        }),
        ('Xavfsizlik', {
            'fields': ('failed_login_attempts', 'is_blocked', 'blocked_until'),
            'classes': ('collapse',)
        }),
        ('Vaqt belgilari', {
            'fields': ('date_joined', 'last_login', 'last_login_attempt'),
            'classes': ('collapse',)
        }),
    )

    # Fieldsets for add form
    add_fieldsets = (
        ('Yangi foydalanuvchi yaratish', {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password1', 'password2'),
        }),
        ('Ruxsatlar', {
            'fields': ('is_staff', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    # Readonly fields
    readonly_fields = ('date_joined', 'last_login', 'last_login_attempt')

    # Actions
    actions = [
        'make_active',
        'make_inactive',
        'verify_users',
        'unblock_users',
        'reset_failed_attempts'
    ]

    def get_inlines(self, request, obj):
        """Rol bo'yicha inline'larni aniqlash"""
        if obj:
            if obj.is_abituriyent:
                return [AbituriyentProfileInline]
            elif obj.is_operator:
                return [OperatorProfileInline]
            elif obj.is_marketing:
                return [MarketingProfileInline]
            elif obj.is_mini_admin:
                return [MiniAdminProfileInline]
            elif obj.is_admin_role:
                return [AdminProfileInline]
        return []

    def get_queryset(self, request):
        """Optimized queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related(
            'abituriyent_profile',
            'operator_profile',
            'marketing_profile',
            'mini_admin_profile',
            'admin_profile'
        )

    # Custom methods for list_display
    def role_badge(self, obj):
        """Rol ko'rsatish uchun badge"""
        colors = {
            'abituriyent': '#007bff',  # blue
            'operator': '#28a745',  # green
            'marketing': '#ffc107',  # yellow
            'mini_admin': '#fd7e14',  # orange
            'admin': '#dc3545'  # red
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_role_display()
        )

    role_badge.short_description = 'Rol'

    def verification_status(self, obj):
        """Tasdiqlash holati"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green;">✓ Tasdiqlangan</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Tasdiqlanmagan</span>'
        )

    verification_status.short_description = 'Tasdiqlash'

    def activity_status(self, obj):
        """Faollik holati"""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">● Faol</span>'
            )
        return format_html(
            '<span style="color: red;">● Nofaol</span>'
        )

    activity_status.short_description = 'Holat'

    def block_status(self, obj):
        """Blok holati"""
        if obj.is_account_blocked():
            return format_html(
                '<span style="color: red;">🔒 Bloklangan</span>'
            )
        elif obj.failed_login_attempts > 0:
            return format_html(
                '<span style="color: orange;">⚠ {} ta urinish</span>',
                obj.failed_login_attempts
            )
        return format_html(
            '<span style="color: green;">🔓 Ochiq</span>'
        )

    block_status.short_description = 'Xavfsizlik'

    def date_joined_short(self, obj):
        """Qisqartirilgan ro'yxatdan o'tish sanasi"""
        if obj.date_joined:
            return obj.date_joined.strftime('%d.%m.%Y')
        return '-'

    date_joined_short.short_description = 'Ro\'yxat sanasi'

    def last_login_short(self, obj):
        """Qisqartirilgan oxirgi kirish"""
        if obj.last_login:
            return obj.last_login.strftime('%d.%m.%Y %H:%M')
        return 'Hech qachon'

    last_login_short.short_description = 'Oxirgi kirish'

    # Actions
    def make_active(self, request, queryset):
        """Foydalanuvchilarni faollashtirish"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} ta foydalanuvchi faollashtirildi.')

    make_active.short_description = "Tanlangan foydalanuvchilarni faollashtirish"

    def make_inactive(self, request, queryset):
        """Foydalanuvchilarni nofaol qilish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} ta foydalanuvchi nofaol qilindi.')

    make_inactive.short_description = "Tanlangan foydalanuvchilarni nofaol qilish"

    def verify_users(self, request, queryset):
        """Foydalanuvchilarni tasdiqlash"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} ta foydalanuvchi tasdiqlandi.')

    verify_users.short_description = "Tanlangan foydalanuvchilarni tasdiqlash"

    def unblock_users(self, request, queryset):
        """Foydalanuvchilarni blokdan chiqarish"""
        updated = queryset.update(is_blocked=False, blocked_until=None, failed_login_attempts=0)
        self.message_user(request, f'{updated} ta foydalanuvchi blokdan chiqarildi.')

    unblock_users.short_description = "Tanlangan foydalanuvchilarni blokdan chiqarish"

    def reset_failed_attempts(self, request, queryset):
        """Muvaffaqiyatsiz urinishlarni tiklash"""
        updated = queryset.update(failed_login_attempts=0)
        self.message_user(request, f'{updated} ta foydalanuvchi uchun urinishlar tiклandi.')

    reset_failed_attempts.short_description = "Muvaffaqiyatsiz urinishlarni tiklash"


@admin.register(AbituriyentProfile)
class AbituriyentProfileAdmin(admin.ModelAdmin):
    """Abituriyent profili admin"""

    list_display = (
        'get_full_name',
        'user_phone',
        'passport_series',
        'age',
        'region',
        'district',
        'profile_completion',
        'created_at_short'
    )

    list_display_links = ('get_full_name',)

    list_filter = (
        'gender',
        'region',
        'district',
        'nationality',
        'created_at'
    )

    search_fields = (
        'first_name',
        'last_name',
        'other_name',
        'passport_series',
        'pinfl',
        'user__phone'
    )

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('last_name', 'first_name', 'other_name', 'birth_date', 'gender', 'nationality')
        }),
        ('Hujjat ma\'lumotlari', {
            'fields': ('passport_series', 'pinfl')
        }),
        ('Manzil ma\'lumotlari', {
            'fields': ('region', 'district', 'address')
        }),
        ('Fayllar', {
            'fields': ('image', 'passport_file'),
            'classes': ('collapse',)
        }),
        ('Vaqt belgilari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'region', 'district')

    def user_phone(self, obj):
        """Foydalanuvchi telefoni"""
        return obj.user.phone

    user_phone.short_description = 'Telefon'

    def age(self, obj):
        """Yosh"""
        return obj.get_age()

    age.short_description = 'Yosh'

    def profile_completion(self, obj):
        """Profil to'liqligi"""
        is_complete = obj.check_profile_completion()
        if is_complete:
            return format_html('<span style="color: green;">✓ To\'liq</span>')
        return format_html('<span style="color: red;">✗ Noto\'liq</span>')

    profile_completion.short_description = 'To\'liqlik'

    def created_at_short(self, obj):
        """Qisqa yaratilgan sana"""
        return obj.created_at.strftime('%d.%m.%Y')

    created_at_short.short_description = 'Yaratilgan'


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    """Telefon tasdiqlash admin"""

    list_display = (
        'phone',
        'code',
        'status_badge',
        'attempts',
        'created_at_short',
        'validity'
    )

    list_filter = (
        'is_used',
        'created_at'
    )

    search_fields = ('phone', 'code')

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('phone', 'code')
        }),
        ('Holat', {
            'fields': ('is_used', 'attempts')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        })
    )

    def status_badge(self, obj):
        """Holat ko'rsatkichi"""
        if obj.is_used:
            return format_html('<span style="color: green;">✓ Ishlatilgan</span>')
        elif obj.is_expired():
            return format_html('<span style="color: red;">✗ Muddati tugagan</span>')
        else:
            return format_html('<span style="color: blue;">● Faol</span>')

    status_badge.short_description = 'Holat'

    def created_at_short(self, obj):
        """Qisqa yaratilgan vaqt"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_short.short_description = 'Yaratilgan'

    def validity(self, obj):
        """Kod haqiqiyligi"""
        if obj.is_valid():
            return format_html('<span style="color: green;">Haqiqiy</span>')
        return format_html('<span style="color: red;">Nohaqiqiy</span>')

    validity.short_description = 'Haqiqiylik'


# Profile admin registrations
@admin.register(OperatorProfile)
class OperatorProfileAdmin(admin.ModelAdmin):
    """Operator profili admin"""

    list_display = ('user', 'shift', 'handled_applications', 'created_at')
    list_filter = ('shift', 'created_at')
    search_fields = ('user__phone', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MarketingProfile)
class MarketingProfileAdmin(admin.ModelAdmin):
    """Marketing profili admin"""

    list_display = ('user', 'department', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('user__phone', 'user__full_name', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MiniAdminProfile)
class MiniAdminProfileAdmin(admin.ModelAdmin):
    """Mini Admin profili admin"""

    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin profili admin"""

    list_display = ('user', 'access_level', 'can_modify_users', 'can_access_reports', 'created_at')
    list_filter = ('access_level', 'can_modify_users', 'can_access_reports', 'created_at')
    search_fields = ('user__phone', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')


# Admin site customization
admin.site.site_header = "Abituriyent Tizimi Boshqaruvi"
admin.site.site_title = "Abituriyent Admin"
admin.site.index_title = "Boshqaruv Paneli"