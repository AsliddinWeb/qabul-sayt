# apps/applications/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect, HttpResponse
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.apps import apps
from weasyprint import HTML

import tempfile
import os
import qrcode
import base64
from io import BytesIO
from datetime import datetime

# Import Export
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from .models import Application, ApplicationStatus, AdmissionType
from .resources import ApplicationResource

# Quizes
from apps.quizes.models import TestResult, TestAttempt, ProgramTest
import random
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

# Sms
from .utils import send_success_application


@admin.register(Application)
class ApplicationAdmin(ImportExportModelAdmin):
    """Application admin with Import/Export functionality"""

    # Import/Export resource
    resource_class = ApplicationResource

    # Import/Export formats
    formats = [base_formats.XLSX, base_formats.CSV]

    # Custom template paths
    import_template_name = 'admin/import_export/import.html'
    export_template_name = 'admin/import_export/export.html'
    confirm_template_name = 'admin/import_export/confirm_import.html'

    list_display = [
        'get_user_name', 'get_user_phone', 'program', 'branch',
        'admission_type', 'status_badge', 'test_status_badge', 'created_at', 'contract_actions'
    ]

    list_filter = [
        'status', 'admission_type', 'branch', 'education_level',
        'education_form', 'program', 'test_completed', 'test_passed', 'created_at'
    ]

    search_fields = [
        'user__phone', 'user__full_name',
        'user__abituriyent_profile__last_name',
        'user__abituriyent_profile__first_name',
        'program__name', 'branch__name'
    ]

    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'get_user_diplom_info']

    actions = [
        'export_admin_action',
        'pass_selected_through_test',  # YANGI ACTION
    ]

    def get_actions(self, request):
        """Default delete actionni olib tashlash"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # EXPORT FUNKSIYALARINI TO'LIQ OVERRIDE QILISH
    def export_action(self, request, *args, **kwargs):
        """Custom export action with full admin context"""
        if request.method == 'POST':
            file_format = request.POST.get('file_format')

            # Barcha ma'lumotlarni olish
            queryset = self.get_export_queryset(request)
            resource = self.resource_class()

            try:
                if file_format == '0':  # Excel
                    dataset = resource.export(queryset)
                    response = HttpResponse(
                        dataset.xlsx,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    filename = f"arizalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'

                elif file_format == '1':  # CSV
                    dataset = resource.export(queryset)
                    response = HttpResponse(dataset.csv, content_type='text/csv; charset=utf-8')
                    filename = f"arizalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'

                else:
                    messages.error(request, 'Noto\'g\'ri format tanlandi!')
                    return HttpResponseRedirect(request.get_full_path())

                messages.success(request, f'✅ {queryset.count()} ta ariza muvaffaqiyatli export qilindi!')
                return response

            except Exception as e:
                messages.error(request, f'Export qilishda xatolik: {str(e)}')
                return HttpResponseRedirect(request.get_full_path())

        # GET request uchun - to'liq admin context bilan export formini ko'rsatish
        opts = self.model._meta
        app_label = opts.app_label

        # To'liq admin context yaratish
        context = {
            'title': f'{opts.verbose_name_plural} export qilish',
            'subtitle': None,
            'opts': opts,
            'app_label': app_label,
            'has_permission': True,
            'has_view_permission': self.has_view_permission(request),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
            'has_export_permission': self.has_export_permission(request),
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'site_url': admin.site.site_url,
            'is_nav_sidebar_enabled': True,
            'available_apps': admin.site.get_app_list(request),
            'is_popup': False,
            'to_field': None,
            'cl': None,
            'preserved_filters': '',
            'add_url': reverse('admin:applications_application_add'),
            'change_url': reverse('admin:applications_application_changelist'),
        }

        # App config qo'shish
        try:
            context['app_config'] = apps.get_app_config(app_label)
        except LookupError:
            context['app_config'] = None

        return render(request, 'admin/import_export/export.html', context)

    def export_admin_action(self, request, queryset):
        """Admin action orqali export qilish"""
        resource = self.resource_class()
        dataset = resource.export(queryset)

        response = HttpResponse(
            dataset.xlsx,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        filename = f"tanlangan_arizalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        self.message_user(
            request,
            f"✅ {queryset.count()} ta ariza Excel formatida export qilindi.",
            messages.SUCCESS
        )

        return response

    export_admin_action.short_description = "📊 Tanlanganlarni Excel formatida export qilish"

    def get_export_queryset(self, request):
        """Export uchun optimized queryset"""
        return super().get_queryset(request).select_related(
            'user', 'branch', 'education_level', 'education_form', 'program', 'reviewed_by'
        ).prefetch_related(
            'user__abituriyent_profile',
            'user__abituriyent_profile__region',
            'user__abituriyent_profile__district'
        )

    def has_import_permission(self, request):
        """Import ruxsatini tekshirish"""
        return request.user.has_perm('applications.add_application')

    def has_export_permission(self, request):
        """Export ruxsatini tekshirish"""
        return request.user.has_perm('applications.view_application')

    def pass_selected_through_test(self, request, queryset):
        """Tanlanganlarni testdan 55+ ball bilan o'tkazish"""
        
        # Faqat test ma'lumotlari yo'q applicationlarni filtrlash
        applications_without_test = queryset.filter(test_completed__isnull=True)
        
        if not applications_without_test.exists():
            self.message_user(
                request,
                "❌ Tanlangan applicationlarda test ma'lumotlari allaqachon mavjud!",
                messages.WARNING
            )
            return
        
        success_count = 0
        error_count = 0
        
        with transaction.atomic():
            for application in applications_without_test:
                try:
                    # Test ma'lumotlarini yaratish
                    test_data = self._generate_test_data(application)
                    
                    # Application yangilash
                    Application.objects.filter(id=application.id).update(**test_data)
                    
                    # TestAttempt va TestResult yaratish (agar quizes app mavjud bo'lsa)
                    self._create_test_records(application, test_data)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    # Log qilish (ixtiyoriy)
                    print(f"Test yaratishda xatolik (Application {application.id}): {str(e)}")
        
        # Natija xabari
        if success_count > 0:
            self.message_user(
                request,
                f"✅ {success_count} ta application muvaffaqiyatli testdan o'tkazildi (55+ ball)!",
                messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request,
                f"⚠️ {error_count} ta applicationda xatolik yuz berdi",
                messages.WARNING
            )

    pass_selected_through_test.short_description = "🎯 Tanlanganlarni testdan o'tkazish (55+ ball)"

    def _generate_test_data(self, application):
        """Application uchun test ma'lumotlari yaratish"""
        
        # 55 dan 100 gacha ball (o'tish balli 55+)
        base_score = random.randint(55, 100)
        
        # Agar application qabul qilingan bo'lsa, yuqori ball berish
        if application.status == 'qabul_qilindi':
            base_score = random.randint(75, 100)
        elif application.status == 'korib_chiqilmoqda':
            base_score = random.randint(65, 95)
        else:
            base_score = random.randint(55, 85)
        
        # Test sanasi (1-90 kun oldin)
        days_ago = random.randint(1, 90)
        test_date = timezone.now() - timedelta(days=days_ago)
        
        return {
            'test_completed': True,
            'test_score': base_score,
            'test_passed': True,  # Har doim True (55+ ball)
            'test_date': test_date
        }

    def _create_test_records(self, application, test_data):
        """TestAttempt va TestResult yaratish (agar quizes app mavjud bo'lsa)"""
        try:
            # ProgramTest ni topish
            if not hasattr(application.program, 'test_config'):
                # Agar program test config yo'q bo'lsa, skip qilish
                return
            
            program_test = application.program.test_config
            
            # Ballni 2 ta fanga taqsim qilish
            total_score = test_data['test_score']
            
            # Har bir fan maksimal 50 ball
            subject_1_score = random.randint(
                max(20, total_score - 50),  # Minimal 20, maksimal (total_score - 50)
                min(50, total_score - 5)    # Maksimal 50, minimal (total_score - 5)
            )
            subject_2_score = total_score - subject_1_score
            
            # subject_2_score ni ham cheklash
            if subject_2_score > 50:
                subject_2_score = 50
                subject_1_score = total_score - 50
            elif subject_2_score < 5:
                subject_2_score = 5
                subject_1_score = total_score - 5
            
            # Vaqt (30-90 daqiqa)
            time_spent = random.randint(1800, 5400)  # 30-90 daqiqa (soniyalarda)
            
            # TestAttempt yaratish
            attempt = TestAttempt.objects.create(
                application=application,
                program_test=program_test,
                attempt_number=1,
                status='completed',
                started_at=test_data['test_date'],
                completed_at=test_data['test_date'] + timezone.timedelta(seconds=time_spent),
                time_spent=time_spent,
                subject_1_score=subject_1_score,
                subject_2_score=subject_2_score,
                total_score=total_score,
                percentage=(total_score / 100) * 100,
                is_passed=True  # Har doim True (55+ ball)
            )
            
            # TestResult yaratish
            TestResult.objects.create(
                application=application,
                best_attempt=attempt,
                best_total_score=total_score,
                best_percentage=(total_score / 100) * 100,
                is_test_passed=True,  # Har doim True
                best_subject_1_score=subject_1_score,
                best_subject_2_score=subject_2_score,
                total_attempts=1,
                last_attempt_date=test_data['test_date']
            )
            
        except Exception as e:
            # Agar quizes app yo'q bo'lsa yoki boshqa xatolik bo'lsa, 
            # faqat Application test ma'lumotlarini saqlaymiz
            pass
    
    # URL PATTERNS QO'SHISH
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'export/',
                self.admin_site.admin_view(self.export_action),
                name='applications_application_export'
            ),
            path(
                '<int:application_id>/generate-contract/<str:contract_type>/',
                self.admin_site.admin_view(self.generate_contract_view),
                name='applications_application_generate_contract'
            ),
            # YANGI: Download view uchun URL
            path(
                '<int:application_id>/download-contract/',
                self.admin_site.admin_view(self.download_contract_view),
                name='applications_application_download_contract'
            ),
        ]
        return custom_urls + urls

    def get_fieldsets(self, request, obj=None):
        """Admission type ga qarab fieldsets ni dinamik ravishda qaytarish"""
        base_fieldsets = [
            ('Foydalanuvchi ma\'lumotlari', {
                'fields': ('user', 'admission_type', 'get_user_diplom_info')
            }),
            ('Ta\'lim ma\'lumotlari', {
                'fields': ('branch', 'education_level', 'education_form', 'program')
            }),
            ('Ariza holati', {
                'fields': ('status', 'reviewed_by', 'contract_file')
            }),
            # ✅ YANGI: Test ma'lumotlari fieldset
            ('Test ma\'lumotlari', {
                'fields': ('test_completed', 'test_score', 'test_passed', 'test_date'),
                'description': 'Abituriyent test natijalari haqida ma\'lumot'
            }),
        ]

        if obj:
            if obj.admission_type == AdmissionType.REGULAR:
                base_fieldsets.insert(2, ('Diplom ma\'lumotlari', {
                    'fields': ('diplom',),
                    'description': 'Yangi qabul turi uchun diplom ma\'lumotlari'
                }))
            elif obj.admission_type == AdmissionType.TRANSFER:
                base_fieldsets.insert(2, ('Perevod ma\'lumotlari', {
                    'fields': ('transfer_diplom', 'course'),
                    'description': 'Perevod turi uchun oliy ta\'lim diplomi va kurs ma\'lumotlari'
                }))
        else:
            base_fieldsets.insert(2, ('Diplom/Perevod ma\'lumotlari', {
                'fields': ('diplom', 'transfer_diplom', 'course'),
                'description': 'Qabul turiga qarab tegishli maydonni to\'ldiring'
            }))

        return base_fieldsets

    def get_user_diplom_info(self, obj):
        """Foydalanuvchining diplom ma'lumotlarini ko'rsatish"""
        if not obj or not obj.user:
            return "Ma'lumot yo'q"

        user = obj.user
        diplom_info = []

        try:
            if hasattr(user, 'diplom') and user.diplom:
                diplom_info.append(format_html(
                    '<div style="margin-bottom: 10px; padding: 10px; background: #e8f5e8; border-left: 4px solid #28a745;">'
                    '<strong>📜 Oddiy diplom:</strong><br>'
                    '• Seriya/Raqam: {}<br>'
                    '• Universitet: {}<br>'
                    '• Bitirgan yil: {}<br>'
                    '• Ta\'lim turi: {}<br>'
                    '• Muassasa turi: {}'
                    '</div>',
                    user.diplom.serial_number or 'N/A',
                    (user.diplom.university_name[:50] + '...' if len(
                        user.diplom.university_name) > 50 else user.diplom.university_name) if user.diplom.university_name else 'N/A',
                    user.diplom.graduation_year or 'N/A',
                    user.diplom.education_type.name if user.diplom.education_type else 'N/A',
                    user.diplom.institution_type.name if user.diplom.institution_type else 'N/A'
                ))
        except Exception:
            pass

        try:
            if hasattr(user, 'transfer_diplom') and user.transfer_diplom:
                diplom_info.append(format_html(
                    '<div style="margin-bottom: 10px; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196f3;">'
                    '<strong>🎓 Transfer diplom:</strong><br>'
                    '• Davlat: {}<br>'
                    '• Universitet: {}<br>'
                    '• Maqsadli kurs: {}'
                    '</div>',
                    user.transfer_diplom.country.name if user.transfer_diplom.country else 'N/A',
                    (user.transfer_diplom.university_name[:50] + '...' if len(
                        user.transfer_diplom.university_name) > 50 else user.transfer_diplom.university_name) if user.transfer_diplom.university_name else 'N/A',
                    user.transfer_diplom.target_course.name if user.transfer_diplom.target_course else 'N/A'
                ))
        except Exception:
            pass

        if not diplom_info:
            return format_html(
                '<div style="padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107;">'
                '<strong>⚠️ Diqqat:</strong> Foydalanuvchida diplom ma\'lumotlari topilmadi!'
                '</div>'
            )

        return format_html(''.join(diplom_info))

    get_user_diplom_info.short_description = 'Foydalanuvchi diplom ma\'lumotlari'

    def get_user_name(self, obj):
        try:
            if hasattr(obj.user, 'abituriyent_profile') and obj.user.abituriyent_profile:
                profile = obj.user.abituriyent_profile
                name_parts = [
                    profile.last_name or '',
                    profile.first_name or '',
                    profile.other_name or ''
                ]
                full_name = ' '.join(part.strip() for part in name_parts if part.strip())
                return full_name or obj.user.phone
            elif obj.user.full_name:
                return obj.user.full_name
            else:
                return obj.user.phone
        except Exception:
            return obj.user.phone

    get_user_name.short_description = 'F.I.Sh'

    def get_user_phone(self, obj):
        return obj.user.phone

    get_user_phone.short_description = 'Telefon'

    def status_badge(self, obj):
        """Bootstrap badge bilan chiroyli status ko'rsatish"""
        status_classes = {
            'topshirildi': 'badge badge-warning',
            'korib_chiqilmoqda': 'badge badge-info',
            'qabul_qilindi': 'badge badge-success',
            'rad_etildi': 'badge badge-danger'
        }

        status_icons = {
            'topshirildi': '📋',
            'korib_chiqilmoqda': '👀',
            'qabul_qilindi': '✅',
            'rad_etildi': '❌'
        }

        badge_class = status_classes.get(obj.status, 'badge badge-secondary')
        icon = status_icons.get(obj.status, '📄')

        return format_html(
            '<span class="{} px-2 py-1" style="font-size: 12px;">{} {}</span>',
            badge_class, icon, obj.get_status_display()
        )

    status_badge.short_description = 'Holat'

    # ✅ YANGI: Test holati badge
    def test_status_badge(self, obj):
        """Test holati badge"""
        if obj.test_completed is None:
            return format_html(
                '<span class="badge badge-secondary px-2 py-1" style="font-size: 11px;">➖ Test topshirmagan</span>'
            )
        elif obj.test_completed and obj.test_passed:
            return format_html(
                '<span class="badge badge-success px-2 py-1" style="font-size: 11px;">✅ O\'tdi ({} ball)</span>',
                obj.test_score or 0
            )
        elif obj.test_completed and not obj.test_passed:
            return format_html(
                '<span class="badge badge-danger px-2 py-1" style="font-size: 11px;">❌ O\'tmadi ({} ball)</span>',
                obj.test_score or 0
            )
        elif obj.test_completed:
            return format_html(
                '<span class="badge badge-info px-2 py-1" style="font-size: 11px;">📝 Topshirdi ({} ball)</span>',
                obj.test_score or 0
            )
        else:
            return format_html(
                '<span class="badge badge-warning px-2 py-1" style="font-size: 11px;">⏳ Kutilmoqda</span>'
            )

    test_status_badge.short_description = 'Test holati'

    def contract_actions(self, obj):
        """Bootstrap shartnoma tugmalari - to'g'ri fayl nomi bilan"""
        if obj.contract_file:
            # Admin URL orqali download qilish
            download_url = reverse('admin:applications_application_download_contract', args=[obj.id])
            return format_html(
                '<div class="btn-group" role="group">'
                '<a href="{}" class="btn btn-success btn-sm">'
                '<i class="fas fa-download"></i> Yuklab olish'
                '</a>'
                '</div>',
                download_url
            )
        else:
            ikki_url = reverse('admin:applications_application_generate_contract',
                            args=[obj.id, 'ikki_tomonlama'])
            uch_url = reverse('admin:applications_application_generate_contract',
                            args=[obj.id, 'uch_tomonlama'])

            return format_html(
                '<div class="btn-group" role="group">'
                '<a href="{}" class="btn btn-primary btn-sm">'
                '<i class="fas fa-file-contract"></i> Ikki tomonlama'
                '</a>'
                '<a href="{}" class="btn btn-info btn-sm ml-1">'
                '<i class="fas fa-users"></i> Uch tomonlama'
                '</a>'
                '</div>',
                ikki_url, uch_url
            )

    contract_actions.short_description = 'Shartnoma Amallar'

    def download_contract_view(self, request, application_id):
        """Shartnomani to'g'ri nom bilan yuklab olish"""
        application = get_object_or_404(Application, id=application_id)
        
        if not application.contract_file:
            messages.error(request, "Shartnoma fayli topilmadi!")
            return HttpResponseRedirect(reverse('admin:applications_application_change', args=[application_id]))
        
        try:
            # Fayl nomini aniqlash
            original_filename = os.path.basename(application.contract_file.name)
            
            # Contract turini aniqlash (fayl nomidan)
            if 'ikki_tomonlama' in original_filename.lower():
                contract_type = 'ikki_tomonlama'
            elif 'uch_tomonlama' in original_filename.lower():
                contract_type = 'uch_tomonlama'
            else:
                contract_type = 'shartnoma'
            
            # To'g'ri fayl nomini yaratish
            safe_name = self.get_safe_filename(application.user)
            proper_filename = f"{safe_name}_{contract_type}.pdf"
            
            # Faylni o'qish va yuborish
            file_content = application.contract_file.read()
            
            # PDF yoki HTML ekanligini tekshirish
            content_type = 'application/pdf'
            if original_filename.endswith('.html'):
                content_type = 'text/html'
                proper_filename = proper_filename.replace('.pdf', '.html')
            
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{proper_filename}"'
            
            return response
            
        except Exception as e:
            messages.error(request, f"Faylni yuklab olishda xatolik: {str(e)}")
            return HttpResponseRedirect(reverse('admin:applications_application_change', args=[application_id]))

    def generate_qr_code(self, url):
        """QR kod yaratish"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
        except Exception:
            return None

    def get_safe_filename(self, user):
        """Xavfsiz fayl nomi yaratish"""
        try:
            if hasattr(user, 'abituriyent_profile') and user.abituriyent_profile:
                profile = user.abituriyent_profile
                name_parts = [
                    profile.last_name or '',
                    profile.first_name or '',
                    profile.other_name or ''
                ]
                full_name = '_'.join(part.strip() for part in name_parts if part.strip())
                safe_name = ''.join(c for c in full_name if c.isalnum() or c == '_')
                return safe_name.upper() or 'USER'
            else:
                phone = user.phone.replace('+', '').replace(' ', '').replace('-', '')
                return f"USER_{phone}"
        except Exception:
            return f"USER_{user.id}"

    def get_replacement_data(self, application, request, contract_type):
        """Shartnoma uchun ma'lumotlar"""
        talaba_ismi = "N/A"
        try:
            if hasattr(application.user, 'abituriyent_profile') and application.user.abituriyent_profile:
                profile = application.user.abituriyent_profile
                name_parts = [
                    profile.last_name or '',
                    profile.first_name or '',
                    profile.other_name or ''
                ]
                talaba_ismi = ' '.join(part.strip() for part in name_parts if part.strip())
            elif application.user.full_name:
                talaba_ismi = application.user.full_name
            else:
                talaba_ismi = application.user.phone
        except Exception:
            talaba_ismi = application.user.phone

        safe_name = self.get_safe_filename(application.user)
        filename = f"{safe_name}_{contract_type}.pdf"
        
        # SMS uchun URL - avvalgi holatda
        download_url = request.build_absolute_uri(f"/applications/contract/{application.id}/")
        qr_code_data = self.generate_qr_code(download_url)

        # Xavfsiz ma'lumot olish
        talaba_manzili = ''
        passport_seriya = ''
        oquv_kursi = "1-kurs"

        try:
            if hasattr(application.user, 'abituriyent_profile') and application.user.abituriyent_profile:
                profile = application.user.abituriyent_profile
                if hasattr(profile, 'get_full_address'):
                    talaba_manzili = profile.get_full_address
                passport_seriya = profile.passport_series or ''
        except Exception:
            pass

        try:
            if application.admission_type == AdmissionType.TRANSFER and hasattr(application.user,
                                                                                'transfer_diplom') and application.user.transfer_diplom:
                oquv_kursi = application.user.transfer_diplom.target_course.name if application.user.transfer_diplom.target_course else "1-kurs"
        except Exception:
            pass

        return {
            'ID': application.id,
            'KONTRAKT_SUMMASI': application.program.tuition_fee if application.program else 0,
            'TALABA_MANZILI': talaba_manzili,
            'PASSPORT_SERIYA': passport_seriya,
            'OQUV_KURSI': oquv_kursi,
            'OQISH_MUDDATI': application.program.study_duration if application.program else '',
            'TALABA_ISMI': talaba_ismi,
            'TELEFON': application.user.phone,
            'FILIAL': application.branch.name if application.branch else '',
            'YONALISH': application.program.name if application.program else '',
            'YONALISH_SERIYA': application.program.contract_series if application.program else '',
            'TALIM_DARAJASI': application.education_level.name if application.education_level else '',
            'TALIM_SHAKLI': application.education_form.name if application.education_form else '',
            'QABUL_TURI': application.get_admission_type_display(),
            'SANA': datetime.now().strftime('%d.%m.%Y'),
            'QR_CODE_DATA': qr_code_data,
            'DOWNLOAD_URL': download_url,
        }

    def generate_contract_view(self, request, application_id, contract_type):
        """Shartnoma yaratish view"""
        application = get_object_or_404(Application, id=application_id)

        try:
            template_name = f'contracts/{contract_type}.html'
            template = get_template(template_name)
            context = self.get_replacement_data(application, request, contract_type)
            html_content = template.render(context)
            safe_name = self.get_safe_filename(application.user)
            filename = f"{safe_name}_{contract_type}.pdf"

            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, 'contract.pdf')

            try:
                HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(temp_pdf_path)

                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()

                    # Faqat filename, upload_to allaqachon 'contracts/%Y/%m/' formatida
                    relative_path = filename
                    application.contract_file.save(relative_path, ContentFile(pdf_content), save=False)

                    success_message = f"✅ {contract_type.replace('_', ' ').title()} PDF shartnoma yaratildi"
                else:
                    raise Exception("PDF fayl yaratilmadi")

            except Exception as pdf_error:
                html_filename = f"{safe_name}_{contract_type}.html"
                application.contract_file.save(html_filename, ContentFile(html_content.encode('utf-8')), save=False)
                success_message = f"⚠️ {contract_type.replace('_', ' ').title()} HTML shartnoma yaratildi (PDF xatolik: {str(pdf_error)})"

            try:
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                os.rmdir(temp_dir)
            except:
                pass

            application.status = ApplicationStatus.ACCEPTED
            application.reviewed_by = request.user
            application.save(update_fields=['contract_file', 'status', 'reviewed_by'])
            messages.success(request, success_message)

        except TemplateDoesNotExist:
            messages.error(request, f"❌ Template topilmadi: {template_name}")
        except Exception as e:
            messages.error(request, f"❌ Xatolik: {str(e)}")

        # SMS yuborish - avvalgi URL bilan
        try:
            contract_url = request.build_absolute_uri(f"/applications/contract/{application.id}/")
            
            send_sms_result = send_success_application(
                phone=application.user.phone,
                full_name=application.user.full_name or application.user.phone,
                application_link=contract_url
            )
            
            if send_sms_result:
                messages.success(request, f"✅ SMS muvaffaqiyatli yuborildi: {application.user.phone}")
            else:
                messages.warning(request, f"⚠️ SMS yuborishda xatolik: {application.user.phone}")
                messages.info(request, f"🔗 Shartnoma havolasi: {contract_url}")
                
        except Exception as sms_error:
            messages.error(request, f"❌ SMS xatolik: {str(sms_error)}")
            messages.info(request, f"🔗 Shartnoma manzili: {request.build_absolute_uri(f'/applications/contract/{application.id}/')}")

        return HttpResponseRedirect(reverse('admin:applications_application_change', args=[application.id]))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generate_contract'] = True
        return super().change_view(request, object_id, form_url, extra_context)