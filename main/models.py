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



from django.db import models

class Projet(models.Model):
    METIERS_CHOICES = [
        ('infirmier', 'Infirmier'),
        ('policier', 'Policier'),
        ('enseignant', 'Enseignant'),
        ('ingenieur', 'Ingénieur'),
        ('medecin', 'Médecin'),
        ('artiste', 'Artiste'),
        ('autre', 'Autre')
    ]

    utilisateur = models.ForeignKey("Particulier", on_delete=models.CASCADE, null=True, blank=True)
    titre = models.CharField(max_length=100)
    description = models.TextField()
    metier = models.CharField(max_length=50, choices=METIERS_CHOICES, default='autre')  # ✅ Ajout du champ
    date_creation = models.DateTimeField(auto_now_add=True)  # ✅ Ajout de la date de création

    def __str__(self):
        return f"{self.titre} - {self.get_metier_display()}"





class Dashboard(models.Model):
    professionnel = models.OneToOneField(Professionnel, on_delete=models.CASCADE, related_name='dashboard')

    def __str__(self):
        return f"Dashboard de {self.professionnel.nom_societe}"
    


class Message(models.Model):
    conversation_id = models.CharField(max_length=255,default = 1)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)

    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.sender} à {self.receiver} - {self.timestamp}"
    
    class Meta:
        ordering = ['timestamp']


class Projets(models.Model):
    TYPE_PROJET_CHOICES = [
        ('achat', 'Acheter un bien'),
        ('vente', 'Vendre un bien'),
    ]

    TYPE_BIEN_CHOICES = [
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('studio', 'Studio'),
    ]

    TRANSPORT_CHOICES = [
        ('tram', 'Tram'),
        ('metro', 'Métro'),
        ('bus', 'Bus'),
        ('gare', 'Gare'),
    ]

    TRAVAUX_CHOICES = [
        ('aucun', 'Aucun travaux'),
        ('petits', 'Petits travaux'),
        ('renovation', 'Rénovation complète'),
    ]

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type_projet = models.CharField(max_length=10, choices=TYPE_PROJET_CHOICES)
    type_bien = models.CharField(max_length=20, choices=TYPE_BIEN_CHOICES)
    nombre_pieces = models.IntegerField(default=1)
    superficie = models.PositiveIntegerField(default=50)
    budget = models.PositiveIntegerField(default=150000)
    localisation = models.CharField(max_length=255, blank=True)

    exterieur = models.BooleanField(default=False)
    garage = models.BooleanField(default=False)
    transport = models.CharField(max_length=10, choices=TRANSPORT_CHOICES, blank=True)
    travaux = models.CharField(max_length=20, choices=TRAVAUX_CHOICES, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.get_type_projet_display()} - {self.get_type_bien_display()}"