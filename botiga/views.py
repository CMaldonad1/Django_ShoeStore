from django.shortcuts import render
from django.core.serializers import serialize
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.db.models import Sum
from rest_framework.decorators import api_view
from .forms import *
from .models import *
from django.db.models import Prefetch, Q
from django.shortcuts import render
from .decorator import *
import requests
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.
def login(request):
    if request.method == 'POST':
        user=request.POST.get('user')
        pswd=request.POST.get('pswd')
        logOK=User.objects.filter(mail__iexact=user, pswd=pswd).first()
        #verifiquem que l'usuari s'ha loginat correctament
        if logOK!=None:
            idUser=logOK.id
            #borrem el possible missatge d'error
            if 'logerr' in request.session:
                request.session.pop('logerr')
            #guardem en sessió les dades de l'usuari
            request.session["login"]={
                'id':idUser,
                'nom':logOK.nom,
                'mail':logOK.mail
                }
            #verifiquem si te cistells
            exist=Cistell.objects.filter(client__id=idUser, pagada=False).first()
            qty=0
            #si te cistell guardem l'id i contem quants items té, sino creem un de nou 
            if exist:
                cistell=exist.id
                auxqty=LineaCistell.objects.filter(cistell=cistell).aggregate(Sum('qty'))
                if auxqty['qty__sum']==None:
                    qty=0
                else:
                    qty=auxqty['qty__sum']
            else:
                cistell=creacioNovaCistella(request)
            sessioCistella(request, cistell, qty)
        else:
            request.session['logerr']="Usuari i/o contrasenya incorrecta!"
    page=request.session.get('page')
    match page:
        case 'cataleg':
            return cataleg(request)
        case 'shopping':
            return shopping(request)
        case 'informacio':
            return informacio(request, request.session.get('item'))

def creacioNovaCistella(request):
        novaCistella=Cistell(request.session["login"]['id'])
        novaCistella.save()

        return novaCistella.id

def sessioCistella(request, cistell, qty):
        request.session['cistella']={
                'id':cistell,
                'qty':qty
            }
        
def logoff(request):
    request.session.clear()
    return cataleg(request)

def cataleg(request, catid=None):
    request.session["page"]="cataleg"
    #query per obtindre les categories i si tenen fills
    categories=Categoria.objects.raw("SELECT * FROM `botiga_categoria` bc LEFT JOIN (SELECT jerarquia_id, count(jerarquia_id) "
                                    "as \"count\" FROM `botiga_categoria` where jerarquia_id is not null GROUP BY jerarquia_id) "
                                    "cnt on bc.id=cnt.jerarquia_id; ")
    talles=Talla.objects.all()
    jerarquia=""

    if catid!=0 and catid!=None:
        #guardem el nom de la categoria seleccionada
        request.session["catSel"]=Categoria.objects.filter(id=catid).values('nom','id').first()
    elif catid==0 or catid==None:
        #si la catid es 0 vol dir que no s'ha seleccionat cap
        request.session["catSel"]=""
        print("hello")
        
    
    #guardem tota la informació de les jerarquies si una ha sigut seleccionada
    if request.session.get('catSel')!="":
        jerarquia=Categoria.objects.filter(id__in=returnParentJerarqui(request.session.get('catSel')["id"])).order_by('id')

    productes=llistatProductes(request)

    return render(request, 'sections/cataleg.html',{
        'title': 'cataleg',
        'head': 'Productes',
        'categories': categories,
        'productes': productes,
        'talles':talles,
        'jerarquia':jerarquia
    })

def llistatProductes(request):
    productes = Producte.objects.prefetch_related(
            Prefetch('variant_set__imatges_set')
        )
    catid=request.session.get('catSel')
    #si hi han filtres els apliquem
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
    if catid != "":
        productes=productes.filter(id__in=CatProd.objects.filter(categ_id__in=returnChildrenJerarqui(catid['id'])).values_list('prod', flat=True))
    
    aplicarDto(productes)
    return productes

def aplicarDto(productes):
    #calculem el preu amb dte
    for p in productes:
        dto=p.variant_set.all()[0].dto
        preu=p.variant_set.all()[0].preu
        if dto>0:
            preu=round(preu*(1-dto),2)
        p.variant_set.all()[0].preu_dto=preu

