from django.http import HttpResponse, JsonResponse

def unauthenticated_user(func):
    def wrapper_func(request, *args, **kwargs):
        if 'login' not in request.session or request.session.get('login')==-1:
            return JsonResponse({'cistella': 0})
        else:
            return func(request, *args, **kwargs)
    return wrapper_func