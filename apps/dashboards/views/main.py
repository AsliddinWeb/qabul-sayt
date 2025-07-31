# apps/dashboard/views/main.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def main_dashboard(request):
    """Asosiy dashboard - role bo'yicha yo'naltirish"""
    user = request.user

    # Role-based routing
    if user.is_abituriyent:
        return redirect('dashboard:abituriyent')
    elif user.is_admin_role or user.is_mini_admin or user.is_operator or user.is_marketing:
        return redirect('admin:index')
    else:
        # Default: abituriyent dashboard
        return redirect('dashboard:abituriyent')