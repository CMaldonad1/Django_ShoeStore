from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

def unauthenticated_user(func):
    def wrapper_func(request, *args, **kwargs):
        if 'login' not in request.session or request.session.get('login')==-1:
            return JsonResponse({'cistella': -1})
        else:
            return func(request, *args, **kwargs)
    return wrapper_func

def pagarLimitation(func):
    def wrapper_func(request, *args, **kwargs):
        if 'login' not in request.session or request.session.get('login')==-1:
            return redirect('cataleg')
        elif 'enviament' not in request.session or request.session.get('enviament')==0:
            return redirect('cistella')
        else:
            return func(request, *args, **kwargs)
    return wrapper_func