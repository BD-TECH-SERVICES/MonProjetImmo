from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db import transaction

from .models import ProfilProfessionnel, DocumentProfessionnel
from .forms_pro import ProfilProfessionnelForm, DocumentProfessionnelForm

class ProfessionnelRequiredMixin(UserPassesTestMixin):
    """Vérifie que l'utilisateur est un professionnel"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'professionnel'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.warning(self.request, _("Veuillez vous connecter pour accéder à cette page."))
            return redirect('login')
        messages.warning(self.request, _("Accès réservé aux professionnels."))
        return redirect('espace_particulier')

class EspaceProfessionnelView(LoginRequiredMixin, ProfessionnelRequiredMixin, TemplateView):
    template_name = 'immobilier/espace_professionnel/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer le profil professionnel
        profil = getattr(user, 'profil_pro', None)
        context['profil'] = profil
        
        # Calculer le pourcentage de complétion du profil
        completion = 0
        if profil:
            completion = 50  # Valeur de base pour avoir un profil
            if profil.telephone:
                completion += 10
            if profil.adresse:
                completion += 10
            if profil.description:
                completion += 10
            if profil.site_web:
                completion += 5
            if profil.logo:
                completion += 15
            
            # Vérifier les documents
            documents_count = profil.documents.count()
            if documents_count > 0:
                completion += min(10, documents_count * 3)  # Max 10% pour les documents
        
        context['completion_percentage'] = min(100, completion)
        
        # Statistiques (valeurs factices pour l'exemple)
        context.update({
            'unread_messages_count': 3,  # À remplacer par une vraie requête
            'biens_count': 5,            # À remplacer par une vraie requête
            'avis_count': 2,             # À remplacer par une vraie requête
            'vues_profil': 124,
            'vues_profil_pourcentage': 62,
            'contacts_count': 18,
            'contacts_pourcentage': 75,
            'taux_reponse': 85,
            'documents_a_verifier': False,  # À remplacer par une vraie vérification
        })
        
        # Dernières activités (exemple)
        from datetime import datetime, timedelta
        
        context['activites'] = [
            {
                'icone': 'fa-envelope',
                'description': 'Nouveau message de Jean Dupont concernant une maison à Paris',
                'date': datetime.now() - timedelta(hours=2)  # Il y a 2 heures
            },
            {
                'icone': 'fa-home',
                'description': 'Votre annonce "Belle maison avec jardin" a été publiée',
                'date': datetime.now() - timedelta(days=2)  # Il y a 2 jours
            },
            {
                'icone': 'fa-star',
                'description': 'Nouvel avis reçu de Marie Martin',
                'date': datetime.now() - timedelta(days=4)  # Il y a 4 jours
            }
        ]
        
        return context

class CreerProfilProfessionnelView(LoginRequiredMixin, CreateView):
    model = ProfilProfessionnel
    form_class = ProfilProfessionnelForm
    template_name = 'immobilier/espace_professionnel/creer_profil.html'
    success_url = reverse_lazy('espace_professionnel')
    
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profil_pro'):
            return redirect('modifier_profil_pro')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        messages.success(self.request, _("Votre profil professionnel a été créé avec succès !"))
        return super().form_valid(form)

class ModifierProfilProfessionnelView(LoginRequiredMixin, UpdateView):
    model = ProfilProfessionnel
    form_class = ProfilProfessionnelForm
    template_name = 'immobilier/espace_professionnel/modifier_profil.html'
    success_url = reverse_lazy('espace_professionnel')
    
    def get_queryset(self):
        return ProfilProfessionnel.objects.filter(utilisateur=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, _("Votre profil a été mis à jour avec succès !"))
        return super().form_valid(form)

class GestionDocumentsView(LoginRequiredMixin, ProfessionnelRequiredMixin, ListView):
    model = DocumentProfessionnel
    template_name = 'immobilier/espace_professionnel/gestion_documents.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        return DocumentProfessionnel.objects.filter(
            professionnel__utilisateur=self.request.user
        ).select_related('professionnel')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DocumentProfessionnelForm()
        return context

def ajouter_document(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profil_pro'):
        return JsonResponse(
            {'success': False, 'message': _("Accès refusé.")}, 
            status=403
        )
    
    if request.method == 'POST':
        form = DocumentProfessionnelForm(
            request.POST, 
            request.FILES, 
            initial={'professionnel': request.user.profil_pro}
        )
        
        if form.is_valid():
            document = form.save(commit=False)
            document.professionnel = request.user.profil_pro
            document.save()
            return JsonResponse({
                'success': True,
                'message': _("Document ajouté avec succès !")
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse(
        {'success': False, 'message': _("Méthode non autorisée.")}, 
        status=405
    )

def supprimer_document(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'success': False, 'message': _("Accès refusé.")}, 
            status=403
        )
    
    document = get_object_or_404(
        DocumentProfessionnel, 
        pk=pk, 
        professionnel__utilisateur=request.user
    )
    
    if request.method == 'DELETE':
        document.delete()
        return JsonResponse({
            'success': True,
            'message': _("Document supprimé avec succès !")
        })
    
    return JsonResponse(
        {'success': False, 'message': _("Méthode non autorisée.")}, 
        status=405
    )
