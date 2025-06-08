from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

from .managers import UserManager
from apps.regions.models import Region, District


class User(AbstractBaseUser, PermissionsMixin):
    """Asosiy foydalanuvchi modeli"""

    ROLE_CHOICES = (
        ('abituriyent', 'Abituriyent'),
        ('operator', 'Operator'),
        ('marketing', 'Marketing'),
        ('mini_admin', 'Mini Admin'),
        ('admin', 'Admin'),
    )

    # Asosiy ma'lumotlar
    phone_validator = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak"
    )
    phone = models.CharField(
        "Telefon raqami",
        max_length=13,
        unique=True,
        validators=[phone_validator],
        help_text="Masalan: +998901234567"
    )

    full_name = models.CharField(
        "To'liq ismi",
        max_length=255,
        blank=True,
        null=True,
        help_text="Foydalanuvchining to'liq ismi"
    )

    # Tasdiqlash va holat
    is_verified = models.BooleanField(
        "SMS kod orqali tasdiqlanganmi?",
        default=False,
        help_text="Telefon raqami SMS kod orqali tasdiqlangan"
    )

    # Rol va huquqlar
    role = models.CharField(
        "Foydalanuvchi roli",
        max_length=20,
        choices=ROLE_CHOICES,
        default='abituriyent',
        help_text="Tizimda foydalanuvchi roli"
    )

    # Tizim holatlari
    is_active = models.BooleanField(
        "Faol holat",
        default=True,
        help_text="Foydalanuvchi faol holatda"
    )

    is_staff = models.BooleanField(
        "Xodim",
        default=False,
        help_text="Admin panelga kirish huquqi"
    )

    # Vaqt belgilari
    date_joined = models.DateTimeField(
        "Ro'yxatdan o'tgan vaqti",
        auto_now_add=True,
        help_text="Foydalanuvchi ro'yxatdan o'tgan vaqt"
    )

    last_login_attempt = models.DateTimeField(
        "Oxirgi kirish urinishi",
        blank=True,
        null=True,
        help_text="Oxirgi marta tizimga kirish urinishi"
    )

    failed_login_attempts = models.PositiveIntegerField(
        "Muvaffaqiyatsiz kirish urinishlari",
        default=0,
        help_text="Ketma-ket muvaffaqiyatsiz kirish urinishlari soni"
    )

    is_blocked = models.BooleanField(
        "Bloklangan",
        default=False,
        help_text="Foydalanuvchi vaqtincha bloklangan"
    )

    blocked_until = models.DateTimeField(
        "Blok tugash vaqti",
        blank=True,
        null=True,
        help_text="Blok tugash vaqti"
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['date_joined']),
        ]

    def __str__(self):
        return f"{self.full_name or self.phone} | ({self.get_role_display()})"

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # Rol tekshirish property'lari
    @property
    def is_marketing(self):
        """Marketing xodimi ekanligini tekshirish"""
        return self.role == 'marketing'

    @property
    def is_operator(self):
        """Operator ekanligini tekshirish"""
        return self.role == 'operator'

    @property
    def is_abituriyent(self):
        """Abituriyent ekanligini tekshirish"""
        return self.role == 'abituriyent'

    @property
    def is_mini_admin(self):
        """Mini admin ekanligini tekshirish"""
        return self.role == 'mini_admin'

    @property
    def is_admin_role(self):
        """Admin ekanligini tekshirish"""
        return self.role == 'admin'

    @property
    def is_management(self):
        """Boshqaruv lavozimida ekanligini tekshirish"""
        return self.role in ['admin', 'mini_admin']

    # Xavfsizlik metodlari
    def is_account_blocked(self):
        """Hisob bloklangan holatda ekanligini tekshirish"""
        if not self.is_blocked:
            return False
        if self.blocked_until and timezone.now() > self.blocked_until:
            self.is_blocked = False
            self.blocked_until = None
            self.failed_login_attempts = 0
            self.save(update_fields=['is_blocked', 'blocked_until', 'failed_login_attempts'])
            return False
        return True

    def block_account(self, minutes=30):
        """Hisobni vaqtincha bloklash"""
        self.is_blocked = True
        self.blocked_until = timezone.now() + timedelta(minutes=minutes)
        self.save(update_fields=['is_blocked', 'blocked_until'])

    def reset_failed_attempts(self):
        """Muvaffaqiyatsiz urinishlar hisobini tiklash"""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])


class BaseProfile(models.Model):
    """Profil modellari uchun asosiy klass"""

    created_at = models.DateTimeField(
        "Yaratilgan vaqti",
        auto_now_add=True,
        help_text="Profil yaratilgan vaqt"
    )

    updated_at = models.DateTimeField(
        "Yangilangan vaqti",
        auto_now=True,
        help_text="Profil oxirgi yangilangan vaqt"
    )

    class Meta:
        abstract = True