#API per filtrar en el catáleg
@api_view(['POST'])
def filtrar(request):
    pmin=request.data["pmin"]
    pmax=request.data["pmax"]
    nom=request.data["nom"]
    talles=request.data["talles"]

    request.session['filtres']={
        'pmin':pmin,
        'pmax':pmax,
        'nom':nom,
        'talles':talles
    }
    
    productes=llistatProductes(request)

    html_content=render_to_string('sections/llistatProductes.html',
                                  {
                                      'productes':productes
                                })
    return HttpResponse(html_content) 

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
    request.session['item']=varid
    if varid!=None:
        #volem que la variant seleccionada surti primer
        varSel = Variant.objects.filter(id=varid).prefetch_related(
                Prefetch('tallavariant_set', queryset=TallaVariant.objects.select_related('talla')),
                Prefetch('imatges_set')
            ).first()
        preu=varSel.preu
        if(varSel.dto>0):
            preu=round(varSel.preu*(1-varSel.dto),2)
        varSel.preu_dto=preu

        #carreguem la resta menys la seleccionada
        restaVar = Variant.objects.filter(prod=varSel.prod.id).exclude(id=varSel.id).prefetch_related(
                Prefetch('tallavariant_set', queryset=TallaVariant.objects.select_related('talla')),
                Prefetch('imatges_set')
            )

        return render(request, 'sections/informacio.html',{
            'prod':varSel,
            'resta':restaVar
        })
    else:
        return cataleg(request)

@unauthenticated_user
def user(request):
    request.session["page"]="usuari"
    return render(request, 'sections/usuari.html',{
        'title': 'Usuari',
        'head': 'Usuari',
    })
#programa de la vista de la cistella
def shopping(request):
    request.session["page"]="shopping"
    
    if 'enviament' in request.session:
        opcion=request.session['enviament']
    else:
        opcion=0

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
    
    request.session['enviament']=opcion

    if 'cistella' in request.session:
        llistat=LineaCistell.objects.filter(cistell_id=request.session['cistella']['id']).all()
        enviament=Enviament.objects.all()
        request.session['fra']=calcularCistella(llistat, opcion)

        return render(request, 'sections/shopping_cart.html',{
            'llistat':llistat,
            'enviament':enviament,
            'opcSelect':int(opcion)
        })
    else:
        return render(request, 'sections/shopping_cart.html')
#elimnació d'un item de la cistella
def deleteItem(request):
    var=request.POST.get('id')
    LineaCistell.objects.filter(var_id=var).delete()
    qty=int(request.POST.get('qty'))*-1
    updateSessionCistella(request,qty)
#calcul de l'import de la cistella tenint en compte l'opció d'enviament
def calcularCistella(llistat, opcion):
    #Calculem els totals per les factures
    totalSinIva=0
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
#calcul de l'iva per tipus i creació d'un JSON amb els diferents import
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
#actualització de l'informació de la qty d'items de la cistella
def updateSessionCistella(request,qty):
    value=int(request.session['cistella']['qty'])+qty
    if value<=0:
        value=0
    request.session['cistella']['qty']=value
    request.session.modified = True
#increment o decrement dels items de la cistella
def updateCistella(request):
    var=request.POST.get('id')
    qty=int(request.POST.get('qty'))

    #identifiquem el botó per sapiguer que está fent l'usuari
    accion = request.POST.get('accion')
    incrDecr=1
    if accion=='decr':
        incrDecr=-1
    #actualitzem el valor de la cistella
    qty+=incrDecr
    
    if (qty)<=0:
        deleteItem(request)
    else:
        updateLinea(request, var, qty)
        updateSessionCistella(request,incrDecr)
#verificació de si l'item existeix en la cisetlla
def producteEnCistella(request,var):
    cistellId=request.session['cistella']['id']
    exist=LineaCistell.objects.filter(cistell_id=cistellId,var_id=var).first()
    if exist:
        return exist.qty
    else:
        return 0
#actualització del valor del item de la cistellas
def updateLinea(request, var, qty):
    idCistell=request.session['cistella']['id']
    LineaCistell.objects.update_or_create(cistell_id=idCistell, var_id=var, defaults={'qty': qty})

