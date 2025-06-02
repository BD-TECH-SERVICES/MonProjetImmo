from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, FormView, RedirectView, TemplateView
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout
from .forms_auth import UserRegistrationForm, UserLoginForm
from .models import ProjetImmobilier

from .models import ProfilProfessionnel

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy('immobilier:redirection_apres_inscription')
    user_type = 'particulier'  # Valeur par défaut
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Récupérer le user_type des arguments de l'URL
        self.user_type = kwargs.get('user_type', 'particulier')
    
    def get_template_names(self):
        if self.user_type == 'professionnel':
            return ['immobilier/auth/register_professionnel.html']
        return ['immobilier/auth/register_particulier.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.user_type
        return context
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_type'] = self.user_type
        return kwargs

    def form_valid(self, form):
        try:
            # Sauvegarder l'utilisateur avec le formulaire
            self.object = form.save(commit=False)
            self.object.user_type = self.user_type
            self.object.save()
            
            # Si l'utilisateur est un professionnel, créer automatiquement un profil
            if self.user_type == 'professionnel':
                # Créer le profil professionnel
                profil = ProfilProfessionnel.objects.create(
                    utilisateur=self.object,
                    type_entreprise=form.cleaned_data.get('type_entreprise', 'autre'),
                    nom_entreprise=form.cleaned_data.get('nom_entreprise', ''),
                    siret=form.cleaned_data.get('siret', ''),
                    telephone=form.cleaned_data.get('telephone', ''),
                    adresse=form.cleaned_data.get('adresse', ''),
                    code_postal=form.cleaned_data.get('code_postal', ''),
                    ville=form.cleaned_data.get('ville', ''),
                    description=form.cleaned_data.get('description', ''),
                    site_web=form.cleaned_data.get('site_web', '')
                )
                
                # Ajouter les étapes de projet sélectionnées pour l'achat et la vente
                etapes_selectionnees = []
                if 'etapes_achat' in form.cleaned_data:
                    etapes_selectionnees.extend(form.cleaned_data['etapes_achat'])
                if 'etapes_vente' in form.cleaned_data:
                    etapes_selectionnees.extend(form.cleaned_data['etapes_vente'])
                
                # Enregistrer toutes les étapes sélectionnées
                if etapes_selectionnees:
                    profil.etapes_projet.set(etapes_selectionnees)
            
            # Connecter l'utilisateur
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            
            user = authenticate(
                username=email,
                password=password
            )
            
            if user is not None:
                login(self.request, user)
                messages.success(self.request, _("Inscription réussie ! Bienvenue sur notre plateforme."))
                
                # Rediriger directement vers la création de projet pour les particuliers
                if self.user_type == 'particulier':
                    return redirect('immobilier:creer_projet')
                # Pour les professionnels, on suit le flux normal
                return redirect('immobilier:redirection_apres_inscription')
                
        except Exception as e:
            messages.error(self.request, _("Une erreur est survenue lors de votre inscription. Veuillez réessayer."))
            
        # En cas d'erreur, on reste sur le formulaire avec les erreurs
        return self.form_invalid(form)


def redirection_apres_inscription(request):
    """
    Redirige l'utilisateur vers la page appropriée après inscription
    """
    if not request.user.is_authenticated:
        return redirect('immobilier:login')
    
    if request.user.user_type == 'particulier':
        # Vérifier si l'utilisateur a déjà un projet
        if not ProjetImmobilier.objects.filter(utilisateur=request.user).exists():
            messages.info(request, _("Créez votre premier projet immobilier pour commencer."))
            return redirect('immobilier:creer_projet')
        return redirect('immobilier:espace_particulier')
    else:
        # Redirection pour les professionnels
        if hasattr(request.user, 'profil_pro'):
            return redirect('immobilier:espace_professionnel')
        messages.info(request, _("Complétez votre profil professionnel pour commencer."))
        return redirect('immobilier:creer_profil_pro')

class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'immobilier/auth/login.html'
    success_url = reverse_lazy('immobilier:accueil')

    def get_success_url(self):
        """Détermine l'URL de redirection après une connexion réussie."""
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and not next_url.startswith('/admin/'):
            return next_url
        return str(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        remember_me = form.cleaned_data.get('remember_me', False)
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            
            # Récupération de l'URL de redirection
            next_url = self.request.GET.get('next', '')
            
            # Gestion du "Se souvenir de moi"
            if remember_me:
                self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 jours
                if next_url and '/admin/' in next_url:
                    next_url = None
            
            # Si une URL de redirection valide est spécifiée, on y redirige
            if next_url and not next_url.startswith(reverse_lazy('admin:login')):
                return redirect(next_url)
            
            # Sinon, on redirige selon le type d'utilisateur
            if user.user_type == 'particulier':
                return redirect('immobilier:espace_particulier')
            else:
                return redirect('immobilier:espace_professionnel')
        else:
            messages.error(self.request, _("Identifiants invalides."))
            return self.form_invalid(form)

from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

@require_http_methods(["GET", "POST"])
@never_cache
def logout_view(request):
    """
    Vue personnalisée pour la déconnexion.
    Déconnecte l'utilisateur et le redirige vers la page d'accueil.
    """
    # Ajouter un message de succès avant la déconnexion (car la session sera effacée)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    
    # Déconnecter l'utilisateur
    auth_logout(request)
    
    # Rediriger vers la page d'accueil
    response = redirect(reverse('immobilier:accueil'))
    
    # Supprimer le cookie de session
    if 'sessionid' in request.COOKIES:
        response.delete_cookie('sessionid')
    
    return response