class MarketingProfile(BaseProfile):
    """Marketing xodimi profili"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='marketing_profile',
        limit_choices_to={'role': 'marketing'},
        verbose_name="Foydalanuvchi"
    )

    department = models.CharField(
        "Bo'lim",
        max_length=100,
        blank=True,
        null=True,
        help_text="Shartnoma bo'limi"
    )

    class Meta:
        verbose_name = "Marketing xodimi profili"
        verbose_name_plural = "Marketing xodimlari profillari"


class OperatorProfile(BaseProfile):
    """Operator profili"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='operator_profile',
        limit_choices_to={'role': 'operator'},
        verbose_name="Foydalanuvchi"
    )

    shift = models.CharField(
        "Ish smenasi",
        max_length=50,
        blank=True,
        null=True,
        help_text="Operator ish smenasi"
    )

    handled_applications = models.PositiveIntegerField(
        "Ko'rib chiqilgan arizalar soni",
        default=0,
        help_text="Operator tomonidan ko'rib chiqilgan arizalar soni"
    )

    class Meta:
        verbose_name = "Operator profili"
        verbose_name_plural = "Operatorlar profillari"


class MiniAdminProfile(BaseProfile):
    """Mini admin profili"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mini_admin_profile',
        limit_choices_to={'role': 'mini_admin'},
        verbose_name="Foydalanuvchi"
    )

    class Meta:
        verbose_name = "Mini Admin profili"
        verbose_name_plural = "Mini Adminlar profillari"


class AdminProfile(BaseProfile):
    """Admin profili"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        limit_choices_to={'role': 'admin'},
        verbose_name="Foydalanuvchi"
    )

    access_level = models.CharField(
        "Kirish darajasi",
        max_length=20,
        choices=[
            ('super', 'Super Admin'),
            ('system', 'Tizim Admin'),
            ('regional', 'Hududiy Admin'),
        ],
        default='regional',
        help_text="Admin kirish huquqlari darajasi"
    )

    can_modify_users = models.BooleanField(
        "Foydalanuvchilarni o'zgartirish huquqi",
        default=True,
        help_text="Boshqa foydalanuvchilarni o'zgartirish huquqi"
    )

    can_access_reports = models.BooleanField(
        "Hisobotlarga kirish huquqi",
        default=True,
        help_text="Tizim hisobotlariga kirish huquqi"
    )

    class Meta:
        verbose_name = "Admin profili"
        verbose_name_plural = "Adminlar profillari"


class AbituriyentProfile(BaseProfile):
    """Abituriyent profili"""

    GENDER_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='abituriyent_profile',
        limit_choices_to={'role': 'abituriyent'},
        verbose_name="Foydalanuvchi"
    )

    # Shaxsiy ma'lumotlar
    last_name = models.CharField(
        "Familiya",
        max_length=100,
        help_text="Abituriyent familiyasi"
    )

    first_name = models.CharField(
        "Ism",
        max_length=100,
        help_text="Abituriyent ismi"
    )

    other_name = models.CharField(
        "Otasining ismi",
        max_length=100,
        help_text="Abituriyent otasining ismi"
    )

    birth_date = models.DateField(
        "Tug'ilgan sana",
        help_text="Abituriyent tug'ilgan sanasi"
    )

    # Hujjat ma'lumotlari
    passport_series = models.CharField(
        "Pasport seriyasi va raqami",
        max_length=9,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z]{2}\d{7}$',
            message="Pasport seriyasi XX1234567 formatida bo'lishi kerak"
        )],
        help_text="Masalan: AA1234567"
    )

    pinfl = models.CharField(
        "JShShIR (PINFL)",
        max_length=14,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\d{14}$',
            message="PINFL 14 ta raqamdan iborat bo'lishi kerak"
        )],
        help_text="14 raqamdan iborat PINFL kodi"
    )

    # Manzil ma'lumotlari
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Viloyat",
        help_text="Abituriyent yashash viloyati"
    )

    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tuman",
        help_text="Abituriyent yashash tumani"
    )

    address = models.TextField(
        "Yashash manzili",
        blank=True,
        null=True,
        help_text="To'liq yashash manzili"
    )

    # Qo'shimcha ma'lumotlar
    gender = models.CharField(
        "Jinsi",
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Abituriyent jinsi"
    )

    nationality = models.CharField(
        "Millati",
        max_length=50,
        default="O'zbek",
        help_text="Abituriyent millati"
    )

    # Fayllar
    image = models.ImageField(
        "3x4 rasm",
        upload_to='users/abituriyents/images/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="3x4 o'lchamdagi rasm (JPG, PNG)"
    )

    passport_file = models.FileField(
        "Pasport nusxasi",
        upload_to='users/abituriyents/passports/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Pasport nusxasi (PDF, JPG, PNG)"
    )


    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.other_name}".strip()

    def get_full_name(self):
        """To'liq ismni qaytarish"""
        return f"{self.last_name} {self.first_name} {self.other_name}".strip()

    def get_age(self):
        """Yoshni hisoblash"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def check_profile_completion(self):
        """Profilning to'liqligini tekshirish"""
        required_fields = [
            self.last_name, self.first_name, self.other_name,
            self.birth_date, self.passport_series, self.pinfl,
            self.gender, self.region, self.district, self.address
        ]

        files_required = [self.image, self.passport_file]

        all_filled = all(field for field in required_fields)
        all_files = all(file for file in files_required)

        self.is_profile_complete = all_filled and all_files
        return self.is_profile_complete

    def save(self, *args, **kwargs):
        self.check_profile_completion()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Abituriyent profili'
        verbose_name_plural = 'Abituriyentlar profillari'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['passport_series']),
            models.Index(fields=['pinfl']),
            models.Index(fields=['region', 'district']),
        ]


