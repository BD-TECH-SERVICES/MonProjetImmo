from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.html import format_html
import os

class CustomUserManager(UserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_type', 'particulier')
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'professionnel')
        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser):
    class UserType(models.TextChoices):
        PARTICULIER = 'particulier', _('Particulier')
        PROFESSIONNEL = 'professionnel', _('Professionnel')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    email = models.EmailField(unique=True, verbose_name=_('email address'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Téléphone'))
    address = models.TextField(blank=True, verbose_name=_('Adresse'))
    user_type = models.CharField(
        max_length=15,
        choices=UserType.choices,
        default=UserType.PARTICULIER,
        verbose_name=_("Type d'utilisateur")
    )
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_user_type_display()})"
    
    @property
    def est_professionnel(self):
        return self.user_type == self.UserType.PROFESSIONNEL
    
    @property
    def est_particulier(self):
        return self.user_type == self.UserType.PARTICULIER
    
    def get_absolute_url(self):
        if self.est_professionnel:
            return '/professionnel/'
        return '/mon-espace/'
    
    @property
    def profil_complet(self):
        """Retourne True si le profil de l'utilisateur est complet"""
        if self.est_particulier:
            return hasattr(self, 'profil_particulier')
        elif self.est_professionnel:
            return hasattr(self, 'profil_pro')
        return False
        
    def get_unread_messages_count(self):
        """
        Retourne le nombre de messages non lus pour l'utilisateur
        """
        from django.db.models import Q, Count
        
        if self.est_professionnel:
            # Pour les professionnels : compter les messages non lus dans leurs conversations
            return Message.objects.filter(
                conversation__professionnel=self,
                lu=False
            ).exclude(expediteur=self).count()
        else:
            # Pour les particuliers : compter les messages non lus dans leurs conversations
            return Message.objects.filter(
                conversation__projet__utilisateur=self,
                lu=False
            ).exclude(expediteur=self).count()

class ProfilParticulier(models.Model):
    """Modèle pour stocker les informations complémentaires des particuliers"""
    utilisateur = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profil_particulier',
        verbose_name=_("Utilisateur")
    )
    date_naissance = models.DateField(
        verbose_name=_("Date de naissance"),
        null=True,
        blank=True
    )
    civilite = models.CharField(
        max_length=10,
        choices=(
            ('M', _('Monsieur')),
            ('Mme', _('Madame')),
            ('Mlle', _('Mademoiselle')),
        ),
        verbose_name=_("Civilité"),
        blank=True
    )
    situation_familiale = models.CharField(
        max_length=20,
        choices=(
            ('celibataire', _('Célibataire')),
            ('marie', _('Marié(e)')),
            ('pacs', _('Pacsé(e)')),
            ('divorce', _('Divorcé(e)')),
            ('veuf', _('Veuf/Veuve')),
        ),
        verbose_name=_("Situation familiale"),
        blank=True
    )
    nombre_enfants = models.PositiveIntegerField(
        verbose_name=_("Nombre d'enfants"),
        default=0
    )
    profession = models.CharField(
        max_length=100,
        verbose_name=_("Profession"),
        blank=True
    )
    revenu_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Revenu mensuel (€)"),
        null=True,
        blank=True
    )
    notification_email = models.BooleanField(
        verbose_name=_("Recevoir les notifications par email"),
        default=True
    )
    notification_sms = models.BooleanField(
        verbose_name=_("Recevoir les notifications par SMS"),
        default=False
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil particulier")
        verbose_name_plural = _("profils particuliers")
        ordering = ['-date_creation']

    def __str__(self):
        return f"Profil de {self.utilisateur.get_full_name() or self.utilisateur.email}"

    def age(self):
        """Calcule l'âge à partir de la date de naissance"""
        if not self.date_naissance:
            return None
        today = timezone.now().date()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))


class TypeBien(models.Model):
    nom = models.CharField(max_length=100, verbose_name=_("Nom"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icone = models.CharField(max_length=50, blank=True, help_text=_("Classe Font Awesome, ex: fa-home"))
    
    class Meta:
        verbose_name = _("type de bien")
        verbose_name_plural = _("types de biens")
        ordering = ['nom']
        
    def __str__(self):
        return self.nom

class TypeEtape(models.TextChoices):
    # Étapes pour l'achat
    DEFINITION_PROJET = 'definition', _('Définition du projet')
    RECHERCHE_BIEN = 'recherche', _('Recherche de biens')
    VISITES = 'visites', _('Visites')
    OFFRES = 'offres', _('Offres et négociations')
    COMPROMIS = 'compromis', _('Signature du compromis')
    PRET = 'pret', _('Obtention du prêt')
    ACTE_DEFINITIF = 'acte', _('Signature de l\'acte définitif')
    REMISE_CLES = 'remise_cles', _('Remise des clés')
    
    # Étapes pour la vente
    ESTIMATION = 'estimation', _('Estimation du bien')
    DIAGNOSTICS = 'diagnostics', _('Réalisation des diagnostics')
    VALORISATION = 'valorisation', _('Valorisation du bien')
    COMMERCIALISATION = 'commercialisation', _('Commercialisation')
    VISITES_VENTE = 'visites_vente', _('Organisation des visites')
    COMPROMIS_VENTE = 'compromis_vente', _('Signature du compromis')
    ACTE_VENTE = 'acte_vente', _('Signature de l\'acte de vente')
    SUIVI_APRES_VENTE = 'suivi_apres_vente', _('Suivi après-vente')

class TypeProfessionnel(models.Model):
    nom = models.CharField(max_length=100, verbose_name=_("Nom du type de professionnel"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text=_("Classe Font Awesome, ex: fa-user-tie"))
    
    class Meta:
        verbose_name = _("type de professionnel")
        verbose_name_plural = _("types de professionnels")
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class EtapeProjet(models.Model):
    type_etape = models.CharField(
        max_length=20,
        choices=TypeEtape.choices,
        verbose_name=_("Type d'étape")
    )
    type_projet = models.CharField(
        max_length=10,
        verbose_name=_("Type de projet")
    )
    ordre = models.PositiveIntegerField(verbose_name=_("Ordre d'affichage"))
    titre = models.CharField(max_length=100, verbose_name=_("Titre de l'étape"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    professionnels_associes = models.ManyToManyField(
        TypeProfessionnel,
        related_name='etapes',
        verbose_name=_("Types de professionnels associés"),
        blank=True
    )
    est_obligatoire = models.BooleanField(
        default=True,
        verbose_name=_("Étape obligatoire")
    )
    
    class Meta:
        verbose_name = _("étape de projet")
        verbose_name_plural = _("étapes de projet")
        ordering = ['type_projet', 'ordre']
        unique_together = ('type_etape', 'type_projet')
    
    def __str__(self):
        return f"{self.type_projet} - {self.titre}"

class ProjetImmobilier(models.Model):
    # Type de projet
    ACHAT = 'achat'
    VENTE = 'vente'
    
    # Type de bien
    MAISON = 'maison'
    APPARTEMENT = 'appartement'
    IMMEUBLE = 'immeuble'
    LOCAL_COMMERCIAL = 'local_commercial'
    TERRAIN = 'terrain'
    AUTRE = 'autre'
    
    # Type de travaux
    TRAVAUX_AMENAGEMENT = 'amenagement'
    TRAVAUX_DECO = 'deco'
    TRAVAUX_RENOVATION_LEGERE = 'renovation_legere'
    TRAVAUX_RENOVATION_COMPLETE = 'renovation_complete'
    
    # Choices constants
    TYPE_PROJET_CHOICES = [
        (ACHAT, 'Achat'),
        (VENTE, 'Vente')
    ]
    
    TYPE_BIEN_CHOICES = [
        (MAISON, 'Maison'),
        (APPARTEMENT, 'Appartement'),
        (IMMEUBLE, 'Immeuble'),
        (LOCAL_COMMERCIAL, 'Local commercial'),
        (TERRAIN, 'Terrain'),
        (AUTRE, 'Autre')
    ]
    
    TRAVAUX_CHOICES = [
        (TRAVAUX_AMENAGEMENT, 'Aménagement'),
        (TRAVAUX_DECO, 'Décoration'),
        (TRAVAUX_RENOVATION_LEGERE, 'Petite rénovation'),
        (TRAVAUX_RENOVATION_COMPLETE, 'Rénovation complète'),
    ]
    
    # Champs de base
    utilisateur = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='projets',
        verbose_name=_("Utilisateur")
    )
    type_projet = models.CharField(
        max_length=20, 
        choices=TYPE_PROJET_CHOICES,
        verbose_name=_("Type de projet")
    )
    type_bien = models.CharField(
        max_length=20, 
        choices=TYPE_BIEN_CHOICES,
        verbose_name=_("Type de bien")
    )
    
    # Champs communs
    nombre_pieces = models.PositiveIntegerField(
        verbose_name=_("Nombre de pièces"),
        null=True,
        blank=True
    )
    surface = models.PositiveIntegerField(
        verbose_name=_("Surface (m²)"),
        null=True,
        blank=True
    )
    surface_min = models.PositiveIntegerField(
        verbose_name=_("Surface minimale (m²)"),
        null=True,
        blank=True
    )
    surface_max = models.PositiveIntegerField(
        verbose_name=_("Surface maximale (m²)"),
        null=True,
        blank=True
    )
    secteur_geographique = models.CharField(
        max_length=255, 
        verbose_name=_("Secteur géographique"),
        blank=True,
        default=''
    )
    
    # Champs spécifiques à l'achat
    avec_exterieur = models.BooleanField(
        verbose_name=_("Avec extérieur"),
        default=False
    )
    surface_exterieur = models.PositiveIntegerField(
        verbose_name=_("Surface extérieure (m²)"),
        null=True,
        blank=True
    )
    avec_garage = models.BooleanField(
        verbose_name=_("Avec garage"),
        default=False
    )
    proximite_transports = models.TextField(
        verbose_name=_("Proximité des transports"),
        blank=True,
        help_text=_("Tram, métro, bus, gares à proximité")
    )
    budget_min = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_("Budget minimum (€)"),
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    budget_max = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_("Budget maximum (€)"),
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    travaux_envisages = models.CharField(
        max_length=20,
        choices=TRAVAUX_CHOICES,
        verbose_name=_("Travaux envisagés"),
        blank=True,
        null=True
    )
    
    # Champs spécifiques à la vente
    caracteristiques = models.TextField(
        verbose_name=_("Caractéristiques du bien"),
        blank=True,
        help_text=_("Jardin, balcon, garage, etc.")
    )
    date_achat = models.DateField(
        verbose_name=_("Date d'achat"),
        null=True,
        blank=True
    )
    exposition = models.CharField(
        max_length=100,
        verbose_name=_("Exposition"),
        blank=True,
        help_text=_("Exposition du jardin ou du séjour")
    )
    
    # Champs système
    description = models.TextField(
        verbose_name=_("Description complémentaire"),
        blank=True
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    professionnel_selectionne = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projets_selectionnes',
        verbose_name=_("Professionnel sélectionné"),
        help_text=_("Professionnel qui a été choisi pour ce projet")
    )
    
    class Meta:
        verbose_name = _("projet immobilier")
        verbose_name_plural = _("projets immobiliers")
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Projet {self.get_type_projet_display()} - {self.get_type_bien_display()} ({self.utilisateur.username})"
    
    # Champs pour la roadmap
    etape_actuelle = models.ForeignKey(
        EtapeProjet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projets_actuels',
        verbose_name=_("Étape actuelle")
    )
    
    def save(self, *args, **kwargs):
        # S'assurer que la surface max est supérieure ou égale à la surface min
        if all(hasattr(self, attr) for attr in ['surface_max', 'surface_min']):
            if self.surface_max is not None and self.surface_min is not None and self.surface_max < self.surface_min:
                self.surface_max = self.surface_min
        
        # Gestion des dates de création/mise à jour
        if not self.pk:  # Si c'est une création
            self.date_creation = timezone.now()
            is_new = True
        else:
            is_new = False
        
        self.date_mise_a_jour = timezone.now()
        
        # Sauvegarde de l'instance
        super().save(*args, **kwargs)
        
        # Initialisation de la roadmap pour les nouveaux projets
        if is_new and not hasattr(self, 'etapes_instance'):
            self.initialiser_roadmap()
    
    def initialiser_roadmap(self):
        # Récupérer toutes les étapes pour ce type de projet
        etapes = EtapeProjet.objects.filter(type_projet=self.type_projet).order_by('ordre')
        
        if not etapes.exists():
            return
        
        # Créer les instances d'étapes pour ce projet
        for etape in etapes:
            EtapeProjetInstance.objects.create(
                projet=self,
                etape=etape,
                statut=EtapeProjetInstance.STATUT_A_VENIR if etape.ordre > 1 else EtapeProjetInstance.STATUT_EN_COURS
            )
        
        # Définir la première étape comme étape actuelle
        if not self.etape_actuelle and etapes.exists():
            self.etape_actuelle = etapes.first()
            self.save(update_fields=['etape_actuelle'])
            
    def get_conversation_avec_professionnel(self):
        """Récupère la conversation associée à ce projet et au professionnel sélectionné"""
        if not self.professionnel_selectionne:
            return None
            
        try:
            return Conversation.objects.get(
                projet=self,
                professionnel=self.professionnel_selectionne,
                particulier=self.utilisateur
            )
        except Conversation.DoesNotExist:
            return None
    
    def avancer_etape(self):
        """Passe à l'étape suivante de la roadmap"""
        if not self.etape_actuelle:
            return False
            
        # Marquer l'étape actuelle comme terminée
        instance_etape = self.etapes_instance.get(etape=self.etape_actuelle)
        instance_etape.est_terminee = True
        instance_etape.date_fin = timezone.now()
        instance_etape.save()
        
        # Trouver la prochaine étape
        prochaine_etape = EtapeProjet.objects.filter(
            type_projet=self.type_projet,
            ordre__gt=self.etape_actuelle.ordre
        ).order_by('ordre').first()
        
        if prochaine_etape:
            self.etape_actuelle = prochaine_etape
            self.save(update_fields=['etape_actuelle'])
            return True
        return False
    
    def reculer_etape(self):
        """Revenir à l'étape précédente de la roadmap"""
        if not self.etape_actuelle:
            return False
            
        # Trouver l'étape précédente
        etape_precedente = EtapeProjet.objects.filter(
            type_projet=self.type_projet,
            ordre__lt=self.etape_actuelle.ordre
        ).order_by('-ordre').first()
        
        if etape_precedente:
            # Réinitialiser l'étape actuelle
            instance_etape = self.etapes_instance.get(etape=self.etape_actuelle)
            instance_etape.est_terminee = False
            instance_etape.date_fin = None
            instance_etape.save()
            
            # Définir l'étape précédente comme étape actuelle
            self.etape_actuelle = etape_precedente
            self.save(update_fields=['etape_actuelle'])
            return True
        return False
    
    def get_avancement(self):
        """Retourne le pourcentage d'avancement du projet"""
        if not hasattr(self, 'etapes_instance'):
            return 0
            
        etapes = self.etapes_instance.all()
        if not etapes.exists():
            return 0
            
        etapes_terminees = etapes.filter(est_terminee=True).count()
        return int((etapes_terminees / etapes.count()) * 100)
    
    def peut_avancer(self):
        """Vérifie si on peut passer à l'étape suivante"""
        if not self.etape_actuelle:
            return False
            
        # Vérifier s'il y a une étape suivante
        return EtapeProjet.objects.filter(
            type_projet=self.type_projet,
            ordre__gt=self.etape_actuelle.ordre
        ).exists()
    
    def peut_reculer(self):
        """Vérifie si on peut revenir à l'étape précédente"""
        if not self.etape_actuelle:
            return False
            
        # Vérifier s'il y a une étape précédente
        return EtapeProjet.objects.filter(
            type_projet=self.type_projet,
            ordre__lt=self.etape_actuelle.ordre
        ).exists()
    
    def get_prochain_professionnel(self):
        """Retourne le type de professionnel nécessaire pour l'étape actuelle"""
        if not self.etape_actuelle:
            return None
            
        professionnels = self.etape_actuelle.professionnels_associes.all()
        return professionnels.first() if professionnels.exists() else None
    def get_conversation_with(self, professionnel):
        """
        Récupère ou crée une conversation avec un professionnel spécifique
        """
        conversation, created = self.conversations.get_or_create(
            professionnel=professionnel,
            defaults={
                'particulier': self.utilisateur,
                'projet': self
            }
        )
        return conversation
        
    def etapes_terminees(self):
        """
        Retourne un queryset des étapes terminées pour ce projet
        """
        return EtapeProjet.objects.filter(
            instances__projet=self,
            instances__est_terminee=True
        )
        
    def get_etape_instance(self, etape):
        """
        Retourne l'instance d'une étape spécifique pour ce projet
        """
        try:
            return self.etapes_instance.get(etape=etape)
        except EtapeProjetInstance.DoesNotExist:
            return None


class ProfilProfessionnel(models.Model):
    """
    Modèle pour stocker les informations complémentaires des professionnels
    """
    class TypeEntreprise(models.TextChoices):
        AGENCE = 'agence', _('Agence immobilière')
        PROMOTEUR = 'promoteur', _('Promoteur immobilier')
        CONSTRUCTEUR = 'constructeur', _('Constructeur')
        AUTRE = 'autre', _('Autre')
    
    utilisateur = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profil_pro',
        verbose_name=_("Utilisateur")
    )
    
    # Informations sur l'entreprise
    type_entreprise = models.CharField(
        max_length=20, 
        choices=TypeEntreprise.choices,
        default=TypeEntreprise.AUTRE,
        verbose_name=_("Type d'entreprise")
    )
    nom_entreprise = models.CharField(
        max_length=100, 
        verbose_name=_("Nom de l'entreprise")
    )
    siret = models.CharField(
        max_length=14, 
        verbose_name=_('Numéro SIRET'),
        help_text=_('14 chiffres, sans espace'),
        blank=True
    )
    description = models.TextField(
        verbose_name=_("Description de l'activité"),
        blank=True
    )
    site_web = models.URLField(
        verbose_name=_('Site web'),
        blank=True
    )
    telephone = models.CharField(
        max_length=20,
        verbose_name=_('Téléphone professionnel'),
        blank=True
    )
    annee_creation = models.PositiveIntegerField(
        verbose_name=_("Année de création"),
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(2025)
        ],
        null=True,
        blank=True
    )
    adresse = models.TextField(
        verbose_name=_('Adresse du siège social'),
        blank=True
    )
    code_postal = models.CharField(
        max_length=10,
        verbose_name=_('Code postal'),
        blank=True
    )
    ville = models.CharField(
        max_length=100,
        verbose_name=_('Ville'),
        blank=True
    )
    logo = models.ImageField(
        upload_to='professionnels/logos/',
        verbose_name=_('Logo'),
        blank=True,
        null=True
    )
    cgu_acceptees = models.BooleanField(
        verbose_name=_("J'accepte les conditions générales d'utilisation"),
        default=False
    )
    date_creation = models.DateTimeField(
        auto_now_add=True
    )
    date_mise_a_jour = models.DateTimeField(
        auto_now=True
    )
    note_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("Note moyenne")
    )
    nombre_avis = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Nombre d'avis")
    )
    
    etapes_projet = models.ManyToManyField(
        'EtapeProjet',
        related_name='professionnels',
        verbose_name=_("Étapes de projet prises en charge"),
        help_text=_("Sélectionnez les étapes de projet pour lesquelles vous proposez vos services"),
        blank=True
    )

    class Meta:
        verbose_name = _("profil professionnel")
        verbose_name_plural = _("profils professionnels")
        ordering = ['nom_entreprise']
    
    def __str__(self):
        return f"{self.nom_entreprise} ({self.get_type_entreprise_display()})"
    
    @property
    def adresse_complete(self):
        return f"{self.adresse}, {self.code_postal} {self.ville}"


