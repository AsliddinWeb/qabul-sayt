# apps/settings/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import ContractTemplate, ContractSettings


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active_badge', 'has_ikki_tomonlama', 'has_uch_tomonlama', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'is_active')
        }),
        ('Ikki tomonlama shartnoma', {
            'fields': ('ikki_tomonlama',),
            'classes': ('collapse',),
            'description': 'Talaba va muassasa o\'rtasidagi shartnoma'
        }),
        ('Uch tomonlama shartnoma', {
            'fields': ('uch_tomonlama',),
            'classes': ('collapse',),
            'description': 'Talaba, ota-ona va muassasa o\'rtasidagi shartnoma'
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Faol</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">Faolsiz</span>'
        )

    is_active_badge.short_description = 'Holat'

    def has_ikki_tomonlama(self, obj):
        return '✅' if obj.ikki_tomonlama else '❌'

    has_ikki_tomonlama.short_description = 'Ikki tomonlama'

    def has_uch_tomonlama(self, obj):
        return '✅' if obj.uch_tomonlama else '❌'

    has_uch_tomonlama.short_description = 'Uch tomonlama'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # CKEditor uchun help text qo'shish
        placeholders_help = """
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <strong>Mavjud placeholder lar:</strong><br>
            <code>{{TALABA_ISMI}}</code> - Talaba ism-sharifi<br>
            <code>{{TELEFON}}</code> - Talaba telefon raqami<br>
            <code>{{FILIAL}}</code> - Filial nomi<br>
            <code>{{YONALISH}}</code> - Ta'lim yo'nalishi<br>
            <code>{{TALIM_DARAJASI}}</code> - Ta'lim darajasi<br>
            <code>{{TALIM_SHAKLI}}</code> - Ta'lim shakli<br>
            <code>{{QABUL_TURI}}</code> - Qabul turi<br>
            <code>{{SANA}}</code> - Bugungi sana<br>
            <small><em>Uch tomonlama uchun qo'shimcha:</em></small><br>
            <code>{{OTA_ONA_ISMI}}</code> - Ota-ona ism-sharifi<br>
            <code>{{OTA_ONA_TELEFON}}</code> - Ota-ona telefon raqami
        </div>
        """

        if 'ikki_tomonlama' in form.base_fields:
            form.base_fields['ikki_tomonlama'].help_text = mark_safe(placeholders_help)
        if 'uch_tomonlama' in form.base_fields:
            form.base_fields['uch_tomonlama'].help_text = mark_safe(placeholders_help)

        return form


@admin.register(ContractSettings)
class ContractSettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'default_contract_type', 'auto_generate_pdf', 'updated_at']

    fieldsets = (
        ('Shartnoma sozlamalari', {
            'fields': ('default_contract_type', 'auto_generate_pdf', 'pdf_page_size')
        }),
        ('Muassasa ma\'lumotlari', {
            'fields': ('company_name', 'company_address', 'director_name')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def has_add_permission(self, request):
        # Faqat bitta sozlama obyekti bo'lishi mumkin
        return not ContractSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Sozlamalarni o'chirib bo'lmaydi
        return False

    def changelist_view(self, request, extra_context=None):
        # Agar sozlama yo'q bo'lsa, avtomatik yaratish
        if not ContractSettings.objects.exists():
            ContractSettings.objects.create()
        return super().changelist_view(request, extra_context)