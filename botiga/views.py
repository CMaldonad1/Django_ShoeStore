from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
#request.session["nom"] = request.POST.get("nom_param", "")
#request.session.clear()

# Create your views here.
def login(request):
    #if request.method == 'POST':
    #    Project.objects.create(name=request.POST['name']) 
    return home(request)

def home(request):
    return render(request, 'sections/home.html',{
        'title': 'Home',
        'head': 'Benvingut a MaviEsports',
        'login': 0,
    })

def registrat(request):
    #if request.method == 'POST':
    #    Project.objects.create(name=request.POST['name']) 
        
    return render(request, 'sections/signIn.html',{
        'title': 'Sign In',
        'head': 'Registrat',
        'form': SignIn(),
    })

def cataleg(request):
    return render(request, 'sections/cataleg.html',{
        'title': 'cataleg',
        'head': 'Productes',
    })
def informacio(request):
    return render(request, 'sections/informacio.html',{
        'title': 'Informacio',
        'head': 'Info',
    })
def user(request):
    return render(request, 'sections/usuari.html',{
        'title': 'Usuari',
        'head': 'Usuari',
    })
def shopping(request):
    return render(request, 'sections/shopping_cart.html')