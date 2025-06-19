from django import forms
from django.contrib.auth import get_user_model
from .models import EducationType, InstitutionType, Course, Diplom, TransferDiplom
from apps.regions.models import Country, Region, District

User = get_user_model()


class EducationTypeForm(forms.ModelForm):
    class Meta:
        model = EducationType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Taʼlim turini kiriting"
            })
        }


class InstitutionTypeForm(forms.ModelForm):
    class Meta:
        model = InstitutionType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Muassasa turini kiriting"
            })
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Kurs nomini kiriting"
            })
        }


class DiplomForm(forms.ModelForm):
    class Meta:
        model = Diplom
        fields = [
            'serial_number', 'education_type', 'institution_type',
            'university_name', 'graduation_year', 'region', 'district', 'diploma_file'
        ]
        widgets = {
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Diplom raqamini kiriting"
            }),
            'education_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'institution_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'university_name': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "Muassasaning to'liq nomini kiriting"
            }),
            'graduation_year': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Bitirgan yilni kiriting (masalan: 2022)",
                'maxlength': '4'
            }),
            'region': forms.Select(attrs={
                'class': 'form-control'
            }),
            'district': forms.Select(attrs={
                'class': 'form-control'
            }),
            'diploma_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # District ni region asosida filter qilish
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['district'].queryset = self.instance.region.districts.all()

    def clean_graduation_year(self):
        graduation_year = self.cleaned_data['graduation_year']
        if not graduation_year.isdigit() or len(graduation_year) != 4:
            raise forms.ValidationError("Yil 4 ta raqamdan iborat bo'lishi kerak")

        current_year = 2025  # Joriy yil
        year = int(graduation_year)
        if year < 1950 or year > current_year:
            raise forms.ValidationError(f"Yil 1950 dan {current_year} gacha bo'lishi kerak")

        return graduation_year


class TransferDiplomForm(forms.ModelForm):
    class Meta:
        model = TransferDiplom
        fields = ['country', 'university_name', 'target_course', 'transcript_file']
        widgets = {
            'country': forms.Select(attrs={
                'class': 'form-control'
            }),
            'university_name': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "Universitetning to'liq nomini kiriting"
            }),
            'target_course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'transcript_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png'
            })
        }



# Qo'shimcha: AJAX orqali district yangilash uchun
class RegionDistrictForm(forms.Form):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label="Viloyatni tanlang",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        empty_label="Tumanni tanlang",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id)
            except (ValueError, TypeError):
                pass