from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class Particulier(models.Model):
    # Gardez ce champ commenté pour le moment
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='particulier',null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    date_naissance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Professionnel(models.Model):
    # Gardez ce champ commenté pour le moment
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professionnel',null=True, blank=True)
    nom_societe = models.CharField(max_length=100)
    siret = models.CharField(max_length=14)
    email_pro = models.EmailField()
    secteur_activite = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_societe



class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('particulier', 'Particulier'),
        ('professionnel', 'Professionnel'),
    )
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='particulier')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


