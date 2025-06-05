from django.db import models
from django.conf import settings
from apps.regions.models import Country, Region, District


class EducationType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Taʼlim turi",
        help_text="Taʼlim turini kiriting (masalan: Bakalavr, Magistratura)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Taʼlim turi"
        verbose_name_plural = "Taʼlim turlari"


class InstitutionType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Muassasa turi",
        help_text="Muassasa turini kiriting (masalan: Universitet, Institut)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Muassasa turi"
        verbose_name_plural = "Muassasa turlari"


class Course(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Kurs",
        help_text="Kurs nomini kiriting (masalan: 1-kurs, 2-kurs)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"


class Diplom(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diplom',
        verbose_name="Foydalanuvchi",
        help_text="Diplomga ega foydalanuvchini tanlang"
    )
    serial_number = models.CharField(
        max_length=100,
        verbose_name="Diplom raqami",
        help_text="Diplomning seriya va raqamini kiriting"
    )
    education_type = models.ForeignKey(
        EducationType,
        on_delete=models.CASCADE,
        verbose_name="Taʼlim turi",
        help_text="Diplom tegishli bo‘lgan taʼlim turini tanlang"
    )
    institution_type = models.ForeignKey(
        InstitutionType,
        on_delete=models.CASCADE,
        verbose_name="Muassasa turi",
        help_text="Diplom berilgan muassasa turini tanlang"
    )
    university_name = models.TextField(
        verbose_name="Universitet nomi",
        help_text="Universitetning to‘liq nomini kiriting"
    )
    graduation_year = models.CharField(
        max_length=4,
        verbose_name="Bitirgan yil",
        help_text="Bitirgan yilni 4 xonali raqamda kiriting (masalan: 2022)"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        verbose_name="Viloyat",
        help_text="Universitet joylashgan viloyatni tanlang"
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        verbose_name="Tuman",
        help_text="Universitet joylashgan tumanni tanlang"
    )
    diploma_file = models.FileField(
        upload_to='diploms/',
        verbose_name="Diplom fayli",
        help_text="Diplom faylini yuklang (PDF yoki rasm formatida)"
    )

    def __str__(self):
        return self.serial_number

    class Meta:
        verbose_name = "Diplom"
        verbose_name_plural = "Diplomlar"


class TransferDiplom(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transfer_diplom',
        verbose_name="Foydalanuvchi",
        help_text="Perevod diplomi egasini tanlang"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name="Davlat",
        help_text="Universitet joylashgan davlatni tanlang"
    )
    university_name = models.TextField(
        verbose_name="Universitet nomi",
        help_text="Perevod qilinayotgan universitetning to‘liq nomini kiriting"
    )
    target_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Kurs",
        help_text="Qabul qilinayotgan kursni tanlang"
    )
    transcript_file = models.FileField(
        upload_to='transcripts/',
        verbose_name="Transcript fayli",
        help_text="Transcript faylini yuklang (PDF yoki rasm formatida)"
    )

    def __str__(self):
        return self.university_name

    class Meta:
        verbose_name = "Perevod diplomi"
        verbose_name_plural = "Perevod diplomlari"
