from django.contrib import admin
from .models import *


# Inline pour afficher/éditer un profil Particulier
class ParticulierInline(admin.StackedInline):
    model = Particulier
    can_delete = False
    verbose_name = "Profil Particulier"
    verbose_name_plural = "Profil Particulier"
    extra = 0  # Ne pas afficher de formulaire supplémentaire par défaut


# Inline pour afficher/éditer un profil Professionnel
class ProfessionnelInline(admin.StackedInline):
    model = Professionnel
    can_delete = False
    verbose_name = "Profil Professionnel"
    verbose_name_plural = "Profil Professionnel"
    extra = 0  # Ne pas afficher de formulaire supplémentaire par défaut


# Personnalisation de l'administration des utilisateurs
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('username', 'email')

    def get_inline_instances(self, request, obj=None):
        """
        Affiche uniquement les inlines correspondant au type d'utilisateur.
        """
        inlines = []
        if obj:  # Vérifie si un utilisateur est édité
            if obj.user_type == 'particulier':
                inlines.append(ParticulierInline(self.model, self.admin_site))
            elif obj.user_type == 'professionnel':
                inlines.append(ProfessionnelInline(self.model, self.admin_site))
        return inlines


# Enregistrement des autres modèles
@admin.register(Particulier)
class ParticulierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'user')


@admin.register(Professionnel)
class ProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('nom_societe', 'email_pro', 'secteur_activite', 'user')


@admin.register(Projet)   
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'date_creation')
    search_fields = ('titre', 'utilisateur__nom')
    list_filter = ('date_creation',)

@admin.register(Carte)
class CarteAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'date_creation')
    filter_horizontal = ('projets',)  # Permet d'afficher un widget pour sélectionner les projets liés
    search_fields = ('titre', 'utilisateur__nom')
    list_filter = ('date_creation',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('professionnel',)
    filter_horizontal = ('cartes',)