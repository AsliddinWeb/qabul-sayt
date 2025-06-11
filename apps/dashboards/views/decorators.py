# apps/dashboard/views/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """Role-based access decorator"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role not in allowed_roles:
                messages.error(request, "Bu sahifaga kirish huquqingiz yo'q")
                return redirect('dashboard:main')

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator