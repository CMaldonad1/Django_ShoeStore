from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.generic import ListView
from .forms import *
from .models import *
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
import json
#request.session["nom"] = request.POST.get("nom_param", "")
#request.session.clear()

# Create your views here.
def login(request):
    #if request.method == 'POST':
    #    Project.objects.create(name=request.POST['name']) 
    return cataleg(request)

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
    request.session["login"]=1
    #query per obtindre les categories i si tenen fills
    categories=Categoria.objects.raw("SELECT * FROM `botiga_categoria` bc LEFT JOIN (SELECT jerarquia_id, count(jerarquia_id) "
                                    "as \"count\" FROM `botiga_categoria` where jerarquia_id is not null GROUP BY jerarquia_id) "
                                    "cnt on bc.id=cnt.jerarquia_id; ")
    talles=Talla.objects.all()
    jerarquia=""
    if request.session.get('catSel')!="" and catid==None:
        idSessionCatSel=request.session.get('catSel')["id"]
        jerarquia=Categoria.objects.filter(id__in=returnParentJerarqui(idSessionCatSel)).order_by('id')
        productes=Producte.objects.filter(id__in=CatProd.objects.filter(categ_id__in=returnChildrenJerarqui(idSessionCatSel)).values_list('prod', flat=True)).prefetch_related('variant_set__imatges_set')
    elif catid!=0 and catid!=None:
        #guardem el nom de la categoria seleccionada
        request.session["catSel"]=Categoria.objects.filter(id=catid).values('nom','id').first()
        #guardem tota la informació de les jerarquies
        jerarquia=Categoria.objects.filter(id__in=returnParentJerarqui(catid)).order_by('id')
        #guardem unicament els productes que estan en el llistat de categories seleccionades
        productes=Producte.objects.filter(id__in=CatProd.objects.filter(categ_id__in=returnChildrenJerarqui(catid)).values_list('prod', flat=True)).prefetch_related('variant_set__imatges_set')
    else:
        request.session["catSel"]=""
        productes = Producte.objects.prefetch_related(
                Prefetch('variant_set__imatges_set')
            )

    if 'filtres' in request.session:
        filtres=request.session.get('filtres')
        if filtres['pmin']!="":
            productes=productes.filter(id__in=Variant.objects.filter(preu__gte = filtres['pmin']).values_list('prod', flat=True))
        if filtres['pmax']!="":
            productes=productes.filter(id__in=Variant.objects.filter(preu__lte = filtres['pmax']).values_list('prod', flat=True))
        if filtres['nom']!="":
            productes=productes.filter(Q(nom__icontains=filtres['nom'])|Q(marca__icontains=filtres['nom']))
        if filtres['talles']!="":
            tallaFiltre=filtres['talles']
            listtalles=tallaFiltre.split(",")
            productes=productes.filter(id__in=Variant.objects.filter(id__in=TallaVariant.objects.filter(talla__in=listtalles).values_list('var', flat=True)).values_list('prod', flat=True))
   
   #calculem el preu amb dte
    for p in productes:
        dto=p.variant_set.all()[0].dto
        preu=p.variant_set.all()[0].preu
        if dto>0:
            preu=round(preu*(1-dto),2)
        p.variant_set.all()[0].preu_dto=preu

    return render(request, 'sections/cataleg.html',{
        'title': 'cataleg',
        'head': 'Productes',
        'categories': categories,
        'productes': productes,
        'form': filterCat(),
        'talles':talles,
        'jerarquia':jerarquia
    })
#funciò recursiva per treure els pares de les categories
def returnParentJerarqui(id):
    cat=[]
    cat.append(id)
    fill=Categoria.objects.filter(id=id).values_list('jerarquia', flat=True)
    for f in fill:
        cat.extend(returnParentJerarqui(f))
    return cat
#funciò recursiva per treure els fills de les categories
def returnChildrenJerarqui(id):
    cat=[]
    cat.append(id)
    fill=Categoria.objects.filter(jerarquia=id).values_list('id', flat=True)
    for f in fill:
        cat.extend(returnChildrenJerarqui(f))
    return cat

def informacio(request, varid=None):
    request.session["page"]="informacio"
    if varid!=None:
        #volem que la variant seleccionada surti primer
        varSel = Variant.objects.filter(id=varid).prefetch_related(
                Prefetch('tallavariant_set', queryset=TallaVariant.objects.select_related('talla')),
                Prefetch('imatges_set')
            )

        #carreguem la resta menys la seleccionada
        restaVar = Variant.objects.filter(prod=varSel[0].prod.id).exclude(id=varSel[0].id).prefetch_related(
                Prefetch('tallavariant_set', queryset=TallaVariant.objects.select_related('talla')),
                Prefetch('imatges_set')
            )
        allVar = varSel | restaVar #combinem els dos resultats

        for p in allVar:
            preu=p.preu
            dto=p.dto
            if(dto>0):
                preu=round(preu*(1-dto),2)
            p.preu_dto=preu

        return render(request, 'sections/informacio.html',{
            'prod':allVar
        })
    else:
        return cataleg(request)

def user(request):
    request.session["page"]="usuari"
    return render(request, 'sections/usuari.html',{
        'title': 'Usuari',
        'head': 'Usuari',
    })

def shopping(request):
    request.session["page"]="shopping"
    return render(request, 'sections/shopping_cart.html')

def add(request):
    if 'cistella' not in request.session:
        request.session['cistella']=1
    else:
        request.session['cistella']=request.session['cistella']+1
    return JsonResponse({'cistella': request.session['cistella']})

@api_view(['POST'])
def filtrar(request):
    pmin=request.data["pmin"]
    pmax=request.data["pmax"]
    nom=request.data["nom"]
    talles=request.data["talles"]
    listtalles=""
    if len(talles)>0:
        listtalles=talles.split(",")

    productes=Variant.objects.prefetch_related('imatges_set')
    if pmin!="":
        productes=productes.filter(preu__gte=pmin)
    if pmax!="":
        productes=productes.filter(preu__lte=pmax)
    if nom!="":
        productes=productes.filter(Q(prod__nom__icontains=nom)|Q(prod__marca__icontains=nom))
    if listtalles!="":
        productes=productes.filter(id__in=TallaVariant.objects.filter(talla__in=listtalles).values_list('var', flat=True))
    if request.session.get('catSel') != "":
        productes=productes.filter(prod__id__in=CatProd.objects.filter(categ__in=returnChildrenJerarqui(request.session.get('catSel')['id'])).values_list('prod', flat=True))

    request.session['filtres']={
        'pmin':pmin,
        'pmax':pmax,
        'nom':nom,
        'talles':talles
    }

    resposta=[]
    for p in productes:
        imatges=[]
        for i in p.imatges_set.all():
            imatges.append(i.url)
        item={
            "id": p.id,
            "prod":p.prod.nom,
            "prodId":p.prod.id,
            "marca":p.prod.marca,
            "var":p.nom,
            "preu":p.preu,
            "dto":p.dto,
            "descr":p.prod.descripcio,
            "imatges":imatges
        }
        resposta.append(item)
    return JsonResponse(resposta, safe=False)    

@api_view(['POST'])
def variantInfo(request):
    idVar=request.data["idVar"]
    productes=Variant.objects.filter(id=idVar).prefetch_related('imatges_set')
    resposta=[]
    for p in productes:
        imatges=[]
        talles=[]
        for i in p.imatges_set.all():
            imatges.append(i.url)
        for t in p.tallavariant_set.all():
            talla={
                'tNom':t.talla.nom,
                'tId':t.talla.id,
                'qty':t.qty
            }
            talles.append(talla)
        item={
            "id": p.id,
            "preu":p.preu,
            "dto":p.dto,
            "imatges":imatges,
            "talles":talles
        }
        
        resposta.append(item)
    return JsonResponse(resposta[0], safe=False) 