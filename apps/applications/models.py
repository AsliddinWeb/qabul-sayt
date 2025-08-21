from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.programs.models import Branch, EducationForm, Program, EducationLevel
from apps.diploms.models import Diplom, TransferDiplom, Course


class ApplicationStatus(models.TextChoices):
    PENDING = 'topshirildi', _('Ariza topshirildi')
    REVIEW = 'korib_chiqilmoqda', _('Ko\'rib chiqilmoqda')
    ACCEPTED = 'qabul_qilindi', _('Qabul qilindi')
    REJECTED = 'rad_etildi', _('Rad etildi')


class AdmissionType(models.TextChoices):
    REGULAR = 'yangi_qabul', _('1-kurs (Yangi qabul)')
    TRANSFER = 'perevod', _('Perevod (O\'qishni ko\'chirish)')


class Application(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'abituriyent'},
        verbose_name=_("Foydalanuvchi"),
        related_name="application"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
        verbose_name=_("Ko'rib chiquvchi xodim")
    )

    admission_type = models.CharField(
        max_length=20,
        choices=AdmissionType.choices,
        default=AdmissionType.REGULAR,
        verbose_name=_("Qabul turi")
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        verbose_name=_("Filial"),
        related_name="applications"
    )
    education_level = models.ForeignKey(
        EducationLevel,
        on_delete=models.CASCADE,
        verbose_name=_("Taʼlim darajasi"),
        related_name="applications"
    )
    education_form = models.ForeignKey(
        EducationForm,
        on_delete=models.CASCADE,
        verbose_name=_("Taʼlim shakli"),
        related_name="applications"
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        verbose_name=_("Yo'nalish"),
        related_name="applications"
    )

    diplom = models.ForeignKey(
        Diplom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Diplom"),
        related_name="applications"
    )
    transfer_diplom = models.ForeignKey(
        TransferDiplom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Perevod diplomi"),
        related_name="applications"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Kurs"),
        related_name="applications"
    )

    contract_file = models.FileField(
        upload_to='contracts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name=_("Shartnoma fayli")
    )

    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        verbose_name=_("Holati")
    )

    # ✅ Test uchun - Xavfsiz - nullable fieldlar
    test_completed = models.BooleanField(
        null=True, blank=True,  # NULL qiymat ruxsat
        verbose_name="Test topshirdi"
    )
    test_score = models.IntegerField(
        null=True, blank=True,
        verbose_name="Test balli"
    )
    test_passed = models.BooleanField(
        null=True, blank=True,
        verbose_name="Test o'tdi"
    )
    test_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Test sanasi"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan sana"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("O'zgartirilgan sana"))

    class Meta:
        verbose_name = _("Ariza")
        verbose_name_plural = _("Barcha arizalar")
        ordering = ['-created_at']

        constraints = []

    def clean(self):
        super().clean()

        if self.admission_type == AdmissionType.TRANSFER:
            if not self.transfer_diplom:
                raise ValidationError({
                    'transfer_diplom': _('Perevod turi uchun diplom majburiy')
                })
            if not self.course:
                raise ValidationError({
                    'course': _('Perevod turi uchun kurs majburiy')
                })

        elif self.admission_type == AdmissionType.REGULAR:
            if not self.diplom:
                raise ValidationError({
                    'diplom': _('Yangi qabul turi uchun diplom majburiy')
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        user_name = getattr(self.user, 'full_name', None) or self.user.phone
        return f"{user_name} - {self.program.name} ({self.get_admission_type_display()})"

    @property
    def is_pending(self):
        return self.status == ApplicationStatus.PENDING

    @property
    def is_accepted(self):
        return self.status == ApplicationStatus.ACCEPTED

    @property
    def can_be_reviewed(self):
        return self.status in [ApplicationStatus.PENDING, ApplicationStatus.REVIEW]

    def mark_as_reviewed(self, reviewer):
        self.status = ApplicationStatus.REVIEW
        self.reviewed_by = reviewer
        self.save(update_fields=['status', 'reviewed_by', 'updated_at'])

    def accept(self, reviewer):
        self.status = ApplicationStatus.ACCEPTED
        self.reviewed_by = reviewer
        self.save(update_fields=['status', 'reviewed_by', 'updated_at'])

    def reject(self, reviewer):
        self.status = ApplicationStatus.REJECTED
        self.reviewed_by = reviewer
        self.save(update_fields=['status', 'reviewed_by', 'updated_at'])

    @classmethod
    def get_optimized_queryset(cls):
        return cls.objects.select_related(
            'user', 'branch', 'education_level',
            'education_form', 'program', 'reviewed_by',
            'diplom', 'transfer_diplom', 'course'
        )

    @classmethod
    def get_pending_applications(cls):
        return cls.get_optimized_queryset().filter(status=ApplicationStatus.PENDING)

    @classmethod
    def get_user_application(cls, user):
        return cls.get_optimized_queryset().filter(user=user).first()


class ApplicationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related(
            'user', 'branch', 'education_level',
            'education_form', 'program'
        )

    def pending(self):
        return self.filter(status=ApplicationStatus.PENDING)

    def accepted(self):
        return self.filter(status=ApplicationStatus.ACCEPTED)

    def for_branch(self, branch):
        return self.filter(branch=branch)