from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views
from .views_auth import RegisterView, LoginView, logout_view, redirection_apres_inscription
from .views_espace import (
    EspaceParticulierView, CreerProjetView, ModifierProjetView, 
    SupprimerProjetView, ConversationsView, ChangerEtapeProjetView
)
from .views_chat import (
    ListeConversationsView, ConversationDetailView,
    NouvelleConversationView, ListeProfessionnelsView
)
from .views_pro import (
    EspaceProfessionnelView, CreerProfilProfessionnelView, 
    ModifierProfilProfessionnelView, GestionDocumentsView, 
    ajouter_document, supprimer_document
)
from .views_profile import profile_view, change_password
from .views_projets import ListeProjetsProfessionnelView, ContacterParticulierView
from .views_projet_detail import DetailProjetView, ChangerEtapeView
from .views_biens import GestionBiensView, CreerBienView, ModifierBienView, SupprimerBienView
from .views_projets import ChargerEtapesView
from .views_questionnaires import QuestionnaireAchatView, QuestionnaireVenteView

app_name = 'immobilier'

urlpatterns = [
    # Pages publiques
    path('', views.accueil, name='accueil'),
    path('biens/', views.ListeBiensView.as_view(), name='liste_biens'),
    path('bien/<int:pk>/', views.DetailBienView.as_view(), name='detail_bien'),
    
    # Authentification
    path('inscription/', views.RegisterChoiceView.as_view(), name='register_choice'),
    path('inscription/particulier/', RegisterView.as_view(), {'user_type': 'particulier'}, name='register_particulier'),
    path('inscription/professionnel/', RegisterView.as_view(), {'user_type': 'professionnel'}, name='register_professionnel'),
    path('connexion/', LoginView.as_view(), name='login'),
    path('connection/', LoginView.as_view(), name='login'),  # Alias pour /connection/
    path('deconnexion/', logout_view, name='logout'),
    
    # Redirection après inscription
    path('redirection/', redirection_apres_inscription, name='redirection_apres_inscription'),
    
    # Pages protégées
    path('bien/ajouter/', login_required(views.CreerBienView.as_view()), name='creer_bien'),
    path('bien/<int:pk>/modifier/', login_required(views.ModifierBienView.as_view()), name='modifier_bien'),
    path('bien/<int:pk>/supprimer/', login_required(views.SupprimerBienView.as_view()), name='supprimer_bien'),
    
    # Gestion des étapes de projet
    path('projet/charger_etapes/', login_required(ChargerEtapesView.as_view()), name='charger_etapes'),
    
    # Gestion des biens
    path('mes-biens/', login_required(GestionBiensView.as_view()), name='gestion_biens'),
    path('bien/ajouter/', login_required(CreerBienView.as_view()), name='creer_bien'),
    path('bien/<int:pk>/modifier/', login_required(ModifierBienView.as_view()), name='modifier_bien'),
    path('bien/<int:pk>/supprimer/', login_required(SupprimerBienView.as_view()), name='supprimer_bien'),
    
    # Espace particulier
    path('mon-espace/', login_required(EspaceParticulierView.as_view()), name='espace_particulier'),
    path('projets/', login_required(EspaceParticulierView.as_view()), name='espace_particulier'),
    path('projet/creer/', login_required(CreerProjetView.as_view()), name='creer_projet'),
    
    # Questionnaires
    path('projet/questionnaire/achat/', login_required(QuestionnaireAchatView.as_view()), name='questionnaire_achat'),
    path('projet/questionnaire/vente/', login_required(QuestionnaireVenteView.as_view()), name='questionnaire_vente'),
    
    path('projet/<int:pk>/modifier/', login_required(ModifierProjetView.as_view()), name='modifier_projet'),
    path('projet/<int:pk>/', login_required(DetailProjetView.as_view(template_name='immobilier/espace_particulier/detail_projet.html')), name='detail_projet'),
    path('projet/<int:pk>/supprimer/', login_required(SupprimerProjetView.as_view()), name='supprimer_projet'),
    
    # Chat et Messagerie
    path('messages/', login_required(ListeConversationsView.as_view()), name='liste_conversations'),
    path('messages/nouveau/<int:projet_id>/', login_required(NouvelleConversationView.as_view()), name='nouvelle_conversation'),
    path('messages/choisir-professionnel/<int:projet_id>/', login_required(ListeProfessionnelsView.as_view()), name='choisir_professionnel'),
    path('messages/conversation/<int:pk>/', login_required(ConversationDetailView.as_view()), name='conversation_detail'),
    
    # Projets pour les professionnels
    path('professionnel/projets/', login_required(ListeProjetsProfessionnelView.as_view()), name='liste_projets_pro'),
    path('professionnel/projet/<int:projet_id>/contacter/', login_required(ContacterParticulierView.as_view()), name='contacter_particulier'),
    path('projet/<int:pk>/changer-etape/', login_required(ChangerEtapeProjetView.as_view()), name='changer_etape'),
    
    # Profil utilisateur
    path('mon-profil/', login_required(profile_view), name='profile'),
    path('mon-profil/changer-mot-de-passe/', login_required(change_password), name='change_password'),
    
    # Espace professionnel
    path('professionnel/', login_required(EspaceProfessionnelView.as_view()), name='espace_professionnel'),
    path('professionnel/profil/creer/', login_required(CreerProfilProfessionnelView.as_view()), name='creer_profil_pro'),
    path('professionnel/profil/modifier/', login_required(ModifierProfilProfessionnelView.as_view()), name='modifier_profil_pro'),
    path('professionnel/documents/', login_required(GestionDocumentsView.as_view()), name='gestion_documents'),
    path('professionnel/documents/ajouter/', login_required(ajouter_document), name='ajouter_document'),
    path('professionnel/documents/<int:pk>/supprimer/', login_required(supprimer_document), name='supprimer_document'),
    
    # Espace admin
    path('admin/', include('django.contrib.auth.urls')),
    
    # Réinitialisation de mot de passe
    path('reinitialisation/mot-de-passe/',
         auth_views.PasswordResetView.as_view(
             template_name='immobilier/auth/password_reset.html',
             email_template_name='immobilier/auth/password_reset_email.html',
             subject_template_name='immobilier/auth/password_reset_subject.txt',
             success_url='/reinitialisation/mot-de-passe/envoye/'
         ),
         name='password_reset'),
    path('reinitialisation/mot-de-passe/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='immobilier/auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reinitialisation/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='immobilier/auth/password_reset_confirm.html',
             success_url='/reinitialisation/reinitialisation-terminee/'
         ),
         name='password_reset_confirm'),
    path('reinitialisation/reinitialisation-terminee/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='immobilier/auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
