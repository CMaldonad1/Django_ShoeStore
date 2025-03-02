from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'home.html',{
        'title': 'Home',
        'head': 'Benvingut a MaviEsports',
        'login': 1,
    })
def shopping(request):
    return render(request, 'sections/shopping_cart.html')