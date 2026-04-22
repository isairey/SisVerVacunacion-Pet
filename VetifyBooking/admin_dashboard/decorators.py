from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def admin_required(function=None, redirect_url='/'):
    """
    Decorator para vistas que requieren que el usuario sea superusuario
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=redirect_url
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator