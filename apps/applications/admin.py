from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Application, ApplicationStatus, AdmissionType


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name', 'get_user_phone', 'program', 'branch',
        'admission_type', 'status_badge', 'get_reviewed_by', 'created_at'
    ]

    list_filter = [
        'status', 'admission_type', 'branch', 'education_level',
        'education_form', 'created_at', 'updated_at'
    ]

    search_fields = [
        'user__first_name', 'user__last_name', 'user__phone',
        'program__name', 'branch__name'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Foydalanuvchi ma\'lumotlari', {
            'fields': ('user', 'admission_type')
        }),
        ('Ta\'lim ma\'lumotlari', {
            'fields': ('branch', 'education_level', 'education_form', 'program')
        }),
        ('Diplom ma\'lumotlari', {
            'fields': ('diplom', 'transfer_diplom', 'course'),
            'classes': ('collapse',)
        }),
        ('Ariza holati', {
            'fields': ('status', 'reviewed_by', 'contract_file')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_review', 'accept_applications', 'reject_applications']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'branch', 'education_level', 'education_form',
            'program', 'reviewed_by', 'diplom', 'transfer_diplom', 'course'
        )

    def get_user_name(self, obj):
        return getattr(obj.user, 'full_name', None) or f"{obj.user.first_name} {obj.user.last_name}".strip()

    get_user_name.short_description = 'F.I.Sh'
    get_user_name.admin_order_field = 'user__first_name'

    def get_user_phone(self, obj):
        return obj.user.phone

    get_user_phone.short_description = 'Telefon'
    get_user_phone.admin_order_field = 'user__phone'

    def status_badge(self, obj):
        colors = {
            'topshirildi': '#ffc107',
            'korib_chiqilmoqda': '#17a2b8',
            'qabul_qilindi': '#28a745',
            'rad_etildi': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Holat'
    status_badge.admin_order_field = 'status'

    def get_reviewed_by(self, obj):
        if obj.reviewed_by:
            return getattr(obj.reviewed_by, 'full_name', None) or obj.reviewed_by.username
        return '-'

    get_reviewed_by.short_description = 'Ko\'rib chiquvchi'
    get_reviewed_by.admin_order_field = 'reviewed_by__first_name'

    def mark_as_review(self, request, queryset):
        updated = queryset.filter(
            status=ApplicationStatus.PENDING
        ).update(
            status=ApplicationStatus.REVIEW,
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} ta ariza ko\'rib chiqish uchun belgilandi.')

    mark_as_review.short_description = 'Tanlangan arizalarni ko\'rib chiqish uchun belgilash'

    def accept_applications(self, request, queryset):
        updated = queryset.filter(
            status__in=[ApplicationStatus.PENDING, ApplicationStatus.REVIEW]
        ).update(
            status=ApplicationStatus.ACCEPTED,
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} ta ariza qabul qilindi.')

    accept_applications.short_description = 'Tanlangan arizalarni qabul qilish'

    def reject_applications(self, request, queryset):
        updated = queryset.filter(
            status__in=[ApplicationStatus.PENDING, ApplicationStatus.REVIEW]
        ).update(
            status=ApplicationStatus.REJECTED,
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} ta ariza rad etildi.')

    reject_applications.short_description = 'Tanlangan arizalarni rad etish'

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == ApplicationStatus.ACCEPTED:
            return False
        return super().has_delete_permission(request, obj)