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


# 🔹 Gestion améliorée des Projets
@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'get_utilisateur', 'date_creation', 'metier')
    search_fields = ('titre', 'utilisateur__nom', 'metier')
    list_filter = ('date_creation', 'metier')

    def get_utilisateur(self, obj):
        """ Vérifie si l'utilisateur est bien lié à un particulier """
        return obj.utilisateur.nom if obj.utilisateur else "Aucun"
    
    def get_date_creation(self, obj):
        """ Vérifie que la date est bien récupérée """
        return obj.date_creation.strftime("%d %b %Y") if obj.date_creation else "Non défini"
    get_date_creation.short_description = "Date de création"


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['get_professionnel']

    def get_professionnel(self, obj):
        """ Récupère le professionnel associé """
        return obj.professionnel if obj.professionnel else "Non défini"
    get_professionnel.short_description = "Professionnel"
    

from django.utils.html import format_html
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read', 'conversation_link')
    list_filter = ('sender', 'receiver', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'content')

    def conversation_link(self, obj):
        """ Lien pour voir les messages d'une conversation """
        return format_html('<a href="/admin/chat/message/?q={}">Voir</a>', obj.conversation_id)

    conversation_link.short_description = "Conversation"

admin.site.register(Message, MessageAdmin)
