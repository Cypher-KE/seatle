from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import Account


def account_role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # Redirect to login if the user is not authenticated
            try:
                account = request.user.account
            except Account.DoesNotExist:
                return HttpResponseForbidden("You do not have an account associated with this user.")

            if account.role not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
