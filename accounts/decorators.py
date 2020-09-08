from django.http import Http404
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_groups(allowed_groups=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            print(request.user.groups.all(), allowed_groups)
            groups = request.user.groups.all() if request.user.groups.exists() else []

            if any(group.name in allowed_groups for group in groups):
                return view_func(request, *args, **kwargs)

            raise Http404()

        return wrapper_func

    return decorator
