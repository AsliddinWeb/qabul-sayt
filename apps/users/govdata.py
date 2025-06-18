# apps/users/govdata.py

import uuid
import os
import base64
import requests
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PassportDataService:
    """Davlat xizmatlari API orqali passport ma'lumotlarini olish"""

    @staticmethod
    def get_passport_info(passport_series, birth_date):
        """
        Passport ma'lumotlarini olish

        Args:
            passport_series: Passport seriya va raqami (masalan: AA1234567)
            birth_date: Tug'ilgan sana (YYYY-MM-DD formatida)

        Returns:
            dict: Ma'lumotlar yoki xatolik
        """

        # Passport seriyani ajratish
        if not passport_series or len(passport_series) < 9:
            return {
                'success': False,
                'error': 'Passport seriya formati noto\'g\'ri'
            }

        document_series = passport_series[:2]
        document_number = passport_series[2:]

        # Sana formatini o'zgartirish
        try:
            birth_date_formatted = datetime.strptime(birth_date, "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError:
            return {
                'success': False,
                'error': 'Sana formati noto\'g\'ri'
            }

        # API ga so'rov yuborish
        url = getattr(settings, 'PASSPORT_API', None)

        if not url:
            # Test rejimi uchun mock data
            return PassportDataService._get_mock_data(passport_series, birth_date)

        params = {
            "documentSeries": document_series,
            "documentNumber": document_number,
            "pinfl": "",
            "dateOfBirth": birth_date_formatted,
            "INN": "",
            "identityDocumentId": 2
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Ma'lumotlarni parse qilish
                result = {
                    'success': True,
                    'data': {
                        'last_name': data.get('familyname', '').upper(),
                        'first_name': data.get('firstname', '').upper(),
                        'other_name': data.get('lastname', '').upper(),
                        'full_name': data.get('fullname', ''),
                        'birth_date': birth_date,
                        'passport_series': passport_series,
                        'pinfl': data.get('pinfl', ''),
                        'gender': data.get('genderid', ''),
                        'address': PassportDataService._parse_address(data),
                        'nationality': 'O\'zbek',  # Default
                    }
                }

                # Qo'shimcha ma'lumotlar (agar mavjud bo'lsa)
                if 'DocumentTables' in data and data['DocumentTables']:
                    doc_info = data['DocumentTables'][0]
                    result['data']['passport_given_date'] = doc_info.get('dateofissue', '')
                    result['data']['passport_given_by'] = doc_info.get('issuedby', '')

                # Rasmni saqlash (agar mavjud bo'lsa)
                if data.get('base64photo'):
                    photo_path = PassportDataService._save_photo(data['base64photo'], passport_series)
                    if photo_path:
                        result['data']['photo_path'] = photo_path

                return result

            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'API xatosi: {response.status_code}'
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'So\'rov vaqti tugadi. Qaytadan urinib ko\'ring.'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                'success': False,
                'error': 'Tarmoq xatosi. Qaytadan urinib ko\'ring.'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': 'Kutilmagan xatolik yuz berdi.'
            }

    @staticmethod
    def _determine_gender(gender_code):
        """Gender kodni o'zgartirish"""
        if gender_code in ['1', 'M', 'male']:
            return 'erkak'
        elif gender_code in ['2', 'F', 'female']:
            return 'ayol'
        return ''

    @staticmethod
    def _parse_address(data):
        """Manzil ma'lumotlarini parse qilish"""
        if 'LivePlaceTables' in data and data['LivePlaceTables']:
            return data['LivePlaceTables'][0].get('address', '')
        return ''

    @staticmethod
    def _save_photo(base64_photo, passport_series):
        """Base64 rasmni saqlash"""
        try:
            file_name = f"{passport_series}_{uuid.uuid4().hex[:8]}.jpg"
            folder_path = os.path.join(settings.MEDIA_ROOT, "passport_photos")
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, "wb") as f:
                f.write(base64.b64decode(base64_photo))

            return f"passport_photos/{file_name}"
        except Exception as e:
            logger.error(f"Photo save error: {str(e)}")
            return None

    @staticmethod
    def _get_mock_data(passport_series, birth_date):
        """Test uchun mock data"""
        return {
            'success': True,
            'data': {
                'last_name': 'TESTOV',
                'first_name': 'TEST',
                'other_name': 'TESTOVICH',
                'full_name': 'TESTOV TEST TESTOVICH',
                'birth_date': birth_date,
                'passport_series': passport_series,
                'pinfl': '12345678901234',
                'gender': 'erkak',
                'passport_given_date': '2020-01-15',
                'passport_expires_date': '2030-01-15',
                'passport_given_by': 'IIV Toshkent shahar bo\'limi',
                'address': 'Toshkent shahar, Yunusobod tumani',
                'nationality': 'O\'zbek'
            }
        }