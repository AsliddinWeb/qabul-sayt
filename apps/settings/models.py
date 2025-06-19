# apps/settings/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField


class ContractTemplate(models.Model):
    """Shartnoma shablonlari"""

    name = models.CharField(
        max_length=200,
        verbose_name=_("Shablon nomi"),
        help_text=_("Masalan: 'Ikki tomonlama shartnoma' yoki 'Uch tomonlama shartnoma'")
    )

    ikki_tomonlama = RichTextField(
        verbose_name=_("Ikki tomonlama shartnoma shabloni"),
        help_text=_(
            "Placeholder lar: {{TALABA_ISMI}}, {{TELEFON}}, {{FILIAL}}, "
            "{{YONALISH}}, {{TALIM_DARAJASI}}, {{TALIM_SHAKLI}}, "
            "{{QABUL_TURI}}, {{SANA}}"
        ),
        blank=True,
        null=True
    )

    uch_tomonlama = RichTextField(
        verbose_name=_("Uch tomonlama shartnoma shabloni"),
        help_text=_(
            "Placeholder lar: {{TALABA_ISMI}}, {{TELEFON}}, {{FILIAL}}, "
            "{{YONALISH}}, {{TALIM_DARAJASI}}, {{TALIM_SHAKLI}}, "
            "{{QABUL_TURI}}, {{SANA}}, {{OTA_ONA_ISMI}}, {{OTA_ONA_TELEFON}}"
        ),
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Faol"),
        help_text=_("Faqat bitta shablon faol bo'lishi mumkin")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan sana"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("O'zgartirilgan sana"))

    class Meta:
        verbose_name = _("Shartnoma shabloni")
        verbose_name_plural = _("Shartnoma shablonlari")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Agar bu shablon faol qilinsa, boshqalarini faolsiz qilish
        if self.is_active:
            ContractTemplate.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {'(Faol)' if self.is_active else ''}"

    @classmethod
    def get_active_template(cls):
        """Faol shablonni olish"""
        return cls.objects.filter(is_active=True).first()

    def get_available_placeholders(self):
        """Mavjud placeholder larni ro'yxati"""
        return [
            '{{TALABA_ISMI}}',
            '{{TELEFON}}',
            '{{FILIAL}}',
            '{{YONALISH}}',
            '{{TALIM_DARAJASI}}',
            '{{TALIM_SHAKLI}}',
            '{{QABUL_TURI}}',
            '{{SANA}}',
            '{{OTA_ONA_ISMI}}',  # Faqat uch tomonlama uchun
            '{{OTA_ONA_TELEFON}}'  # Faqat uch tomonlama uchun
        ]


class ContractSettings(models.Model):
    """Shartnoma sozlamalari"""

    CONTRACT_TYPES = [
        ('ikki_tomonlama', _('Ikki tomonlama')),
        ('uch_tomonlama', _('Uch tomonlama')),
    ]

    default_contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPES,
        default='ikki_tomonlama',
        verbose_name=_("Standart shartnoma turi")
    )

    auto_generate_pdf = models.BooleanField(
        default=True,
        verbose_name=_("Avtomatik PDF yaratish"),
        help_text=_("Agar faol bo'lsa, HTML dan PDF yaratishga harakat qiladi")
    )

    pdf_page_size = models.CharField(
        max_length=10,
        choices=[
            ('A4', 'A4'),
            ('Letter', 'Letter'),
        ],
        default='A4',
        verbose_name=_("PDF sahifa o'lchami")
    )

    company_name = models.CharField(
        max_length=200,
        default="Ta'lim muassasasi",
        verbose_name=_("Muassasa nomi")
    )

    company_address = models.TextField(
        blank=True,
        verbose_name=_("Muassasa manzili")
    )

    director_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Direktor F.I.Sh")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Shartnoma sozlamasi")
        verbose_name_plural = _("Shartnoma sozlamalari")

    def save(self, *args, **kwargs):
        # Faqat bitta sozlama obyekti bo'lishi kerak
        if not self.pk and ContractSettings.objects.exists():
            raise ValueError("Faqat bitta sozlama obyekti yaratish mumkin")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shartnoma sozlamalari - {self.company_name}"

    @classmethod
    def get_settings(cls):
        """Sozlamalarni olish yoki standart yaratish"""
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create()
        return settings