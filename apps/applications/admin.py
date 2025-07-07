from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from weasyprint import HTML
import tempfile
import os
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from .models import Application, ApplicationStatus, AdmissionType


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_name', 'get_user_phone', 'program', 'branch',
        'admission_type', 'status_badge', 'created_at', 'contract_actions'
    ]

    list_filter = [
        'status', 'admission_type', 'branch', 'education_level',
        'education_form', 'created_at'
    ]

    search_fields = [
        'user__phone', 'user__full_name',
        'user__abituriyent_profile__last_name',
        'user__abituriyent_profile__first_name',
        'program__name', 'branch__name'
    ]

    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'get_user_diplom_info']
    actions = ['generate_ikki_tomonlama_bulk', 'generate_uch_tomonlama_bulk']

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
        ]

        if obj:  # Mavjud obyekt uchun
            if obj.admission_type == AdmissionType.REGULAR:
                # Yangi qabul uchun - faqat diplom
                base_fieldsets.insert(2, ('Diplom ma\'lumotlari', {
                    'fields': ('diplom',),
                    'description': 'Yangi qabul turi uchun diplom ma\'lumotlari'
                }))
            elif obj.admission_type == AdmissionType.TRANSFER:
                # Perevod uchun - transfer diplom va course
                base_fieldsets.insert(2, ('Perevod ma\'lumotlari', {
                    'fields': ('transfer_diplom', 'course'),
                    'description': 'Perevod turi uchun oliy ta\'lim diplomi va kurs ma\'lumotlari'
                }))
        else:  # Yangi obyekt uchun
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

        # Oddiy diplom ma'lumotlari
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
                user.diplom.serial_number,
                user.diplom.university_name[:50] + '...' if len(user.diplom.university_name) > 50 else user.diplom.university_name,
                user.diplom.graduation_year,
                user.diplom.education_type.name,
                user.diplom.institution_type.name
            ))

        # Transfer diplom ma'lumotlari
        if hasattr(user, 'transfer_diplom') and user.transfer_diplom:
            diplom_info.append(format_html(
                '<div style="margin-bottom: 10px; padding: 10px; background: #e3f2fd; border-left: 4px solid #2196f3;">'
                '<strong>🎓 Transfer diplom:</strong><br>'
                '• Davlat: {}<br>'
                '• Universitet: {}<br>'
                '• Maqsadli kurs: {}'
                '</div>',
                user.transfer_diplom.country.name,
                user.transfer_diplom.university_name[:50] + '...' if len(user.transfer_diplom.university_name) > 50 else user.transfer_diplom.university_name,
                user.transfer_diplom.target_course.name
            ))

        if not diplom_info:
            return format_html(
                '<div style="padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107;">'
                '<strong>⚠️ Diqqat:</strong> Foydalanuvchida diplom ma\'lumotlari topilmadi!<br>'
                'Ariza topshirishdan oldin diplom ma\'lumotlarini kiritish kerak.'
                '</div>'
            )

        return format_html(''.join(diplom_info))

    get_user_diplom_info.short_description = 'Foydalanuvchi diplom ma\'lumotlari'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ForeignKey maydonlari uchun querysetni cheklash"""
        if db_field.name == "diplom":
            # Faqat joriy foydalanuvchining diplomini ko'rsatish
            if hasattr(request, '_obj_') and request._obj_ and request._obj_.user:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request._obj_.user)
            else:
                kwargs["queryset"] = db_field.related_model.objects.none()

        elif db_field.name == "transfer_diplom":
            # Faqat joriy foydalanuvchining transfer diplomini ko'rsatish
            if hasattr(request, '_obj_') and request._obj_ and request._obj_.user:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request._obj_.user)
            else:
                kwargs["queryset"] = db_field.related_model.objects.none()

        elif db_field.name == "course":
            # Faqat transfer diplom mavjud bo'lsa kurslarni ko'rsatish
            if hasattr(request, '_obj_') and request._obj_ and request._obj_.user:
                if hasattr(request._obj_.user, 'transfer_diplom') and request._obj_.user.transfer_diplom:
                    # Transfer diplom mavjud bo'lsa barcha kurslarni ko'rsatish
                    pass  # Default queryset
                else:
                    kwargs["queryset"] = db_field.related_model.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """Formni olishdan oldin obj ni request ga qo'shish"""
        request._obj_ = obj
        form = super().get_form(request, obj, **kwargs)

        # Admission type ga qarab maydonlarni yashirish/ko'rsatish
        if obj:
            if obj.admission_type == AdmissionType.REGULAR:
                # Yangi qabul - transfer diplom va course ni yashirish
                if 'transfer_diplom' in form.base_fields:
                    del form.base_fields['transfer_diplom']
                if 'course' in form.base_fields:
                    del form.base_fields['course']
            elif obj.admission_type == AdmissionType.TRANSFER:
                # Perevod - diplom ni yashirish
                if 'diplom' in form.base_fields:
                    del form.base_fields['diplom']

        return form

    def get_user_name(self, obj):
        # AbituriyentProfile dan yoki User.full_name dan ismni olish
        try:
            if hasattr(obj.user, 'abituriyent_profile'):
                profile = obj.user.abituriyent_profile
                return f"{profile.last_name} {profile.first_name} {profile.other_name}".strip()
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

    def contract_actions(self, obj):
        """Bootstrap bilan chiroyli shartnoma tugmalari"""
        if obj.contract_file:
            # Shartnoma allaqachon mavjud
            download_url = f"/media/{obj.contract_file.name}"
            return format_html(
                '<div class="btn-group" role="group">'
                '<a href="{}" target="_blank" class="btn btn-success btn-sm">'
                '<i class="fas fa-download"></i> Yuklab olish'
                '</a>'
                '</div>',
                download_url
            )
        else:
            # Yangi shartnoma yaratish tugmalari
            ikki_url = reverse('admin:applications_application_generate_contract',
                               args=[obj.id, 'ikki_tomonlama'])
            uch_url = reverse('admin:applications_application_generate_contract',
                              args=[obj.id, 'uch_tomonlama'])

            return format_html(
                '<div class="btn-group" role="group" aria-label="Shartnoma tugmalari">'
                '<a href="{}" class="btn btn-primary btn-sm" title="Ikki tomonlama shartnoma">'
                '<i class="fas fa-file-contract"></i> Ikki tomonlama'
                '</a>'
                '<a href="{}" class="btn btn-purple btn-sm ml-1" title="Uch tomonlama shartnoma" '
                'style="background-color: #6f42c1; border-color: #6f42c1; color: white;">'
                '<i class="fas fa-users"></i> Uch tomonlama'
                '</a>'
                '</div>',
                ikki_url, uch_url
            )

    contract_actions.short_description = 'Shartnoma Amallar'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:application_id>/generate-contract/<str:contract_type>/',
                self.admin_site.admin_view(self.generate_contract_view),
                name='applications_application_generate_contract'
            ),
        ]
        return custom_urls + urls

    def generate_qr_code(self, url):
        """Haqiqiy QR kod yaratish"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            # QR kod rasmini yaratish
            img = qr.make_image(fill_color="black", back_color="white")

            # Base64 ga o'tkazish
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            print(f"QR kod xatoligi: {e}")
            return None

    def get_safe_filename(self, user):
        """Xavfsiz fayl nomi yaratish - ABDUJABBOROV_ASLIDDIN_KOMIL_OGLI formatda"""
        try:
            if hasattr(user, 'abituriyent_profile'):
                profile = user.abituriyent_profile
                name_parts = [
                    profile.last_name or '',
                    profile.first_name or '',
                    profile.other_name or ''
                ]
                full_name = '_'.join(part.strip() for part in name_parts if part.strip())

                # O'zbek harflarini ingliz harflariga o'tkazish
                trans_table = {
                    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                    'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                    'ь': '', 'ы': 'y', 'ъ': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                    'ғ': 'g', 'қ': 'q', 'ҳ': 'h', 'ў': 'o', 'ё': 'yo', 'ъ': '',
                    # Katta harflar
                    'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
                    'Ж': 'J', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
                    'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                    'Ф': 'F', 'Х': 'X', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
                    'Ь': '', 'Ы': 'Y', 'Ъ': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA',
                    'Ғ': 'G', 'Қ': 'Q', 'Ҳ': 'H', 'Ў': 'O', 'Ё': 'YO', 'Ъ': '',
                    # O'zbek harflari
                    'ʻ': '', 'ʼ': '', ''': '', ''': '', '"': '', '"': '',
                    ' ': '_', '-': '_', '.': '_', ',': '_'
                }

                safe_name = ''
                for char in full_name:
                    safe_name += trans_table.get(char, char)

                # Faqat harf, raqam va _ qoldirish
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
                return safe_name.upper() or 'USER'
            else:
                # Telefon raqamidan foydalanish
                phone = user.phone.replace('+', '').replace(' ', '').replace('-', '')
                return f"USER_{phone}"
        except Exception:
            return f"USER_{user.id}"

    def get_replacement_data(self, application, request, contract_type):
        """Ma'lumotlarni olish va haqiqiy QR kod yaratish"""
        # Talaba ismini olish - AbituriyentProfile dan yoki User.full_name dan
        talaba_ismi = "N/A"
        try:
            if hasattr(application.user, 'abituriyent_profile'):
                profile = application.user.abituriyent_profile
                talaba_ismi = f"{profile.last_name} {profile.first_name} {profile.other_name}".strip()
            elif application.user.full_name:
                talaba_ismi = application.user.full_name
            else:
                talaba_ismi = application.user.phone
        except Exception:
            talaba_ismi = application.user.phone

        # Fayl nomini oldindan hisoblash (QR kod uchun)
        safe_name = self.get_safe_filename(application.user)
        filename = f"{safe_name}_{contract_type}.pdf"

        # QR kod uchun to'liq URL
        download_url = request.build_absolute_uri(
            f"/media/contracts/{datetime.now().year}/{datetime.now().month:02d}/{filename}")

        # Haqiqiy QR kod yaratish
        qr_code_data = self.generate_qr_code(download_url)

        return {
            'ID': application.id,
            'KONTRAKT_SUMMASI': application.program.tuition_fee,
            'TALABA_MANZILI': application.user.abituriyent_profile.get_full_address,
            'PASSPORT_SERIYA': application.user.abituriyent_profile.passport_series,
            'OQUV_KURSI': application.user.transfer_diplom.target_course if application.admission_type == AdmissionType.TRANSFER else "1-kurs",
            'OQISH_MUDDATI': application.program.study_duration,

            'TALABA_ISMI': talaba_ismi,
            'TELEFON': application.user.phone,
            'FILIAL': application.branch.name,
            'YONALISH': application.program.name,
            'TALIM_DARAJASI': application.education_level.name,
            'TALIM_SHAKLI': application.education_form.name,
            'QABUL_TURI': application.get_admission_type_display(),
            'SANA': datetime.now().strftime('%d.%m.%Y'),
            'QR_CODE_DATA': qr_code_data,  # Base64 encoded QR kod
            'DOWNLOAD_URL': download_url,
        }

    def generate_contract_view(self, request, application_id, contract_type):
        """Template dan shartnoma yaratish"""
        application = get_object_or_404(Application, id=application_id)

        try:
            # Template faylni yuklash
            template_name = f'contracts/{contract_type}.html'
            template = get_template(template_name)

            # Ma'lumotlarni almashtirish (haqiqiy QR kod bilan)
            context = self.get_replacement_data(application, request, contract_type)
            html_content = template.render(context)

            # Fayl nomini yaratish
            safe_name = self.get_safe_filename(application.user)
            filename = f"{safe_name}_{contract_type}.pdf"

            # WeasyPrint bilan PDF yaratish
            temp_dir = tempfile.mkdtemp()
            temp_pdf_path = os.path.join(temp_dir, 'contract.pdf')

            try:
                HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(temp_pdf_path)

                # PDF fayl mavjudligini tekshirish
                if os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as pdf_file:
                        pdf_content = pdf_file.read()

                    # To'g'ri fayl yo'li bilan saqlash
                    year = datetime.now().year
                    month = f"{datetime.now().month:02d}"
                    relative_path = f"contracts/{year}/{month}/{filename}"

                    application.contract_file.save(relative_path, ContentFile(pdf_content), save=False)
                    success_message = f"✅ {contract_type.replace('_', ' ').title()} PDF shartnoma yaratildi: {filename}"
                else:
                    raise Exception("PDF fayl yaratilmadi")

            except Exception as pdf_error:
                # PDF yaratilmasa, HTML saqlaymiz
                print(f"PDF error: {pdf_error}")
                html_filename = f"{safe_name}_{contract_type}.html"
                application.contract_file.save(html_filename, ContentFile(html_content.encode('utf-8')), save=False)
                success_message = f"⚠️ {contract_type.replace('_', ' ').title()} HTML shartnoma yaratildi (PDF yaratilmadi): {html_filename}"

            # Temporary fayllarni o'chirish
            try:
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                os.rmdir(temp_dir)
            except:
                pass

            # Shartnoma muvaffaqiyatli yaratilgandan keyin statusni "qabul qilindi" ga o'zgartirish
            application.status = ApplicationStatus.ACCEPTED
            application.reviewed_by = request.user
            application.save(update_fields=['contract_file', 'status', 'reviewed_by'])
            messages.success(request, success_message)

        except TemplateDoesNotExist:
            messages.error(request, f"❌ Template topilmadi: {template_name}")
        except Exception as e:
            messages.error(request, f"❌ Xatolik: {str(e)}")

        return HttpResponseRedirect(reverse('admin:applications_application_change', args=[application.id]))

    def generate_ikki_tomonlama_bulk(self, request, queryset):
        """Ikki tomonlama shartnoma yaratish"""
        success_count = 0
        error_count = 0

        for application in queryset:
            try:
                contract_type = 'ikki_tomonlama'

                # Template va context tayyorlash
                template_name = f'contracts/{contract_type}.html'
                template = get_template(template_name)
                context = self.get_replacement_data(application, request, contract_type)
                html_content = template.render(context)

                # Fayl nomi
                safe_name = self.get_safe_filename(application.user)
                filename = f"{safe_name}_{contract_type}.pdf"

                # PDF yaratish
                temp_dir = tempfile.mkdtemp()
                temp_pdf_path = os.path.join(temp_dir, 'contract.pdf')

                HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(temp_pdf_path)

                with open(temp_pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()

                # Saqlash
                year = datetime.now().year
                month = f"{datetime.now().month:02d}"
                relative_path = f"contracts/{year}/{month}/{filename}"

                application.contract_file.save(relative_path, ContentFile(pdf_content), save=False)

                # Shartnoma muvaffaqiyatli yaratilgandan keyin statusni "qabul qilindi" ga o'zgartirish
                application.status = ApplicationStatus.ACCEPTED
                application.reviewed_by = request.user
                application.save(update_fields=['contract_file', 'status', 'reviewed_by'])

                success_count += 1

                # Cleanup
                os.remove(temp_pdf_path)
                os.rmdir(temp_dir)

            except Exception as e:
                error_count += 1
                print(f"Error generating ikki tomonlama contract for {application.id}: {e}")

        self.message_user(
            request,
            f"✅ {success_count} ta ikki tomonlama shartnoma yaratildi va holati 'qabul qilindi' ga o'zgartirildi. ❌ {error_count} ta xatolik.",
            messages.SUCCESS if success_count > 0 else messages.ERROR
        )

    generate_ikki_tomonlama_bulk.short_description = "📝 Ikki tomonlama shartnoma yaratish"

    def generate_uch_tomonlama_bulk(self, request, queryset):
        """Uch tomonlama shartnoma yaratish"""
        success_count = 0
        error_count = 0

        for application in queryset:
            try:
                contract_type = 'uch_tomonlama'

                # Template va context tayyorlash
                template_name = f'contracts/{contract_type}.html'
                template = get_template(template_name)
                context = self.get_replacement_data(application, request, contract_type)
                html_content = template.render(context)

                # Fayl nomi
                safe_name = self.get_safe_filename(application.user)
                filename = f"{safe_name}_{contract_type}.pdf"

                # PDF yaratish
                temp_dir = tempfile.mkdtemp()
                temp_pdf_path = os.path.join(temp_dir, 'contract.pdf')

                HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(temp_pdf_path)

                with open(temp_pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()

                # Saqlash
                year = datetime.now().year
                month = f"{datetime.now().month:02d}"
                relative_path = f"contracts/{year}/{month}/{filename}"

                application.contract_file.save(relative_path, ContentFile(pdf_content), save=False)

                # Shartnoma muvaffaqiyatli yaratilgandan keyin statusni "qabul qilindi" ga o'zgartirish
                application.status = ApplicationStatus.ACCEPTED
                application.reviewed_by = request.user
                application.save(update_fields=['contract_file', 'status', 'reviewed_by'])

                success_count += 1

                # Cleanup
                os.remove(temp_pdf_path)
                os.rmdir(temp_dir)

            except Exception as e:
                error_count += 1
                print(f"Error generating uch tomonlama contract for {application.id}: {e}")

        self.message_user(
            request,
            f"✅ {success_count} ta uch tomonlama shartnoma yaratildi va holati 'qabul qilindi' ga o'zgartirildi. ❌ {error_count} ta xatolik.",
            messages.SUCCESS if success_count > 0 else messages.ERROR
        )

    generate_uch_tomonlama_bulk.short_description = "👨‍👩‍👧 Uch tomonlama shartnoma yaratish"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generate_contract'] = True
        return super().change_view(request, object_id, form_url, extra_context)