# apps/applications/urls.py

from django.urls import path
from .views import get_contract_by_phone, serve_contract_by_id

urlpatterns = [
    # Existing
    path('get-contract/<str:phone>/', get_contract_by_phone, name='get_contract_by_phone'),
    
    # New smart contract serving
    path('contract/<int:application_id>/', serve_contract_by_id, name='serve_contract'),
]