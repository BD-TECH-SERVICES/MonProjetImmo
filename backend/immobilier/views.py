from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import HttpResponseServerError
from .mixins import LoginRequiredMixin
from .models import BienImmobilier, TypeBien
from .forms import BienImmobilierForm

# Gestionnaires d'erreurs personnalisés
def handler400(request, exception=None, template_name='immobilier/errors/400.html'):
    """Gestion personnalisée de l'erreur 400 - Requête incorrecte"""
    return render(request, template_name, status=400)

def handler403(request, exception=None, template_name='immobilier/errors/403.html'):
    """Gestion personnalisée de l'erreur 403 - Accès refusé"""
    return render(request, template_name, status=403)

def handler404(request, exception=None, template_name='immobilier/errors/404.html'):
    """Gestion personnalisée de l'erreur 404 - Page non trouvée"""
    return render(request, template_name, status=404)

def handler500(request, template_name='immobilier/errors/500.html'):
    """Gestion personnalisée de l'erreur 500 - Erreur serveur interne"""
    return render(request, template_name, status=500)

class ListeBiensView(ListView):
    model = BienImmobilier
    template_name = 'immobilier/liste_biens.html'
    context_object_name = 'biens'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtres de recherche
        type_transaction = self.request.GET.get('type_transaction')
        type_bien = self.request.GET.get('type_bien')
        ville = self.request.GET.get('ville')
        prix_max = self.request.GET.get('prix_max')
        
        if type_transaction:
            queryset = queryset.filter(type_transaction=type_transaction)
        if type_bien:
            queryset = queryset.filter(type_bien_id=type_bien)
        if ville:
            queryset = queryset.filter(ville__icontains=ville)
        if prix_max:
            queryset = queryset.filter(prix__lte=prix_max)
            
        return queryset.filter(disponible=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types_bien'] = TypeBien.objects.all()
        return context

class DetailBienView(DetailView):
    model = BienImmobilier
    template_name = 'immobilier/detail_bien.html'
    context_object_name = 'bien'

class CreerBienView(LoginRequiredMixin, CreateView):
    model = BienImmobilier
    form_class = BienImmobilierForm
    template_name = 'immobilier/creer_bien.html'
    success_url = reverse_lazy('liste_biens')
    
    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        messages.success(self.request, 'Le bien a été ajouté avec succès !')
        return super().form_valid(form)

class ModifierBienView(LoginRequiredMixin, UpdateView):
    model = BienImmobilier
    form_class = BienImmobilierForm
    template_name = 'immobilier/modifier_bien.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Le bien a été mis à jour avec succès !')
        return reverse_lazy('detail_bien', kwargs={'pk': self.object.pk})

class SupprimerBienView(LoginRequiredMixin, DeleteView):
    model = BienImmobilier
    template_name = 'immobilier/supprimer_bien.html'
    success_url = reverse_lazy('liste_biens')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le bien a été supprimé avec succès !')
        return super().delete(request, *args, **kwargs)

class RegisterChoiceView(TemplateView):
    """Vue pour le choix du type de compte à l'inscription"""
    template_name = 'immobilier/auth/register_choice.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


def accueil(request):
    """
    Vue pour la page d'accueil du site
    """
    # Rediriger les utilisateurs connectés vers leur espace respectif
    if request.user.is_authenticated and hasattr(request.user, 'user_type'):
        if request.user.user_type == 'particulier':
            if request.path != reverse('immobilier:espace_particulier'):
                return redirect('immobilier:espace_particulier')
        elif request.user.user_type == 'professionnel':
            if request.path != reverse('immobilier:espace_professionnel'):
                return redirect('immobilier:espace_professionnel')
    
    # Récupérer les biens à vendre
    biens_vente = BienImmobilier.objects.filter(
        type_transaction='vente',
        disponible=True
    ).order_by('-date_creation')[:3]
    
    # Récupérer les biens à louer
    biens_location = BienImmobilier.objects.filter(
        type_transaction='location',
        disponible=True
    ).order_by('-date_creation')[:3]
    
    context = {
        'biens_vente': biens_vente,
        'biens_location': biens_location,
    }
    
    return render(request, 'immobilier/accueil.html', context)
