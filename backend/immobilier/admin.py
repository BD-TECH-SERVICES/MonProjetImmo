from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    User, ProfilParticulier, ProfilProfessionnel, TypeBien, 
    BienImmobilier, Conversation, Message, DocumentProfessionnel, ProjetImmobilier
)

# Enregistrement du modèle utilisateur personnalisé
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'profil_complet')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone', 'address')}),
        ('Type et autorisations', {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def profil_complet(self, obj):
        return obj.profil_complet
    profil_complet.boolean = True
    profil_complet.short_description = 'Profil complet'

@admin.register(ProfilParticulier)
class ProfilParticulierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'civilite', 'date_naissance', 'situation_familiale', 'nombre_enfants')
    list_filter = ('civilite', 'situation_familiale')
    search_fields = ('utilisateur__first_name', 'utilisateur__last_name', 'utilisateur__email')
    raw_id_fields = ('utilisateur',)
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    fieldsets = (
        ('Utilisateur', {'fields': ('utilisateur',)}),
        ('Informations personnelles', {
            'fields': (
                'civilite', 'date_naissance', 'situation_familiale', 
                'nombre_enfants', 'profession', 'revenu_mensuel'
            )
        }),
        ('Préférences', {
            'fields': ('notification_email', 'notification_sms')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_mise_a_jour'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProfilProfessionnel)
class ProfilProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'utilisateur', 'type_entreprise', 'ville', 'cgu_acceptees')
    list_filter = ('type_entreprise', 'cgu_acceptees')
    search_fields = ('nom_entreprise', 'utilisateur__first_name', 'utilisateur__last_name', 'siret')
    raw_id_fields = ('utilisateur',)
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    fieldsets = (
        ('Utilisateur', {'fields': ('utilisateur',)}),
        ('Informations entreprise', {
            'fields': (
                'type_entreprise', 'nom_entreprise', 'siret', 'description',
                'site_web', 'annee_creation', 'logo'
            )
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'code_postal', 'ville', 'telephone')
        }),
        ('Statistiques', {
            'fields': ('note_moyenne', 'nombre_avis')
        }),
        ('CGU', {
            'fields': ('cgu_acceptees',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_mise_a_jour'),
            'classes': ('collapse',)
        }),
    )

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('expediteur', 'contenu', 'date_creation', 'lu')
    fields = ('expediteur', 'contenu', 'date_creation', 'lu')
    ordering = ('-date_creation',)
    can_delete = False
    max_num = 20
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_projet', 'get_particulier', 'get_professionnel', 'nb_messages', 'nb_non_lus', 'date_creation', 'date_modification')
    list_filter = ('date_creation', 'date_modification')
    search_fields = (
        'projet__titre',
        'particulier__first_name',
        'particulier__last_name',
        'particulier__email',
        'professionnel__first_name',
        'professionnel__last_name',
        'professionnel__email',
        'professionnel__profil_pro__nom_entreprise'
    )
    raw_id_fields = ('projet', 'particulier', 'professionnel')
    readonly_fields = ('date_creation', 'date_modification', 'nb_messages', 'nb_non_lus')
    inlines = [MessageInline]
    
    fieldsets = (
        ('Informations de la conversation', {
            'fields': ('projet', 'particulier', 'professionnel', 'date_creation', 'date_modification')
        }),
        ('Statistiques', {
            'fields': ('nb_messages', 'nb_non_lus'),
        }),
    )
    
    def get_projet(self, obj):
        return format_html('<a href="/admin/immobilier/projetimmobilier/{}/change/">{}</a>',
                         obj.projet.id, str(obj.projet))
    get_projet.short_description = 'Projet'
    get_projet.admin_order_field = 'projet__id'
    
    def get_particulier(self, obj):
        return format_html('<a href="/admin/immobilier/user/{}/change/">{} ({})</a>',
                         obj.particulier.id,
                         obj.particulier.get_full_name() or obj.particulier.username,
                         obj.particulier.email)
    get_particulier.short_description = 'Particulier'
    get_particulier.admin_order_field = 'particulier__username'
    
    def get_professionnel(self, obj):
        if obj.professionnel:
            try:
                nom_entreprise = obj.professionnel.profil_pro.nom_entreprise
                return format_html('<a href="/admin/immobilier/user/{}/change/">{} - {} ({})</a>',
                             obj.professionnel.id,
                             obj.professionnel.get_full_name() or obj.professionnel.username,
                             nom_entreprise,
                             obj.professionnel.email)
            except:
                return format_html('<a href="/admin/immobilier/user/{}/change/">{} ({})</a>',
                             obj.professionnel.id,
                             obj.professionnel.get_full_name() or obj.professionnel.username,
                             obj.professionnel.email)
        return '-'
    get_professionnel.short_description = 'Professionnel'
    get_professionnel.admin_order_field = 'professionnel__username'
    
    def nb_messages(self, obj):
        count = obj.messages.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)
    nb_messages.short_description = 'Nombre de messages'
    
    def nb_non_lus(self, obj):
        count = obj.messages.filter(lu=False).count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', count)
        return '0'
    nb_non_lus.short_description = 'Messages non lus'

# Définition des actions d'administration pour les messages
def marquer_comme_lus(modeladmin, request, queryset):
    updated = queryset.update(lu=True)
    modeladmin.message_user(request, f"{updated} message(s) marqué(s) comme lu(s)")
marquer_comme_lus.short_description = "Marquer les messages sélectionnés comme lus"


def marquer_comme_non_lus(modeladmin, request, queryset):
    updated = queryset.update(lu=False)
    modeladmin.message_user(request, f"{updated} message(s) marqué(s) comme non lu(s)")
marquer_comme_non_lus.short_description = "Marquer les messages sélectionnés comme non lus"


# Enregistrement du modèle Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_conversation', 'get_expediteur', 'apercu_contenu', 'date_creation', 'lu')
    list_filter = ('lu', 'date_creation', 'expediteur__user_type')
    search_fields = ('contenu', 'expediteur__username', 'expediteur__email', 'expediteur__first_name', 'expediteur__last_name')
    raw_id_fields = ('conversation', 'expediteur')
    readonly_fields = ('date_creation', 'get_projet', 'get_particulier', 'get_professionnel')
    list_editable = ('lu',)
    date_hierarchy = 'date_creation'
    actions = [marquer_comme_lus, marquer_comme_non_lus]
    
    fieldsets = (
        ('Informations du message', {
            'fields': ('conversation', 'expediteur', 'contenu', 'lu', 'date_creation')
        }),
        ('Détails de la conversation', {
            'fields': ('get_projet', 'get_particulier', 'get_professionnel'),
            'classes': ('collapse',)
        }),
    )
    
    def get_conversation(self, obj):
        return format_html('<a href="/admin/immobilier/conversation/{}/change/">{}</a>',
                         obj.conversation.id, obj.conversation.id)
    get_conversation.short_description = 'Conversation'
    get_conversation.admin_order_field = 'conversation__id'
    
    def get_expediteur(self, obj):
        user_type = obj.expediteur.get_user_type_display()
        return format_html('{} <span style="color: {}; font-weight: bold;">({})</span>',
                         obj.expediteur.get_full_name() or obj.expediteur.username,
                         'blue' if obj.expediteur.user_type == 'professionnel' else 'green',
                         user_type)
    get_expediteur.short_description = 'Expéditeur'
    get_expediteur.admin_order_field = 'expediteur__username'
    
    def apercu_contenu(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    apercu_contenu.short_description = 'Message'
    
    def get_projet(self, obj):
        projet = obj.conversation.projet
        return format_html('<a href="/admin/immobilier/projetimmobilier/{}/change/">{}</a>',
                         projet.id, str(projet))
    get_projet.short_description = 'Projet associé'
    
    def get_particulier(self, obj):
        particulier = obj.conversation.particulier
        return format_html('{} ({})',
                         particulier.get_full_name() or particulier.username,
                         particulier.email)
    get_particulier.short_description = 'Particulier'
    
    def get_professionnel(self, obj):
        professionnel = obj.conversation.professionnel
        if professionnel:
            try:
                nom_entreprise = professionnel.profil_pro.nom_entreprise
                return format_html('{} - {} ({})',
                             professionnel.get_full_name() or professionnel.username,
                             nom_entreprise,
                             professionnel.email)
            except:
                return format_html('{} ({})',
                             professionnel.get_full_name() or professionnel.username,
                             professionnel.email)
        return '-'
    get_professionnel.short_description = 'Professionnel'

@admin.register(DocumentProfessionnel)
class DocumentProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_professionnel', 'type_document', 'date_creation', 'est_verifie', 'est_expire')
    list_filter = ('type_document', 'est_verifie', 'date_creation')
    search_fields = ('professionnel__nom_entreprise', 'professionnel__utilisateur__username')
    raw_id_fields = ('professionnel',)
    readonly_fields = ('date_creation',)
    
    def get_professionnel(self, obj):
        return obj.professionnel.nom_entreprise
    get_professionnel.short_description = 'Professionnel'
    
    def est_expire(self, obj):
        return obj.est_expire()
    est_expire.boolean = True
    est_expire.short_description = 'Expiré'

@admin.register(TypeBien)
class TypeBienAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'icone')
    search_fields = ('nom', 'description')
    list_editable = ('icone',)

@admin.register(BienImmobilier)
class BienImmobilierAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_bien', 'type_transaction', 'prix', 'ville', 'disponible', 'get_proprietaire')
    list_filter = ('type_bien', 'type_transaction', 'disponible')
    search_fields = ('titre', 'ville', 'adresse', 'proprietaire__username', 'proprietaire__email')
    list_editable = ('disponible',)
    raw_id_fields = ('proprietaire', 'type_bien')
    readonly_fields = ('date_creation', 'date_mise_a_jour')
    
    def get_proprietaire(self, obj):
        return obj.proprietaire.get_full_name() or obj.proprietaire.username
    get_proprietaire.short_description = 'Propriétaire'

@admin.register(ProjetImmobilier)
class ProjetImmobilierAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_utilisateur', 'type_projet', 'type_bien', 'get_budget_display', 'get_etape_actuelle', 'avancement_barre')
    list_filter = ('type_projet', 'type_bien', 'date_creation')
    search_fields = ('titre', 'description', 'utilisateur__username', 'utilisateur__email', 'professionnel_selectionne__username')
    raw_id_fields = ('utilisateur', 'professionnel_selectionne')
    readonly_fields = ('date_creation', 'date_mise_a_jour', 'avancement_barre', 'afficher_etape_actuelle', 'afficher_professionnel')
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'utilisateur', 'type_projet', 'type_bien')
        }),
        ('Détails', {
            'fields': ('budget_min', 'budget_max', 'surface_min', 'surface_max', 'secteur_geographique')
        }),
        ('Suivi du projet', {
            'fields': ('etape_actuelle', 'afficher_etape_actuelle', 'avancement_barre'),
            'classes': ('collapse',)
        }),
        ('Professionnel associé', {
            'fields': ('professionnel_selectionne', 'afficher_professionnel'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_mise_a_jour'),
            'classes': ('collapse',)
        }),
    )
    
    def get_utilisateur(self, obj):
        return f"{obj.utilisateur.get_full_name() or obj.utilisateur.username}"
    get_utilisateur.short_description = 'Utilisateur'
    get_utilisateur.admin_order_field = 'utilisateur__username'
    
    def get_etape_actuelle(self, obj):
        if obj.etape_actuelle:
            return obj.etape_actuelle.titre
        return "Non démarré"
    get_etape_actuelle.short_description = 'Étape actuelle'
    
    def afficher_etape_actuelle(self, obj):
        if obj.etape_actuelle:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<p><strong>Description:</strong> {}</p>'
                '<p><strong>Professionnels associés:</strong> {}</p>'
                '</div>',
                obj.etape_actuelle.description or 'Aucune description',
                ", ".join([p.nom for p in obj.etape_actuelle.professionnels_associes.all()]) or 'Aucun'
            )
        return "Aucune étape en cours"
    afficher_etape_actuelle.short_description = 'Détails de l\'étape'
    afficher_etape_actuelle.allow_tags = True
    
    def avancement_barre(self, obj):
        pourcentage = obj.get_avancement()
        return format_html(
            '<div style="width:100%; background-color:#e0e0e0; border-radius:5px; margin:5px 0;">'
            '<div style="width:{}%; background-color:#4CAF50; color:white; text-align:center; padding:2px 0; border-radius:5px;" '
            'title="{}%">{}%</div></div>',
            pourcentage, pourcentage, pourcentage
        )
    avancement_barre.short_description = 'Avancement'
    avancement_barre.allow_tags = True
    
    def get_budget_display(self, obj):
        if obj.budget_min is not None and obj.budget_max is not None:
            return f"{obj.budget_min}€ - {obj.budget_max}€"
        elif obj.budget_min is not None:
            return f"À partir de {obj.budget_min}€"
        elif obj.budget_max is not None:
            return f"Jusqu'à {obj.budget_max}€"
        return "Non spécifié"
    get_budget_display.short_description = 'Budget'
    get_budget_display.admin_order_field = 'budget_min'

    def get_professionnel(self, obj):
        if obj.professionnel_selectionne:
            return obj.professionnel_selectionne.get_full_name() or obj.professionnel_selectionne.username
        return "Aucun"
    get_professionnel.short_description = 'Professionnel associé'
    get_professionnel.admin_order_field = 'professionnel_selectionne__username'
    
    def afficher_professionnel(self, obj):
        if obj.professionnel_selectionne and hasattr(obj.professionnel_selectionne, 'profilprofessionnel'):
            pro = obj.professionnel_selectionne.profilprofessionnel
            return format_html(
                '<div style="margin: 10px 0;">'
                '<p><strong>Entreprise:</strong> {}</p>'
                '<p><strong>Téléphone:</strong> {}</p>'
                '<p><strong>Email:</strong> {}</p>'
                '</div>',
                pro.nom_entreprise,
                pro.telephone or 'Non renseigné',
                obj.professionnel_selectionne.email
            )
        return "Aucun professionnel associé"
    afficher_professionnel.short_description = 'Détails du professionnel'
    afficher_professionnel.allow_tags = True
