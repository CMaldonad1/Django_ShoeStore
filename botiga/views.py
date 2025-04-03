from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.generic import ListView
from .forms import *
from .models import *
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
import json
from .decorator import unauthenticated_user
#request.session["nom"] = request.POST.get("nom_param", "")
#request.session.clear()

# Create your views here.
def login(request):
    if request.method == 'POST':
        user=request.POST.get('user')
        pswd=request.POST.get('pswd')
        logOK=User.objects.filter(mail__iexact=user, pswd=pswd).first()
        #verifiquem que l'usuari s'ha loginat correctament
        if logOK:
            idUser=logOK.id
            #borrem el possible missatge d'error
            if 'logerr' in request.session:
                request.session.pop('logerr')
            #guardem en sessió les dades de l'usuari
            request.session["login"]={
                'id':idUser,
                'nom':logOK.nom
                }
            #verifiquem si te cistells
            exist=Cistell.objects.filter(client__id=idUser, enviament__isnull=True).first()
            qty=0
            # #si te cistell guardem l'id i contem quants items té, sino creem un de nou 
            if exist:
                cistell=exist.id
                auxqty=LineaCistell.objects.filter(cistell=cistell).aggregate(Sum('qty'))
                if auxqty['qty__sum']==None:
                    qty=0
                else:
                    qty=auxqty['qty__sum']
            else:
                novaCistella=Cistell(client=logOK)
                novaCistella.save()
                cistell=novaCistella.id
            request.session['cistella']={
                    'id':cistell,
                    'qty':qty
                }
        else:
            request.session['logerr']="Usuari i/o contrasenya incorrecta!"
    return cataleg(request)

def logoff(request):
    if 'login' in request.session:
        request.session.pop('login')
    if 'cistella' in request.session:
        request.session.pop('cistella')
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
    if 'logerr' in request.session:
        request.session.pop('logerr')
    request.session["page"]="cataleg"
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
    
    if 'logerr' in request.session:
        request.session.pop('logerr')

    if 'enviament' in request.session:
        opcion=request.session['enviament']
    else:
        request.session['enviament']=0

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion=='vuidar':
            vuidarCistella(request)
        elif accion=='incr' or accion=='decr':
            updateCistella(request)
        elif accion=='delete':
            deleteItem(request)
        else:
            opcion = int(request.POST.get('enviament'))
            

    llistat=LineaCistell.objects.filter(cistell_id=request.session['cistella']['id']).all()

    if len(llistat)==0:
        opcion=0

    enviament=Enviament.objects.all()
    request.session['enviament']=opcion
    request.session['fra']=calcularCistella(llistat, opcion)
    return render(request, 'sections/shopping_cart.html',{
        'llistat':llistat,
        'enviament':enviament,
        'opcSelect':int(request.session['enviament'])
    })

def deleteItem(request):
    var=request.POST.get('id')
    LineaCistell.objects.filter(var_id=var).delete()
    qty=int(request.POST.get('qty'))*-1

def calcularCistella(llistat, opcion):
    #Calculem els totals per les factures
    totalSinIva=0
    # totalIva=0
    totalIva=[]
    totalFra=0
    cost=0
    #iterem per el llistat de productes i calculem l'iva i el guardem en una variable diccionari
    for ll in llistat:
        iva=ll.var.var.prod.iva.percentatge
        auxSinIva= round(ll.qty*ll.var.var.preu*(1-ll.var.var.dto),2)
        auxTotalIva= round(auxSinIva*(iva/100), 2)
        ll.preu_qty=auxSinIva
        totalSinIva +=auxSinIva
        calculIva(totalIva,iva,auxTotalIva)
        totalFra += auxSinIva+auxTotalIva
    
    #si s'ha escollit una opció d'enviament farem el calcul d'aquest
    if opcion!=0:
        enviament=Enviament.objects.filter(id=opcion).first()
        if enviament.preu_min>totalSinIva:
            cost=enviament.cost
            iva=enviament.iva.percentatge
            auxTotalIva=round(cost*(iva/100),2)
            calculIva(totalIva,iva,auxTotalIva)
            totalFra+=cost+auxTotalIva

    totalIva=sorted(totalIva, key=lambda k: k.get('nom'), reverse=True)

    return {
            'totalSinIva':totalSinIva,
            'totalEnvio':cost,
            'totalIva':totalIva,
            'totalFra':totalFra
        }

def calculIva(totalIva,iva,total):
        exist=False
        for i in totalIva:
            if i['nom']==iva:
                i['total']+=total
                exist=True
                break
        if not exist:
            totalIva.append({
                'nom':iva,
                'total':total
            })

def updateSessionCistella(request,qty):
    value=int(request.session['cistella']['qty'])+qty
    if value<=0:
        value=0
    request.session['cistella']['qty']=value
    request.session.modified = True

def updateCistella(request):
    var=request.POST.get('id')
    qty=int(request.POST.get('qty'))

    #identifiquem el botó per sapiguer que está fent l'usuari
    accion = request.POST.get('accion')
    incrDecr=1
    if accion=='decr':
        incrDecr=-1
    #actualitzem el valor de la cistella
    updateSessionCistella(request,incrDecr)
    incrDecr+=qty
    if (incrDecr)<=0:
        deleteItem(request)
    else:
        updateLinea(request, var, incrDecr)

def producteEnCistella(request,var):
    cistellId=request.session['cistella']['id']
    exist=LineaCistell.objects.filter(cistell_id=cistellId,var_id=var).first()
    if exist:
        return exist.qty
    else:
        return 0

def updateLinea(request, var, qty):
    idCistell=request.session['cistella']['id']
    LineaCistell.objects.update_or_create(cistell_id=idCistell, var_id=var, defaults={'qty': qty})

@api_view(['POST'])
@unauthenticated_user
def addCistella(request):
    var=request.data["var"]
    qty=int(request.data["qty"])
    qtyCistella=request.session['cistella']['qty']
    exist=producteEnCistella(request,var)
    exist+=qty
    updateLinea(request, var, exist)
       
    # incrementem el contador de la cistella
    updateSessionCistella(request,qty)

    # guardem els items que han agregat a la cistella
    return JsonResponse({'cistella': request.session['cistella']['qty']})

def vuidarCistella(request):
    LineaCistell.objects.filter(cistell_id=request.session['cistella']['id']).delete()
    request.session['cistella']['qty']=0
    
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
                'tId':t.id,
                'qty':t.qty
            }
            talles.append(talla)
        item={
            "id": p.id,
            "nom": p.nom,
            "preu":p.preu,
            "dto":p.dto,
            "imatges":imatges,
            "talles":talles
        }
        
        resposta.append(item)
    return JsonResponse(resposta[0], safe=False) 