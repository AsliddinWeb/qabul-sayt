# apps/dashboard/views/main.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def main_dashboard(request):
    """Asosiy dashboard - role bo'yicha yo'naltirish"""
    user = request.user

    # Role-based routing
    role_urls = {
        'abituriyent': 'dashboard:abituriyent',
        'operator': 'admin:index',
        'marketing': 'admin:index',
        'mini_admin': 'admin:index',
        'admin': 'admin:index'
    }

    target_url = role_urls.get(user.role, 'dashboard:abituriyent')
    return redirect(target_url)