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
        'operator': 'dashboard:operator',
        'marketing': 'dashboard:marketing',
        'mini_admin': 'dashboard:mini_admin',
        'admin': 'dashboard:admin'
    }

    target_url = role_urls.get(user.role, 'dashboard:abituriyent')
    return redirect(target_url)