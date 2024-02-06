from django.db import models

# Create your models here.
from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    tele = models.CharField(max_length=20)
    cin = models.CharField(max_length=20)
    image = models.ImageField(upload_to='clients', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Car(models.Model):
    model = models.CharField(max_length=100)
    maker = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='Available')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='cars', null=True, blank=True)

    def __str__(self):
        return f"{self.maker} {self.model} - {self.year}"
