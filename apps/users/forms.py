# apps/users/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import User


class PhoneForm(forms.Form):
    """Telefon raqam formasi"""
    phone = forms.CharField(
        max_length=17,  # +998 90 123 45 67 format uchun
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

        # Bo'sh joylar va boshqa belgilarni olib tashlash
        phone = ''.join(filter(lambda x: x.isdigit() or x == '+', phone))

        # Bo'sh bo'lsa xato
        if not phone:
            raise ValidationError("Telefon raqam kiritilmagan")

        # + belgisi bo'lmasa qo'shish
        if not phone.startswith('+'):
            phone = '+' + phone

        # 998 bilan boshlanmasa qo'shish
        if not phone.startswith('+998'):
            if phone.startswith('+'):
                phone = phone[1:]  # + ni olib tashlash
            if not phone.startswith('998'):
                phone = '998' + phone
            phone = '+' + phone

        # Faqat raqamlar va + belgisi
        if not all(c.isdigit() or c == '+' for c in phone):
            raise ValidationError("Telefon raqam faqat raqamlardan iborat bo'lishi kerak")

        # Uzunligini tekshirish (+998901234567 = 13 ta belgi)
        if len(phone) != 13:
            raise ValidationError("Telefon raqam to'liq emas. Masalan: +998901234567")

        # O'zbek operatorlarini tekshirish
        operator_codes = ['90', '91', '93', '94', '95', '97', '98', '99', '33', '88', '20', '77']
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

        # Bo'sh bo'lsa
        if not code:
            raise ValidationError("SMS kod kiritilmagan")

        # Faqat raqamlar
        if not code.isdigit():
            raise ValidationError("SMS kod faqat raqamlardan iborat bo'lishi kerak")

        # 4 ta raqam
        if len(code) != 4:
            raise ValidationError("SMS kod 4 ta raqamdan iborat bo'lishi kerak")

        return code