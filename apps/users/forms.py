# apps/users/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import User, AbituriyentProfile
from apps.regions.models import Region, District


class PhoneForm(forms.Form):
    """Telefon raqam formasi"""
    phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 90 123 45 67',
            'id': 'phone',
            'autocomplete': 'tel',
            'inputmode': 'tel',
            'autofocus': True,
        }),
        label="Telefon raqami"
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        phone = ''.join(filter(lambda x: x.isdigit() or x == '+', phone))

        if not phone:
            raise ValidationError("Telefon raqam kiritilmagan")

        if not phone.startswith('+'):
            phone = '+' + phone

        if not phone.startswith('+998'):
            if phone.startswith('+'):
                phone = phone[1:]
            if not phone.startswith('998'):
                phone = '998' + phone
            phone = '+' + phone

        if not all(c.isdigit() or c == '+' for c in phone):
            raise ValidationError("Telefon raqam faqat raqamlardan iborat bo'lishi kerak")

        if len(phone) != 13:
            raise ValidationError("Telefon raqam to'liq emas. Masalan: +998901234567")

        operator_codes = ['90', '91', '93', '94', '95', '97', '98', '99', '33', '88', '20', '77', '50', '55']
        operator_code = phone[4:6]

        if operator_code not in operator_codes:
            raise ValidationError(f"Noto'g'ri operator kodi: {operator_code}")

        return phone


class VerifyCodeForm(forms.Form):
    """SMS kodni tasdiqlash formasi"""
    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '0000',
            'id': 'code-input',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'pattern': '[0-9]{4}',
            'style': 'font-size: 28px; letter-spacing: 15px; font-weight: bold;'
        }),
        label="SMS kod"
    )

    phone = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '')

        if not code:
            raise ValidationError("SMS kod kiritilmagan")

        if not code.isdigit():
            raise ValidationError("SMS kod faqat raqamlardan iborat bo'lishi kerak")

        if len(code) != 4:
            raise ValidationError("SMS kod 4 ta raqamdan iborat bo'lishi kerak")

        return code


class AbituriyentProfileForm(forms.ModelForm):
    """Abituriyent profili uchun forma - qo'lda to'ldirish uchun optimizatsiyalangan"""

    class Meta:
        model = AbituriyentProfile
        fields = [
            'last_name', 'first_name', 'other_name',
            'birth_date', 'passport_series', 'pinfl',
            'gender', 'nationality', 'region', 'district',
            'address', 'image', 'passport_file'
        ]

        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiya',
                'style': 'text-transform: uppercase;'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ism',
                'style': 'text-transform: uppercase;'
            }),
            'other_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Otasining ismi',
                'style': 'text-transform: uppercase;'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'passport_series': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AA1234567',
                'maxlength': '9',
                'style': 'text-transform: uppercase;'
            }),
            'pinfl': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678901234',
                'maxlength': '14',
                'inputmode': 'numeric',
                'pattern': '[0-9]{14}'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'value': "O'zbek"
            }),
            'region': forms.Select(attrs={
                'class': 'form-control'
            }),
            'district': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'To\'liq manzilni kiriting'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png',
                'style': 'display: none;'
            }),
            'passport_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf,image/jpeg,image/jpg,image/png'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Maydon labellarini o'zgartirish
        self.fields['last_name'].label = 'Familiya *'
        self.fields['first_name'].label = 'Ism *'
        self.fields['other_name'].label = 'Otasining ismi *'
        self.fields['birth_date'].label = 'Tug\'ilgan sana *'
        self.fields['passport_series'].label = 'Passport seriya va raqami *'
        self.fields['pinfl'].label = 'PINFL *'
        self.fields['gender'].label = 'Jinsi *'
        self.fields['nationality'].label = 'Millati'
        self.fields['region'].label = 'Viloyat *'
        self.fields['district'].label = 'Tuman *'
        self.fields['address'].label = 'Yashash manzili *'
        self.fields['image'].label = '3x4 rasm'  # * belgisini olib tashladik
        self.fields['passport_file'].label = 'Passport nusxasi'

        # Required maydonlarni belgilash
        required_fields = [
            'last_name', 'first_name', 'other_name', 'birth_date',
            'passport_series', 'pinfl', 'gender', 'region', 'district',
            'address'
        ]
        
        for field_name in required_fields:
            self.fields[field_name].required = True

        # Image va passport_file ixtiyoriy
        self.fields['image'].required = False
        self.fields['passport_file'].required = False

        # Gender choices
        self.fields['gender'].choices = [
            ('', 'Tanlang'),
            ('erkak', 'Erkak'),
            ('ayol', 'Ayol')
        ]

        # Region choices
        self.fields['region'].queryset = Region.objects.order_by('name')
        self.fields['region'].empty_label = "Viloyatni tanlang"

        # District filtrlash
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(
                    region_id=region_id
                ).order_by('name')
                self.fields['district'].empty_label = "Tumanni tanlang"
            except (ValueError, TypeError):
                self.fields['district'].queryset = District.objects.none()
                self.fields['district'].empty_label = "Avval viloyatni tanlang"
        elif self.instance.pk and self.instance.region:
            self.fields['district'].queryset = District.objects.filter(
                region=self.instance.region
            ).order_by('name')
            self.fields['district'].empty_label = "Tumanni tanlang"
        else:
            self.fields['district'].queryset = District.objects.none()
            self.fields['district'].empty_label = "Avval viloyatni tanlang"
            

    def clean_passport_series(self):
        """Passport seriyani tekshirish va formatlash"""
        passport_series = self.cleaned_data.get('passport_series', '').upper().strip()

        if passport_series:
            import re
            if not re.match(r'^[A-Z]{2}\d{7}$', passport_series):
                raise ValidationError('Passport seriya formati noto\'g\'ri. Masalan: AA1234567')

            # Boshqa foydalanuvchida bunday passport seriya bormi tekshirish
            if self.instance.pk:
                existing = AbituriyentProfile.objects.filter(
                    passport_series=passport_series
                ).exclude(pk=self.instance.pk).first()
            else:
                existing = AbituriyentProfile.objects.filter(
                    passport_series=passport_series
                ).first()

            if existing:
                raise ValidationError('Bu passport seriya allaqachon ro\'yxatdan o\'tgan')

        return passport_series

    def clean_pinfl(self):
        """PINFL ni tekshirish"""
        pinfl = self.cleaned_data.get('pinfl', '').strip()

        if pinfl:
            import re
            if not re.match(r'^\d{14}$', pinfl):
                raise ValidationError('PINFL 14 ta raqamdan iborat bo\'lishi kerak')

            # Boshqa foydalanuvchida bunday PINFL bormi tekshirish
            if self.instance.pk:
                existing = AbituriyentProfile.objects.filter(
                    pinfl=pinfl
                ).exclude(pk=self.instance.pk).first()
            else:
                existing = AbituriyentProfile.objects.filter(
                    pinfl=pinfl
                ).first()

            if existing:
                raise ValidationError('Bu PINFL allaqachon ro\'yxatdan o\'tgan')

        return pinfl

    def clean_birth_date(self):
        """Tug'ilgan sanani tekshirish"""
        birth_date = self.cleaned_data.get('birth_date')

        if birth_date:
            from datetime import date
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if age < 16:
                raise ValidationError('Yoshingiz 16 dan kichik bo\'lmasligi kerak')
            if age > 60:
                raise ValidationError('Yoshingiz 60 dan katta bo\'lmasligi kerak')

        return birth_date

    def clean_district(self):
        """District va region mos kelishini tekshirish"""
        district = self.cleaned_data.get('district')
        region = self.cleaned_data.get('region')

        if district and region:
            if district.region != region:
                raise ValidationError('Tanlangan tuman viloyatga mos kelmaydi')

        return district

    def clean_image(self):
        """Rasm faylini tekshirish"""
        image = self.cleaned_data.get('image')

        if image:
            # Fayl hajmini tekshirish (2MB dan katta bo'lmasligi kerak)
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Rasm hajmi 2MB dan katta bo\'lmasligi kerak')

            # Fayl formatini tekshirish
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError('Faqat JPG, JPEG, PNG formatidagi fayllar qabul qilinadi')

        return image

    def clean_passport_file(self):
        """Passport fayl tekshirish"""
        passport_file = self.cleaned_data.get('passport_file')

        if passport_file:
            # Fayl hajmini tekshirish (5MB dan katta bo'lmasligi kerak)
            if passport_file.size > 5 * 1024 * 1024:
                raise ValidationError('Fayl hajmi 5MB dan katta bo\'lmasligi kerak')

            # Fayl formatini tekshirish
            if not passport_file.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                raise ValidationError('Faqat PDF, JPG, JPEG, PNG formatidagi fayllar qabul qilinadi')

        return passport_file

    def clean(self):
        """Form umumiy validatsiyasi"""
        cleaned_data = super().clean()
        
        # Ismlarni katta harfga o'tkazish
        for field_name in ['last_name', 'first_name', 'other_name']:
            if cleaned_data.get(field_name):
                cleaned_data[field_name] = cleaned_data[field_name].upper().strip()
        
        return cleaned_data