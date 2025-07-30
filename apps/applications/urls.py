from django.urls import path
from .views import get_contract_by_phone

urlpatterns = [
    path('get-contract/<str:phone>/', get_contract_by_phone, name='get_contract_by_phone'),
]
