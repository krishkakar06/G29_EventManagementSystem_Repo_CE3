from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_role = getattr(request.user.profile, 'role', None)
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                return HttpResponseForbidden("You do not have permission to access this page.")
            return redirect('login')
        return wrapper
    return decorator
