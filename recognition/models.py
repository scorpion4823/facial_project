

# Create your models here.
from django.db import models

class Person(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    adresse = models.CharField(max_length=255)
    image = models.ImageField(upload_to='persons/')

    def __str__(self):
        return f"{self.nom} {self.prenom}"
