# apps/users/utils.py

import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_eskiz_client():
    """
    Eskiz clientini yaratish
    """
    from eskiz.client.sync import ClientSync

    return ClientSync(
        email=settings.ESKIZ_EMAIL,
        password=settings.ESKIZ_PASSWORD
    )


def send_sms(phone, message):
    """
    Bitta SMS yuborish
    """
    if hasattr(settings, 'ESKIZ_EMAIL') and hasattr(settings, 'ESKIZ_PASSWORD'):
        try:
            client = get_eskiz_client()
            phone_number = int(phone.replace('+', ''))  # + belgisiz
            resp = client.send_sms(phone_number=phone_number, message=message)

            if resp.status == 'waiting' or resp.status == 'delivered':
                logger.info(f"SMS sent: {resp}")
                return True
            else:
                logger.error(f"Failed to send SMS: {resp}")
                return False

        except Exception as e:
            logger.error(f"Eskiz SMS error: {str(e)}")
            return False

    else:
        logger.info(f"[DEV MODE] SMS to {phone}: {message}")
        print(f"\n{'=' * 50}")
        print("SMS YUBORILDI (DEV MODE)")
        print(f"Raqam: {phone}")
        print(f"Xabar: {message}")
        print(f"{'=' * 50}\n")
        return True


def send_batch_sms(phone_numbers, message):
    """
    Bir nechta raqamlarga SMS yuborish
    """
    if hasattr(settings, 'ESKIZ_EMAIL') and hasattr(settings, 'ESKIZ_PASSWORD'):
        try:
            client = get_eskiz_client()
            messages = []

            for idx, phone in enumerate(phone_numbers):
                phone_number = int(phone.replace('+', ''))
                messages.append({
                    "user_sms_id": f"msg{idx}",
                    "to": phone_number,
                    "text": message
                })

            dispatch_id = str(int(time.time()))
            resp = client.send_batch_sms(messages=messages, dispatch_id=dispatch_id)

            logger.info(f"Batch SMS response: {resp}")
            return True

        except Exception as e:
            logger.error(f"Eskiz batch SMS error: {str(e)}")
            return False
    else:
        for phone in phone_numbers:
            send_sms(phone, message)
        return True


def check_sms_status(sms_id):
    """
    SMS holatini tekshirish (eskiz rasmiy API orqali emas, placeholder)
    """
    logger.warning("Eskiz rasmiy API status tekshiruvini hozircha qo'llab-quvvatlamaydi.")
    return {"status": "unknown", "message": "Eskiz client bu funksiyani qo'llab-quvvatlamaydi."}


def get_sms_balance():
    """
    SMS balansini olish
    """
    if hasattr(settings, 'ESKIZ_EMAIL') and hasattr(settings, 'ESKIZ_PASSWORD'):
        try:
            client = get_eskiz_client()
            balance = client.get_balance()
            logger.info(f"Current balance: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Balance error: {str(e)}")
            return None
    else:
        return 999999  # Dev mode


def format_phone_number(phone):
    """
    Telefon raqamni formatlash
    """
    if not phone or len(phone) < 13:
        return phone
    return f"{phone[:4]} {phone[4:6]} {phone[6:9]} {phone[9:11]} {phone[11:13]}"


def validate_uzbek_phone(phone):
    """
    O'zbekiston raqamini tekshirish
    """
    if not phone.startswith('+998') or len(phone) != 13:
        return False
    operator_codes = ['90', '91', '93', '94', '95', '97', '98', '99', '33', '88', '20', '77']
    return phone[4:6] in operator_codes


def send_verification_code(phone, code):
    """
    Tasdiqlash kodi yuborish
    """
    message = f"Xalqaro innovatsion universiteti qabul tizimiga kirish kodingiz: {code}"
    return send_sms(phone, message)


def send_notification_sms(phone, notification_type, **kwargs):
    """
    SMS bildirishnomalar shablonlari
    """
    templates = {
        'welcome': "Xush kelibsiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.",
        'password_reset': "Parolni tiklash kodi: {code}",
        'login_alert': "Hisobingizga kirish amalga oshirildi. Agar bu siz bo'lmasangiz, darhol xabar bering.",
        'profile_updated': "Profilingiz muvaffaqiyatli yangilandi.",
        'application_received': "Arizangiz qabul qilindi. Tez orada aloqaga chiqamiz.",
        'application_approved': "Tabriklaymiz! Arizangiz tasdiqlandi.",
        'application_rejected': "Afsus, arizangiz rad etildi. Batafsil ma'lumot uchun bog'laning.",
    }

    template = templates.get(notification_type, "Sizga xabar yuborildi.")
    message = template.format(**kwargs)
    return send_sms(phone, message)
