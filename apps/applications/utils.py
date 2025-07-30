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


def send_success_application(phone, full_name, application_link):
    """
    Bitta SMS yuborish
    """
    if hasattr(settings, 'ESKIZ_EMAIL') and hasattr(settings, 'ESKIZ_PASSWORD'):
        try:
            client = get_eskiz_client()
            phone_number = int(phone.replace('+', ''))  # + belgisiz
            resp = client.send_sms(phone_number=phone_number,
                                   message=f"🎉 Yaxshi yangilik, hurmatli {full_name}!\n\n"
                                           f"Siz Xalqaro innovatsion universitetiga kontrakt asosida tavsiya etildingiz.\n\n"
                                           f"Shartnomangizni quyidagi havola orqali yuklab olishingiz mumkin: {application_link}\n\n"
                                           f"Katta imkoniyatlar sizni kutmoqda!"
                                   )

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
        logger.info(f"[DEV MODE] SMS to {phone}: {full_name}")
        print(f"\n{'=' * 50}")
        print("SMS YUBORILDI (DEV MODE)")
        print(f"Raqam: {phone}")
        print(f"Xabar: {full_name}")
        print(f"{'=' * 50}\n")
        return True
