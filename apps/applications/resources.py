# apps/applications/resources.py

from import_export import resources, fields, widgets
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from django.contrib.auth import get_user_model
from .models import Application
from apps.programs.models import Branch, EducationLevel, EducationForm, Program

User = get_user_model()


class ApplicationResource(resources.ModelResource):
    """Application modeli uchun import/export resource"""

    # Basic fields
    id = fields.Field(attribute='id', column_name='ID')

    # User ma'lumotlari
    user_phone = fields.Field(
        attribute='user__phone',
        column_name='Telefon raqami'
    )

    user_full_name = fields.Field(
        attribute='user__full_name',
        column_name='To\'liq ismi'
    )

    # Abituriyent profili ma'lumotlari
    last_name = fields.Field(
        attribute='user__abituriyent_profile__last_name',
        column_name='Familiya'
    )

    first_name = fields.Field(
        attribute='user__abituriyent_profile__first_name',
        column_name='Ism'
    )

    other_name = fields.Field(
        attribute='user__abituriyent_profile__other_name',
        column_name='Otasining ismi'
    )

    birth_date = fields.Field(
        attribute='user__abituriyent_profile__birth_date',
        column_name='Tug\'ilgan sana',
        widget=widgets.DateWidget(format='%d.%m.%Y')
    )

    passport_series = fields.Field(
        attribute='user__abituriyent_profile__passport_series',
        column_name='Passport seriya'
    )

    pinfl = fields.Field(
        attribute='user__abituriyent_profile__pinfl',
        column_name='PINFL'
    )

    gender = fields.Field(
        attribute='user__abituriyent_profile__gender',
        column_name='Jinsi'
    )

    region = fields.Field(
        attribute='user__abituriyent_profile__region__name',
        column_name='Viloyat'
    )

    district = fields.Field(
        attribute='user__abituriyent_profile__district__name',
        column_name='Tuman'
    )

    address = fields.Field(
        attribute='user__abituriyent_profile__address',
        column_name='Manzil'
    )

    # Application asosiy ma'lumotlari
    admission_type = fields.Field(
        attribute='admission_type',
        column_name='Qabul turi'
    )

    branch = fields.Field(
        attribute='branch__name',  # To'g'ridan-to'g'ri name ni olish
        column_name='Filial'
    )

    education_level = fields.Field(
        attribute='education_level__name',  # To'g'ridan-to'g'ri name ni olish
        column_name='Ta\'lim darajasi'
    )

    education_form = fields.Field(
        attribute='education_form__name',  # To'g'ridan-to'g'ri name ni olish
        column_name='Ta\'lim shakli'
    )

    program = fields.Field(
        attribute='program__name',  # To'g'ridan-to'g'ri name ni olish
        column_name='Yo\'nalish'
    )

    # Diplom ma'lumotlari - xavfsiz field access
    diplom_serial_number = fields.Field(
        column_name='Diplom raqami'
    )

    diplom_university = fields.Field(
        column_name='Diplom universiteti'
    )

    # Transfer diplom ma'lumotlari - xavfsiz field access
    transfer_diplom_university = fields.Field(
        column_name='Transfer universiteti'
    )

    transfer_diplom_country = fields.Field(
        column_name='Transfer davlati'
    )

    target_course = fields.Field(
        column_name='Maqsadli kurs'
    )

    # Ariza holati va vaqt
    status = fields.Field(
        attribute='status',
        column_name='Holati'
    )

    reviewed_by = fields.Field(
        column_name='Ko\'rib chiquvchi'
    )

    has_contract = fields.Field(
        column_name='Shartnoma mavjud'
    )

    created_at = fields.Field(
        attribute='created_at',
        column_name='Yaratilgan sana',
        widget=widgets.DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    updated_at = fields.Field(
        attribute='updated_at',
        column_name='Yangilangan sana',
        widget=widgets.DateTimeWidget(format='%d.%m.%Y %H:%M')
    )

    # Program qo'shimcha ma'lumotlari
    tuition_fee = fields.Field(
        attribute='program__tuition_fee',
        column_name='Kontrakt summasi'
    )

    study_duration = fields.Field(
        attribute='program__study_duration',
        column_name='O\'qish muddati'
    )

    class Meta:
        model = Application
        import_id_fields = ('id',)
        fields = (
            'id', 'user_phone', 'user_full_name',
            'last_name', 'first_name', 'other_name',
            'birth_date', 'passport_series', 'pinfl',
            'gender', 'region', 'district', 'address',
            'admission_type', 'branch', 'education_level',
            'education_form', 'program', 'tuition_fee',
            'study_duration', 'diplom_serial_number',
            'diplom_university', 'transfer_diplom_university',
            'transfer_diplom_country', 'target_course',
            'status', 'reviewed_by', 'has_contract',
            'created_at', 'updated_at'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    # XAVFSIZ DEHYDRATE FUNKSIYALARI
    def dehydrate_diplom_serial_number(self, application):
        """Diplom raqamini xavfsiz olish"""
        try:
            if hasattr(application, 'diplom') and application.diplom:
                return application.diplom.serial_number
            return ''
        except Exception:
            return ''

    def dehydrate_diplom_university(self, application):
        """Diplom universitetini xavfsiz olish"""
        try:
            if hasattr(application, 'diplom') and application.diplom:
                return application.diplom.university_name
            return ''
        except Exception:
            return ''

    def dehydrate_transfer_diplom_university(self, application):
        """Transfer universiteti nomini xavfsiz olish"""
        try:
            if hasattr(application, 'transfer_diplom') and application.transfer_diplom:
                return application.transfer_diplom.university_name
            return ''
        except Exception:
            return ''

    def dehydrate_transfer_diplom_country(self, application):
        """Transfer davlati nomini xavfsiz olish"""
        try:
            if hasattr(application, 'transfer_diplom') and application.transfer_diplom:
                return application.transfer_diplom.country.name
            return ''
        except Exception:
            return ''

    def dehydrate_target_course(self, application):
        """Maqsadli kursni xavfsiz olish"""
        try:
            if hasattr(application, 'course') and application.course:
                return application.course.name
            return ''
        except Exception:
            return ''

    def dehydrate_reviewed_by(self, application):
        """Ko'rib chiquvchi nomini xavfsiz olish"""
        try:
            if application.reviewed_by:
                return application.reviewed_by.get_full_name() or application.reviewed_by.username
            return ''
        except Exception:
            return ''

    def dehydrate_admission_type(self, application):
        """Admission type ni o'zbek tilida export qilish"""
        try:
            return application.get_admission_type_display()
        except Exception:
            return application.admission_type

    def dehydrate_status(self, application):
        """Status ni o'zbek tilida export qilish"""
        try:
            return application.get_status_display()
        except Exception:
            return application.status

    def dehydrate_gender(self, application):
        """Gender ni formatlash"""
        try:
            if hasattr(application.user, 'abituriyent_profile') and application.user.abituriyent_profile:
                gender = application.user.abituriyent_profile.gender
                return 'Erkak' if gender == 'erkak' else 'Ayol' if gender == 'ayol' else gender
            return ''
        except Exception:
            return ''

    def dehydrate_has_contract(self, application):
        """Shartnoma mavjudligini tekshirish"""
        try:
            return 'Ha' if application.contract_file else 'Yo\'q'
        except Exception:
            return 'Yo\'q'

    def export(self, queryset=None, *args, **kwargs):
        """Custom export with optimization"""
        if queryset is None:
            queryset = self.get_queryset()

        # Optimized queryset - faqat mavjud related fieldlarni select qilish
        try:
            queryset = queryset.select_related(
                'user',
                'branch',
                'education_level',
                'education_form',
                'program',
                'reviewed_by'
            ).prefetch_related(
                'user__abituriyent_profile',
                'user__abituriyent_profile__region',
                'user__abituriyent_profile__district'
            )
        except Exception:
            # Agar ba'zi related fieldlar mavjud bo'lmasa, asosiy queryset ni ishlatamiz
            pass

        return super().export(queryset, *args, **kwargs)

    def get_queryset(self):
        """Barcha arizalarni olish"""
        return Application.objects.all()