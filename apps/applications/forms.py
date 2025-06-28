from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Application, AdmissionType, ApplicationStatus
from apps.programs.models import Branch, EducationForm, Program, EducationLevel
from apps.diploms.models import Diplom, TransferDiplom, Course
from django.db import models

User = get_user_model()


class ApplicationForm(forms.ModelForm):
    """Ariza yaratish/tahrirlash formasi"""

    class Meta:
        model = Application
        fields = [
            'admission_type', 'branch', 'education_level',
            'education_form', 'program', 'diplom',
            'transfer_diplom', 'course',
        ]
        widgets = {
            'admission_type': forms.Select(
                attrs={
                    'class': 'form-select',
                    'onchange': 'toggleDiplomFields()'
                }
            ),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'education_form': forms.Select(attrs={'class': 'form-select'}),
            'program': forms.Select(attrs={'class': 'form-select'}),
            'diplom': forms.Select(attrs={'class': 'form-select'}),
            'transfer_diplom': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),

        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Foydalanuvchi uchun mavjud diplomlarni filterlash
        if self.user:
            self.fields['diplom'].queryset = Diplom.objects.filter(user=self.user)
            self.fields['transfer_diplom'].queryset = TransferDiplom.objects.filter(user=self.user)
            
            # Agar foydalanuvchida oddiy diplom bo'lsa, Sirtqi ta'lim shaklini chiqarib tashlash
            if hasattr(self.user, 'diplom') and self.user.diplom:
                # Education form querysetini filterlash - Sirtqi (id=2) ni chiqarib tashlash
                self.fields['education_form'].queryset = EducationForm.objects.exclude(id=2)

        # Admission type ga qarab fieldlarni yashirish/ko'rsatish
        if self.instance and self.instance.pk:
            self._setup_conditional_fields()

    def _setup_conditional_fields(self):
        """Admission type ga qarab maydonlarni sozlash"""
        if self.instance.admission_type == AdmissionType.REGULAR:
            self.fields['transfer_diplom'].widget = forms.HiddenInput()
            self.fields['course'].widget = forms.HiddenInput()
        elif self.instance.admission_type == AdmissionType.TRANSFER:
            self.fields['diplom'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        admission_type = cleaned_data.get('admission_type')
        diplom = cleaned_data.get('diplom')
        transfer_diplom = cleaned_data.get('transfer_diplom')
        course = cleaned_data.get('course')
        education_form = cleaned_data.get('education_form')

        # Oddiy diplom bo'lsa va Sirtqi ta'lim shakli tanlanmagan bo'lishi kerak
        if self.user and hasattr(self.user, 'diplom') and self.user.diplom:
            if education_form and education_form.id == 2:  # Sirtqi ta'lim shakli
                raise ValidationError({
                    'education_form': _('O\'rta maktab diplomi bilan sirtqi ta\'lim shaklini tanlay olmaysiz')
                })

        # Admission type ga mos ravishda validatsiya
        if admission_type == AdmissionType.TRANSFER:
            if not transfer_diplom:
                raise ValidationError({
                    'transfer_diplom': _('Perevod turi uchun diplom majburiy')
                })
            if not course:
                raise ValidationError({
                    'course': _('Perevod turi uchun kurs majburiy')
                })
            # Yangi qabul uchun kerakli maydonlarni tozalash
            cleaned_data['diplom'] = None

        elif admission_type == AdmissionType.REGULAR:
            if not diplom:
                raise ValidationError({
                    'diplom': _('Yangi qabul turi uchun diplom majburiy')
                })
            # Perevod uchun kerakli maydonlarni tozalash
            cleaned_data['transfer_diplom'] = None
            cleaned_data['course'] = None

        return cleaned_data

    def save(self, commit=True):
        application = super().save(commit=False)
        if self.user:
            application.user = self.user
        if commit:
            application.save()
        return application


class ApplicationFilterForm(forms.Form):
    """Arizalarni filterlash formasi (admin uchun)"""

    status = forms.ChoiceField(
        choices=[('', _('Barcha holatlar'))] + ApplicationStatus.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    admission_type = forms.ChoiceField(
        choices=[('', _('Barcha turlar'))] + AdmissionType.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        empty_label=_('Barcha filiallar'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    education_level = forms.ModelChoiceField(
        queryset=EducationLevel.objects.all(),
        empty_label=_('Barcha darajalar'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        empty_label=_('Barcha yo\'nalishlar'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        label=_('Sanadan')
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        label=_('Sanagacha')
    )

    def filter_queryset(self, queryset):
        """QuerySetni filterlash"""
        if self.cleaned_data.get('status'):
            queryset = queryset.filter(status=self.cleaned_data['status'])

        if self.cleaned_data.get('admission_type'):
            queryset = queryset.filter(admission_type=self.cleaned_data['admission_type'])

        if self.cleaned_data.get('branch'):
            queryset = queryset.filter(branch=self.cleaned_data['branch'])

        if self.cleaned_data.get('education_level'):
            queryset = queryset.filter(education_level=self.cleaned_data['education_level'])

        if self.cleaned_data.get('program'):
            queryset = queryset.filter(program=self.cleaned_data['program'])

        if self.cleaned_data.get('date_from'):
            queryset = queryset.filter(created_at__date__gte=self.cleaned_data['date_from'])

        if self.cleaned_data.get('date_to'):
            queryset = queryset.filter(created_at__date__lte=self.cleaned_data['date_to'])

        return queryset


class ApplicationReviewForm(forms.ModelForm):
    """Arizani ko'rib chiqish formasi (admin uchun)"""

    review_comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Izoh yozing...')
            }
        ),
        required=False,
        label=_('Izoh')
    )

    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Faqat review qilish mumkin bo'lgan statuslarni ko'rsatish
        self.fields['status'].choices = [
            (ApplicationStatus.REVIEW, _('Ko\'rib chiqilmoqda')),
            (ApplicationStatus.ACCEPTED, _('Qabul qilindi')),
            (ApplicationStatus.REJECTED, _('Rad etildi')),
        ]


class QuickApplicationForm(forms.ModelForm):
    """Tezkor ariza yaratish formasi"""

    class Meta:
        model = Application
        fields = ['branch', 'program', 'admission_type']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'program': forms.Select(attrs={'class': 'form-select'}),
            'admission_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Eng ko'p ishlatiladigan filial va yo'nalishlarni birinchi o'ringa qo'yish
        popular_branches = Branch.objects.annotate(
            app_count=models.Count('applications')
        ).order_by('-app_count')[:5]

        popular_programs = Program.objects.annotate(
            app_count=models.Count('applications')
        ).order_by('-app_count')[:10]

        self.fields['branch'].queryset = popular_branches
        self.fields['program'].queryset = popular_programs

    def save(self, commit=True):
        application = super().save(commit=False)
        if self.user:
            application.user = self.user
            # Default qiymatlarni o'rnatish
            application.education_level = EducationLevel.objects.first()
            application.education_form = EducationForm.objects.first()

        if commit:
            application.save()
        return application


class BulkApplicationActionForm(forms.Form):
    """Bir nechta arizaga bir vaqtda amal qilish formasi"""

    ACTION_CHOICES = [
        ('accept', _('Barcha tanlangan arizalarni qabul qilish')),
        ('reject', _('Barcha tanlangan arizalarni rad etish')),
        ('mark_review', _('Ko\'rib chiqilmoqda deb belgilash')),
        ('export', _('Eksport qilish')),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    application_ids = forms.CharField(
        widget=forms.HiddenInput()
    )

    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Amalni bajarishni tasdiqlash')
    )