@api_view(['POST'])
def realitzarPagament(request):
    # idCistell=request.session['cistella']['id']
    email=request.session['login']['mail']
    # pagarCistell(idCistell)
    # idFactura=creacioFactura(request, idCistell)
    idFactura=1
    # altaIvaFactura(request,idFactura)
    # altaLineasFra(idCistell, idFactura)

    #ens carreguem la informació que hi ha en sessio de la compra
    # eliminarSessionsCompra(request)

    #creació de nou cistell de compra per a l'usuari.
    # cistell=creacioNovaCistella(request)
    # sessioCistella(request, cistell, 0)

    #demanem la factura a jasperReport
    response=jasperFactura(idFactura)
    header="Pagament realitzat correctament!"
    #Si la factura de Jasper s'ha generat correctament l'enviem per correu. Depenent de 
    #si s'ha pogut o no traslladarem un misatge o un altre.
    if response.status_code==200:
        enviarEmail(request,response,idFactura)
        msg="S'ha fet arribar al teu correu "+email+" la factura de la teva compra.<br>"
    else:
        msg="La teva factura no s'ha pogut enviar al teu correu "+email+" per problemes técnics.<br>"
    
    msg+="Pots tornar a renviarte les teves factures a través del teu perfil."
    html_content=render_to_string('sections/pagamentComplet.html',
                                  {
                                      'header':header,
                                      'msg':msg
                                })
    return HttpResponse(html_content)
#eliminar Cistella, Fra i enviament de session
def eliminarSessionsCompra(request):
    request.session.pop('cistella')
    request.session.pop('fra')
    request.session.pop('enviament')

def jasperFactura(idFactura):
    jasperserver_url = settings.JASPER_URL
    username = settings.JASPER_USER
    password = settings.JASPER_PASSWORD
    params={
        'fact_id':idFactura
    }
    response = requests.get(
        jasperserver_url,
        params=params,
        auth=HTTPBasicAuth(username, password),
        headers={'Accept': 'application/pdf'}
    )
    return response

def enviarEmail(request, response, idFactura):
    email= EmailMessage(
        subject="Factura "+str(idFactura),
        body="Hola "+request.session['login']['nom']+",<br><br>graciès per la teva compra. "+ 
            "Troba adjunt la teva factura.<br><br>"+
            "Atentament,<br>"+
            "MaviBotiga",
        from_email=settings.EMAIL_HOST_USER,
        to=[request.session['login']['mail']]
    )
    email.content_subtype = 'html'
    email.attach(
        "Factura_"+str(idFactura)+".pdf",
        response.content,
        'application/pdf'
    )
    email.send()

def pagarCistell(idCistell):
    cistell=Cistell.objects.get(id=idCistell)
    cistell.pagada=True
    cistell.save()
    
def creacioFactura(request,idCistell):
    metodePago=MetodePagament.objects.filter(id=1).first()
    tipus=Contadors.objects.filter(id=1).first()
    botiga=Botiga.objects.filter(id=1).first()
    numFormat=f"{tipus.qty:06d}"
    numFra=tipus.tipus+"-"+numFormat
    costEnviament=request.session['fra']['totalEnvio']
    totalFra=request.session['fra']['totalFra']

    fra=Factura(numero=numFra,tipus=tipus,
                cistell_id=idCistell,pagament=metodePago,
                botiga=botiga,gtoEnvio=costEnviament,
                totalFra=totalFra
                )
    fra.save()
    return fra.id

def altaIvaFactura(request, idFactura):
    ivas=request.session['fra']['totalIva']
    for i in ivas:
        iva=IvaFactura(fact_id=idFactura, tipusiva=i['nom'], total=i['total'])
        iva.save()

def altaLineasFra(idCistell, idFactura):
    itemsCistella=LineaCistell.objects.filter(cistell_id=idCistell).all()

    for item in itemsCistella:
        preu=item.var.var.preu
        qty=item.qty
        dto=item.var.var.dto
        iva=item.var.var.prod.iva.percentatge
        total=round(((preu*qty)*(1-dto))*(1+(iva/100)),2)
        lf=LineaFactura(fact_id=idFactura,
                        tallavar_id=item.var.id,
                        qty=qty, preu=preu,
                        dto=dto, iva=iva,
                        total=total)
        lf.save()

#pagament de cistella
@pagarLimitation
def pagamentCistella(request):
    user=User.objects.filter(id=request.session['login']['id']).first()
    enviament=Enviament.objects.filter(id=request.session.get('enviament')).first()
    return render(request, 'sections/pagament.html',
                  {
                      'user':user,
                      'enviament':enviament,
                  })

@api_view(['POST'])
@unauthenticated_user
def addCistella(request):
    var=request.data["var"]
    qty=int(request.data["qty"])
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

@api_view(['GET'])
def eliminarMissatge(request):
    if 'logerr' in request.session:
        request.session.pop('logerr')
    return JsonResponse({'done':1}, safe=False) 