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
from .models import Application, ApplicationStatus


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

    readonly_fields = ['created_at', 'updated_at', 'reviewed_by']
    actions = ['generate_contracts_bulk']

    fieldsets = (
        ('Foydalanuvchi ma\'lumotlari', {
            'fields': ('user', 'admission_type')
        }),
        ('Ta\'lim ma\'lumotlari', {
            'fields': ('branch', 'education_level', 'education_form', 'program')
        }),
        ('Ariza holati', {
            'fields': ('status', 'reviewed_by', 'contract_file')
        }),
    )

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
        colors = {
            'topshirildi': '#ffc107',
            'korib_chiqilmoqda': '#17a2b8',
            'qabul_qilindi': '#28a745',
            'rad_etildi': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )

    status_badge.short_description = 'Holat'

    def contract_actions(self, obj):
        """Shartnoma yaratish tugmalari"""
        if obj.contract_file:
            # Shartnoma allaqachon mavjud
            download_url = f"/media/{obj.contract_file.name}"
            return format_html(
                '<a href="{}" target="_blank" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">📄 Yuklab olish</a>',
                download_url
            )
        else:
            # Yangi shartnoma yaratish
            ikki_url = reverse('admin:applications_application_generate_contract',
                               args=[obj.id, 'ikki_tomonlama'])
            uch_url = reverse('admin:applications_application_generate_contract',
                              args=[obj.id, 'uch_tomonlama'])
            return format_html(
                '<a href="{}" style="background: #007bff; color: white; padding: 3px 8px; text-decoration: none; border-radius: 3px; margin-right: 5px;">📝 Ikki tomonlama</a>'
                '<a href="{}" style="background: #6f42c1; color: white; padding: 3px 8px; text-decoration: none; border-radius: 3px;">👨‍👩‍👧 Uch tomonlama</a>',
                ikki_url, uch_url
            )

    contract_actions.short_description = 'Shartnoma'

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
            application.status = ApplicationStatus.ACCEPTED  # Bu qo'shildi
            application.reviewed_by = request.user
            application.save(update_fields=['contract_file', 'status', 'reviewed_by'])  # 'status' qo'shildi
            messages.success(request, success_message)

        except TemplateDoesNotExist:
            messages.error(request, f"❌ Template topilmadi: {template_name}")
        except Exception as e:
            messages.error(request, f"❌ Xatolik: {str(e)}")

        return HttpResponseRedirect(reverse('admin:applications_application_change', args=[application.id]))

    def generate_contracts_bulk(self, request, queryset):
        """Bir nechta shartnomani avtomatik yaratish"""
        success_count = 0
        error_count = 0

        for application in queryset:
            try:
                # Yoshga qarab shartnoma turini aniqlash
                contract_type = self.determine_contract_type(application)

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
                application.status = ApplicationStatus.ACCEPTED  # Bu qo'shildi
                application.reviewed_by = request.user
                application.save(update_fields=['contract_file', 'status', 'reviewed_by'])  # 'status' qo'shildi

                success_count += 1

                # Cleanup
                os.remove(temp_pdf_path)
                os.rmdir(temp_dir)

            except Exception as e:
                error_count += 1
                print(f"Error generating contract for {application.id}: {e}")

        self.message_user(
            request,
            f"✅ {success_count} ta shartnoma yaratildi va holati 'qabul qilindi' ga o'zgartirildi. ❌ {error_count} ta xatolik.",
            messages.SUCCESS if success_count > 0 else messages.ERROR
        )

    generate_contracts_bulk.short_description = "📄 Tanlangan arizalar uchun shartnoma yaratish"

    def determine_contract_type(self, application):
        """Shartnoma turini aniqlash (yoshga qarab)"""
        try:
            if hasattr(application.user, 'abituriyent_profile'):
                profile = application.user.abituriyent_profile
                age = profile.get_age()  # AbituriyentProfile da get_age() metodi bor
                if age < 18:
                    return 'uch_tomonlama'  # Voyaga yetmagan - ota-ona bilan
                else:
                    return 'ikki_tomonlama'  # Voyaga yetgan - faqat talaba bilan
            else:
                return 'ikki_tomonlama'  # Default
        except Exception:
            return 'ikki_tomonlama'  # Fallback

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_generate_contract'] = True
        return super().change_view(request, object_id, form_url, extra_context)