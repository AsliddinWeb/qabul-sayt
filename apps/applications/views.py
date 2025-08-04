# apps/applications/views.py - to'liq yangilangan

import os
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, FileResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Application

User = get_user_model()

def find_contract_file(application):
    """
    Contract file ni topish - turli yo'llarni sinab ko'rish
    Model o'zgartirilmasdan ishlaydi
    """
    media_root = settings.MEDIA_ROOT
    
    # Possible file paths in priority order
    possible_paths = []
    
    # 1. Database da qanday saqlangan bo'lsa
    if application.contract_file.name:
        possible_paths.append(
            os.path.join(media_root, application.contract_file.name)
        )
    
    # 2. Nested structure ni to'g'rilash
    if 'contracts/contracts/' in application.contract_file.name:
        corrected_path = application.contract_file.name.replace('contracts/contracts/', 'contracts/')
        possible_paths.append(
            os.path.join(media_root, corrected_path)
        )
    
    # 3. Filename ni extract qilib, to'g'ri yo'lda qidirish
    filename = os.path.basename(application.contract_file.name)
    year = application.created_at.year
    month = f"{application.created_at.month:02d}"
    
    possible_paths.extend([
        # To'g'ri structure
        os.path.join(media_root, 'contracts', str(year), month, filename),
        
        # Nested structure (mavjud holatda)
        os.path.join(media_root, 'contracts', str(year), month, 'contracts', str(year), month, filename),
        
        # Root contracts folder
        os.path.join(media_root, 'contracts', filename),
        
        # Year folder only
        os.path.join(media_root, 'contracts', str(year), filename),
    ])
    
    # Try each possible path
    for file_path in possible_paths:
        if os.path.exists(file_path):
            return file_path
    
    return None

def get_contract_by_phone(request, phone):
    """Phone orqali contract olish - smart file detection bilan"""
    user = get_object_or_404(User, phone=phone)

    try:
        application = user.application
    except Application.DoesNotExist:
        raise Http404("Application topilmadi")

    if not application.contract_file:
        raise Http404("Shartnoma fayli mavjud emas")

    # Smart file path detection
    file_path = find_contract_file(application)
    if not file_path:
        raise Http404("Shartnoma fayli topilmadi")

    return FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f"contract_{application.id}.pdf"
    )

def serve_contract_by_id(request, application_id):
    """Application ID orqali contract serve qilish"""
    application = get_object_or_404(Application, id=application_id)
    
    if not application.contract_file:
        raise Http404("Contract file mavjud emas")
    
    # Smart file path detection
    file_path = find_contract_file(application)
    if not file_path:
        raise Http404("Contract file topilmadi")
    
    return FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f"contract_{application.id}.pdf"
    )