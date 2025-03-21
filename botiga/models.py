from django.db import models

# Create your models here.
class Iva(models.Model):
    nom = models.CharField(max_length=20,null=False)
    percentatge = models.FloatField(null=False)
    def __str__(self):
        return "Tipus: "+self.nom+"; Percentatge: "+str(self.percentatge)

class Enviament(models.Model):
    nom=models.CharField(max_length=100,null=False)
    dies_min=models.IntegerField(null=False)
    dies_max=models.IntegerField(null=True)
    cost=models.FloatField(null=False)
    preu_min=models.FloatField(null=True)
    iva=models.ForeignKey(Iva, on_delete=models.SET_NULL, null=True)

class Producte(models.Model):
    nom=models.CharField(max_length=100,null=False)
    marca=models.CharField(max_length=20,null=False)
    descripcio=models.CharField(max_length=150,null=False)
    iva=models.ForeignKey(Iva, on_delete=models.SET_NULL, null=True)

class Categoria(models.Model):
    nom = models.CharField(max_length=200)
    jerarquia = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.nom

class CatProd(models.Model):
    prod = models.ForeignKey(Producte, on_delete=models.CASCADE)
    categ = models.ForeignKey(Categoria, on_delete=models.CASCADE)

class Variant(models.Model):
    nom = models.CharField(max_length=100,null=False)
    preu = models.FloatField(null=False)
    dto = models.FloatField(null=True)
    prod = models.ForeignKey(Producte, on_delete=models.CASCADE)

class Imatges(models.Model):
    url = models.CharField(max_length=250,null=False)
    var = models.ForeignKey(Variant, on_delete=models.CASCADE)

class Talla(models.Model):
    nom = models.CharField(max_length=5,null=False)

class TallaVariant(models.Model):
    var = models.ForeignKey(Variant, on_delete=models.CASCADE, null=False)
    talla = models.ForeignKey(Talla, on_delete=models.CASCADE, null=False)
    qty = models.IntegerField(null=False)

class User(models.Model):
    mail=models.CharField(max_length=100, unique=True, null=False)
    nom=models.CharField(max_length=50, null=False)
    cognom=models.CharField(max_length=50, null=False)
    cognom2=models.CharField(max_length=50)
    pswd=models.CharField(max_length=10,null=False)
    direccio=models.CharField(max_length=100)
    poblacio=models.CharField(max_length=100)
    cp=models.CharField(max_length=5)
    pais=models.CharField(max_length=100)
    
    def __str__(self):
        return self.nom

class Cistell(models.Model):
    enviament=models.ForeignKey(Enviament, on_delete=models.DO_NOTHING)
    client=models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False)

class LineaCistell(models.Model):
    cistell=models.ForeignKey(Cistell, on_delete=models.CASCADE, null=False)
    var=models.ForeignKey(TallaVariant, on_delete=models.CASCADE, null=False)
    qty=models.IntegerField(null=True)

class Contadors(models.Model):
    tipus=models.CharField(max_length=10, unique=True, null=False)
    qty=models.IntegerField(null=True)

class MetodePagament(models.Model):
    nom=models.CharField(max_length=20,null=False, unique=True)

class Botiga(models.Model):
    nom=models.CharField(max_length=50,null=False)
    nif=models.CharField(max_length=8,null=False)
    direccio=models.CharField(max_length=100)
    poblacio=models.CharField(max_length=100)
    cp=models.CharField(max_length=5)
    pais=models.CharField(max_length=100)
    registre=models.CharField(max_length=300)

class Factura(models.Model):
    numero=models.CharField(max_length=20)
    tipus=models.ForeignKey(Contadors,on_delete=models.DO_NOTHING, null=False)
    cistell=models.ForeignKey(Cistell, on_delete=models.DO_NOTHING, null=False)
    pagament=models.ForeignKey(MetodePagament, on_delete=models.DO_NOTHING, null=False)
    botiga=models.ForeignKey(Botiga, on_delete=models.DO_NOTHING, null=False)

class LineaFactura(models.Model):
    fact=models.ForeignKey(Factura,on_delete=models.CASCADE, null=False)
    nom=models.CharField(max_length=100,null=False)
    var = models.ForeignKey(Variant, on_delete=models.DO_NOTHING, null=False)
    talla = models.ForeignKey(Talla, on_delete=models.DO_NOTHING, null=False)
    qty = models.IntegerField(null=False)
    preu = models.FloatField(null=False)
    dto = models.FloatField(null=True)
    iva = models.FloatField(null=False)
    total=models.FloatField(null=False)