class Conversation(models.Model):
    """
    Modèle représentant une conversation entre utilisateurs
    à propos d'un projet immobilier spécifique.
    """
    projet = models.ForeignKey(
        'ProjetImmobilier',
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name=_("Projet concerné")
    )
    professionnel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_pro',
        verbose_name=_("Professionnel"),
        null=True,
        blank=True
    )
    particulier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations_particulier',
        verbose_name=_("Particulier"),
        default=1  # ID d'un utilisateur existant (à adapter selon votre base de données)
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    date_modification = models.DateTimeField(auto_now=True, verbose_name=_("Dernière mise à jour"))
    
    class Meta:
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        ordering = ['-date_modification']
        unique_together = ('projet', 'professionnel', 'particulier')
    
    def __str__(self):
        professionnel_nom = self.professionnel.get_full_name() or self.professionnel.username if self.professionnel else "Anonyme"
        return f"Conversation sur {self.projet} - {professionnel_nom} et {self.particulier}"
    
    def get_absolute_url(self):
        return reverse('immobilier:conversation_detail', args=[self.id])
    
    def get_other_user(self, user):
        """Retourne l'autre utilisateur de la conversation"""
        if user == self.professionnel:
            return self.particulier
        return self.professionnel
    
    @property
    def messages_by_date(self):
        """Organise les messages par date pour l'affichage"""
        messages_dict = {}
        for message in self.messages.all().order_by('date_creation'):
            date = message.date_creation.date()
            if date not in messages_dict:
                messages_dict[date] = []
            messages_dict[date].append(message)
        return messages_dict


class Message(models.Model):
    """
    Modèle représentant un message dans une conversation
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_("Conversation")
    )
    expediteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
        verbose_name=_("Expéditeur")
    )
    contenu = models.TextField(verbose_name=_("Message"))
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_("Date d'envoi"))
    lu = models.BooleanField(default=False, verbose_name=_("Message lu"))
    
    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Message de {self.expediteur} - {self.date_creation.strftime('%d/%m/%Y %H:%M')}"
    
    def marquer_comme_lu(self):
        if not self.lu:
            self.lu = True
            self.save(update_fields=['lu'])


class EtapeProjetInstance(models.Model):
    """Instance d'une étape pour un projet spécifique"""
    projet = models.ForeignKey(
        'ProjetImmobilier',
        on_delete=models.CASCADE,
        related_name='etapes_instance',
        verbose_name=_("Projet")
    )
    etape = models.ForeignKey(
        'EtapeProjet',
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name=_("Étape")
    )
    date_debut = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Date de début")
    )
    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin")
    )
    est_terminee = models.BooleanField(
        default=False,
        verbose_name=_("Étape terminée")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes sur l'étape")
    )
    
    class Meta:
        verbose_name = _("instance d'étape de projet")
        verbose_name_plural = _("instances d'étapes de projet")
        ordering = ['projet', 'etape__ordre']
        unique_together = ('projet', 'etape')
    
    def __str__(self):
        return f"{self.projet} - {self.etape.titre}"


