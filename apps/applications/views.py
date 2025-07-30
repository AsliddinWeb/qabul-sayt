from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from .models import Application
from django.contrib.auth import get_user_model

User = get_user_model()

def get_contract_by_phone(request, phone):
    user = get_object_or_404(User, phone=phone)

    try:
        application = user.application
    except Application.DoesNotExist:
        raise Http404("Application topilmadi")

    if not application.contract_file:
        raise Http404("Shartnoma fayli mavjud emas")

    return redirect(application.contract_file.url)
