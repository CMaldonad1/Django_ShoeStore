from django.shortcuts import render
import json
from django.core.serializers import serialize
from django.http import HttpResponse
from .forms import *
from .models import *
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
#request.session["nom"] = request.POST.get("nom_param", "")
#request.session.clear()

# Create your views here.
def login(request):
    #if request.method == 'POST':
    #    Project.objects.create(name=request.POST['name']) 
    return home(request)

def home(request):
    request.session["page"]="home"
    return render(request, 'sections/home.html',{
        'title': 'Home',
        'head': 'Benvingut a MaviEsports',
        'login': 2,
    })

def registrat(request):
    #if request.method == 'POST':
    #    Project.objects.create(name=request.POST['name']) 
        
    return render(request, 'sections/signIn.html',{
        'title': 'Sign In',
        'head': 'Registrat',
        'form': SignIn(),
    })

def cataleg(request, catid=None):
    request.session["page"]="cataleg"
    #query per obtindre les categories i si tenen fills
    categories=Categoria.objects.raw("SELECT * FROM `botiga_categoria` bc LEFT JOIN (SELECT jerarquia_id, count(jerarquia_id) "
                                    "as \"count\" FROM `botiga_categoria` where jerarquia_id is not null GROUP BY jerarquia_id) "
                                    "cnt on bc.id=cnt.jerarquia_id; ")
    if request.method == 'GET':
        productes=Variant.objects.filter(prod_id__in=CatProd.objects.filter(categ_id__in=returnChildrenJerarqui(catid)).values_list('prod', flat=True)).order_by('nom')
    else:
        productes=Variant.objects.all()
    
    return render(request, 'sections/cataleg.html',{
        'title': 'cataleg',
        'head': 'Productes',
        'categories': categories,
        'productes': productes,
    })

def informacio(request):
    request.session["page"]="informacio"
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
    request.session["page"]="shopping"
    return render(request, 'sections/shopping_cart.html')

#funciò recursiva per treure els productes de les categories
def returnChildrenJerarqui(id):
    cat=[]
    cat.append(id)
    fill=Categoria.objects.filter(jerarquia=id).values_list('id', flat=True)
    for f in fill:
        cat.extend(returnChildrenJerarqui(f))
    return cat
    