class PhoneVerification(models.Model):
    """Telefon raqamini tasdiqlash modeli"""

    phone_validator = RegexValidator(
        regex=r'^\+998\d{9}$',
        message="Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak"
    )

    phone = models.CharField(
        "Telefon raqami",
        max_length=13,
        validators=[phone_validator],
        help_text="Tasdiqlash kodi yuborilgan telefon raqami"
    )

    code = models.CharField(
        "Tasdiqlash kodi",
        max_length=4,
        validators=[RegexValidator(
            regex=r'^\d{6}$',
            message="Tasdiqlash kodi 4 ta raqamdan iborat bo'lishi kerak"
        )],
        help_text="4 raqamli tasdiqlash kodi"
    )

    created_at = models.DateTimeField(
        "Yaratilgan vaqti",
        auto_now_add=True,
        help_text="Tasdiqlash kodi yaratilgan vaqt"
    )

    is_used = models.BooleanField(
        "Ishlatilgan",
        default=False,
        help_text="Tasdiqlash kodi ishlatilgan"
    )

    attempts = models.PositiveIntegerField(
        "Urinishlar soni",
        default=0,
        help_text="Noto'g'ri kiritish urinishlari soni"
    )

    def is_expired(self):
        """Kodning muddati tugaganligini tekshirish"""
        return timezone.now() > self.created_at + timedelta(minutes=5)  # 5 daqiqa

    def is_valid(self):
        """Kodning haqiqiyligini tekshirish"""
        return not self.is_expired() and not self.is_used and self.attempts < 3

    @classmethod
    def can_send_code(cls, phone):
        """SMS yuborish mumkinligini tekshirish"""
        from django.utils import timezone
        from datetime import timedelta

        # Oxirgi 1 daqiqada yuborilgan kodlar soni
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_codes = cls.objects.filter(
            phone=phone,
            created_at__gte=one_minute_ago
        ).count()

        # 1 daqiqada 3 tadan ko'p yuborish mumkin emas
        if recent_codes >= 3:
            return False, "Juda ko'p urinish! 1 daqiqa kutib turing."

        # Oxirgi aktiv kod bormi tekshirish
        last_active_code = cls.objects.filter(
            phone=phone,
            is_used=False,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()

        # Agar oxirgi kod 30 soniyadan kam vaqt oldin yuborilgan bo'lsa
        if last_active_code:
            time_passed = timezone.now() - last_active_code.created_at
            if time_passed.total_seconds() < 30:
                wait_time = 30 - int(time_passed.total_seconds())
                return False, f"Kod allaqachon yuborilgan, {wait_time} soniya kutib turing."

        return True, "OK"

    @classmethod
    def verify_code(cls, phone, code):
        """Kodni tasdiqlash"""
        try:
            verification = cls.objects.filter(
                phone=phone,
                code=code,
                is_used=False
            ).order_by('-created_at').first()

            if not verification:
                return False, "Noto'g'ri kod"

            if verification.is_expired():
                return False, "Kod muddati tugagan"

            if verification.attempts >= 3:
                return False, "Juda ko'p urinish"

            verification.is_used = True
            verification.save()
            return True, "Kod tasdiqlandi"

        except Exception as e:
            return False, f"Xatolik yuz berdi: {str(e)}"

    class Meta:
        verbose_name = "Telefon tasdiqlash"
        verbose_name_plural = "Telefon tasdiqlash kodlari"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone', 'created_at']),
            models.Index(fields=['code', 'is_used']),
        ]

    def __str__(self):
        return f"{self.phone} - {self.code} ({'Ishlatilgan' if self.is_used else 'Faol'})"