class DocumentProfessionnel(models.Model):
    """
    Modèle pour stocker les documents des professionnels (KBIS, assurance, etc.)
    """
    class TypeDocument(models.TextChoices):
        KBIS = 'kbis', 'KBIS'
        ASSURANCE = 'assurance', _('Attestation d\'assurance')
        AUTRE = 'autre', _('Autre document')
    
    professionnel = models.ForeignKey(
        ProfilProfessionnel,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_("Professionnel")
    )
    type_document = models.CharField(
        max_length=20,
        choices=TypeDocument.choices,
        verbose_name=_("Type de document")
    )
    fichier = models.FileField(
        upload_to='professionnels/documents/',
        verbose_name=_('Fichier')
    )
    date_expiration = models.DateField(
        verbose_name=_("Date d'expiration"),
        null=True,
        blank=True
    )
    est_verifie = models.BooleanField(
        verbose_name=_('Document vérifié'),
        default=False
    )
    date_creation = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("document professionnel")
        verbose_name_plural = _("documents professionnels")
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.get_type_document_display()} - {self.professionnel.nom_entreprise}"
    
    @property
    def est_expire(self):
        if not self.date_expiration:
            return False
        from datetime import date
        return date.today() > self.date_expiration


class BienImmobilier(models.Model):
    TYPE_TRANSACTION = [
        ('vente', 'À vendre'),
        ('location', 'À louer'),
    ]

    titre = models.CharField(max_length=200, verbose_name=_("Titre"))
    description = models.TextField(verbose_name=_("Description"))
    type_bien = models.ForeignKey(
        TypeBien, 
        on_delete=models.CASCADE,
        verbose_name=_("Type de bien")
    )
    type_transaction = models.CharField(
        max_length=10, 
        choices=TYPE_TRANSACTION,
        verbose_name=_("Type de transaction")
    )
    prix = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name=_("Prix (€)")
    )
    surface = models.PositiveIntegerField(
        help_text=_("Surface en m²"),
        verbose_name=_("Surface")
    )
    nombre_pieces = models.PositiveIntegerField(verbose_name=_("Nombre de pièces"))
    adresse = models.CharField(max_length=255, verbose_name=_("Adresse"))
    code_postal = models.CharField(max_length=10, verbose_name=_("Code postal"))
    ville = models.CharField(max_length=100, verbose_name=_("Ville"))
    proprietaire = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='biens',
        verbose_name=_("Propriétaire")
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name=_("Dernière mise à jour"))
    disponible = models.BooleanField(default=True, verbose_name=_("Disponible"))
    image_principale = models.ImageField(
        upload_to='biens/', 
        blank=True, 
        null=True,
        verbose_name=_("Image principale")
    )

    def __str__(self):
        return f"{self.titre} - {self.get_type_transaction_display()} - {self.prix}€"

    class Meta:
        verbose_name = _("bien immobilier")
        verbose_name_plural = _("biens immobiliers")
        ordering = ['-date_creation']
        permissions = [
            ('publish_bien', _('Peut publier un bien')),
            ('unpublish_bien', _('Peut retirer un bien de la publication')),
        ]
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('immobilier:detail_bien', args=[str(self.id)])
    
    @property
    def est_a_vendre(self):
        return self.type_transaction == 'vente'
    
    @property
    def est_a_louer(self):
        return self.type_transaction == 'location'
    
    @property
    def prix_formate(self):
        if self.est_a_louer:
            return f"{self.prix} €/mois"
        return f"{self.prix} €"
