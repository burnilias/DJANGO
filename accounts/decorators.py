import functools
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


def _get_token_user(request):
    """Authenticate user via DRF Token header. Returns (user, None) or raises."""
    auth = TokenAuthentication()
    try:
        user, _ = auth.authenticate(request)
        return user
    except AuthenticationFailed:
        return None
    except Exception:
        return None


def login_required_custom(view_func):
    """Decorator: ensure a valid DRF Token is present and user status is active."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = _get_token_user(request)
        if user is None:
            return JsonResponse(
                {'success': False, 'message': 'Authentication required.'},
                status=401,
            )
        if user.status == 'desactive':
            return JsonResponse(
                {'success': False, 'message': 'Ce compte est désactivé.'},
                status=403,
            )
        if user.status == 'veille':
            return JsonResponse(
                {'success': False, 'message': 'Ce compte est en veille.'},
                status=403,
            )
        # Attach the resolved user to the request for downstream use
        request.custom_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Decorator: ensure the authenticated user has one of the allowed roles."""
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'custom_user', None)
            if user is None:
                user = _get_token_user(request)
            if user is None:
                return JsonResponse(
                    {'success': False, 'message': 'Authentication required.'},
                    status=401,
                )
            if user.role not in allowed_roles:
                return JsonResponse(
                    {'success': False, 'message': 'Access denied for your role.'},
                    status=403,
                )
            request.custom_user = user
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ── Session-based decorators for Django template views ──────────────────────

def session_login_required(view_func):
    """Decorator: check Django session for user_id and active status (template views)."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return HttpResponseRedirect('/')
        from .models import CustomUser
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            request.session.flush()
            return HttpResponseRedirect('/')
        if user.status != 'active':
            request.session.flush()
            return HttpResponseRedirect('/')
        request.session_user = user
        return view_func(request, *args, **kwargs)
    return wrapper


def session_role_required(*allowed_roles):
    """Decorator: check session user has one of the allowed roles (template views)."""
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'session_user', None)
            if user is None:
                user_id = request.session.get('user_id')
                if not user_id:
                    return HttpResponseRedirect('/')
                from .models import CustomUser
                try:
                    user = CustomUser.objects.get(pk=user_id)
                except CustomUser.DoesNotExist:
                    request.session.flush()
                    return HttpResponseRedirect('/')
            if user.role not in allowed_roles:
                return HttpResponseRedirect('/')
            request.session_user = user
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
