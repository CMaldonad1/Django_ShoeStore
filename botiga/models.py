from django.db import models

# Create your models here.
class Iva(models.Model):
    nom = models.CharField(max_length=200)
    percentatge = models.FloatField()

    #funcion para que se pueda ver en el administrador las clases
    #con sus valores en vez de objetos
    def __str__(self):
        return "Tipus: "+self.nom+"; Percentatge: "+str(self.percentatge)

class Categoria(models.Model):
    nom = models.CharField(max_length=200)
    jerarquia = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.nom