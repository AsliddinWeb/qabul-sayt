from django.db import models


class Region(models.Model):
    """Viloyat yoki shaharlar (masalan: Toshkent, Andijon, Qoraqalpog‘iston)"""
    name = models.CharField(max_length=100, verbose_name="Viloyat yoki shahar nomi")

    class Meta:
        unique_together = ('name', )
        verbose_name = "Viloyat yoki shahar"
        verbose_name_plural = "Viloyat va shaharlar"

    def __str__(self):
        return f"{self.name}"


class District(models.Model):
    """Tumanlar yoki shaharchalar, viloyatga bog‘langan"""
    name = models.CharField(max_length=100, verbose_name="Tuman nomi")
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='districts',
        verbose_name="Viloyat yoki shahar"
    )

    class Meta:
        unique_together = ('name', 'region')
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"

    def __str__(self):
        return f"{self.name}, {self.region.name}"
