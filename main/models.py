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
class Projet(models.Model):
    utilisateur = models.ForeignKey(Particulier, on_delete=models.CASCADE, related_name='projets')
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Carte(models.Model):
    utilisateur = models.ForeignKey(Particulier, on_delete=models.CASCADE, related_name='cartes')
    titre = models.CharField(max_length=255)
    projets = models.ManyToManyField(Projet, related_name='cartes')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} - {self.utilisateur.nom}"


class Dashboard(models.Model):
    professionnel = models.OneToOneField(Professionnel, on_delete=models.CASCADE, related_name='dashboard')
    cartes = models.ManyToManyField(Carte, related_name='dashboards')

    def __str__(self):
        return f"Dashboard de {self.professionnel.nom_societe}"