from django.db import models


class Country(models.Model):
    """Davlatlar (masalan: O‘zbekiston, Qozog‘iston, Rossiya)"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Davlat nomi",
        help_text="Davlat nomini kiriting (masalan: O‘zbekiston, Qozog‘iston)"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Davlat"
        verbose_name_plural = "Davlatlar"


class Region(models.Model):
    """Viloyat yoki shaharlar (masalan: Toshkent, Andijon, Qoraqalpog‘iston)"""
    name = models.CharField(
        max_length=100,
        verbose_name="Viloyat yoki shahar nomi",
        help_text="Viloyat yoki shahar nomini kiriting (masalan: Toshkent)"
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name='regions',
        verbose_name="Davlat",
        help_text="Ushbu viloyat tegishli bo‘lgan davlatni tanlang"
    )

    class Meta:
        unique_together = ('name', 'country')
        verbose_name = "Viloyat yoki shahar"
        verbose_name_plural = "Viloyat va shaharlar"

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class District(models.Model):
    """Tumanlar yoki shaharchalar, viloyatga bog‘langan"""
    name = models.CharField(
        max_length=100,
        verbose_name="Tuman nomi",
        help_text="Tuman yoki shaharcha nomini kiriting (masalan: Olmazor)"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='districts',
        verbose_name="Viloyat yoki shahar",
        help_text="Ushbu tuman tegishli bo‘lgan viloyat yoki shaharni tanlang"
    )

    class Meta:
        unique_together = ('name', 'region')
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"

    def __str__(self):
        return f"{self.name}, {self.region.name}"
