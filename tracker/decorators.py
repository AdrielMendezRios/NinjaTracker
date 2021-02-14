from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tracker:index')
        else:
            return view_func(request, *args, **kwargs)
    
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0]
                # print(group)
                # print(type(group))

            if str(group) in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponse("You're not authorized to read this page")
        return wrapper_func
    return decorator

