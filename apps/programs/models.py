from django.db import models


class Branch(models.Model):
    """University branches like: Tashkent, Andijan, Nukus"""
    name = models.CharField(
        max_length=100,
        verbose_name="Filial nomi",
        help_text="Universitet filiali nomini kiriting (masalan: Toshkent, Andijon, Nukus)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"


class EducationLevel(models.Model):
    """Education level: Bachelor, Master, etc."""
    name = models.CharField(
        max_length=100,
        verbose_name="Taʼlim darajasi",
        help_text="Taʼlim darajasini kiriting (masalan: Bakalavr, Magistr)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taʼlim darajasi"
        verbose_name_plural = "Taʼlim darajalari"


class EducationForm(models.Model):
    """Education form: Full-time, Part-time, Evening"""
    name = models.CharField(
        max_length=100,
        verbose_name="Taʼlim shakli",
        help_text="Taʼlim shaklini kiriting (masalan: Kunduzgi, Sirtqi, Kechki)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taʼlim shakli"
        verbose_name_plural = "Taʼlim shakllari"


class Program(models.Model):
    """Educational programs: direction, tuition fee, duration, etc."""
    image = models.ImageField(
        upload_to='programs/program/',
        null=True,
        blank=True,
        verbose_name="Yo‘nalish rasmi",
        help_text="Yo‘nalish uchun rasm yuklang (ixtiyoriy)"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Yo‘nalish nomi",
        help_text="Yo‘nalish nomini kiriting (masalan: Dasturiy injiniring, Biologiya)"
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Yo‘nalish kodi",
        help_text="Yo‘nalish kodini kiriting (masalan: 5330200)"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        verbose_name="Filial",
        help_text="Yo‘nalish mavjud bo‘lgan filialni tanlang"
    )
    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.CASCADE,
        verbose_name="Taʼlim darajasi",
        help_text="Yo‘nalish tegishli bo‘lgan taʼlim darajasini tanlang"
    )
    education_form = models.ForeignKey(
        EducationForm,
        on_delete=models.CASCADE,
        verbose_name="Taʼlim shakli",
        help_text="Yo‘nalish tegishli bo‘lgan taʼlim shaklini tanlang"
    )

    tuition_fee = models.CharField(
        max_length=255,
        verbose_name="Kontrakt summasi",
        help_text="Yillik kontrakt summasini kiriting (masalan: 12 000 000 so‘m)"
    )
    study_duration = models.CharField(
        max_length=100,
        verbose_name="O‘qish muddati",
        help_text="O‘qish muddatini kiriting (masalan: 4 yil, 2 yil)"
    )
    contract_series = models.CharField(
        max_length=100,
        verbose_name="Shartnoma seriyasi",
        help_text="Shartnoma seriyasini kiriting (masalan: 2025-BK)"
    )

    def __str__(self):
        return f"{self.name} - ({self.education_form}) - ({self.education_level})"

    class Meta:
        verbose_name = "Yo‘nalish"
        verbose_name_plural = "Yo‘nalishlar"
