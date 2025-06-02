from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _


from .models import BienImmobilier
from .forms import BienImmobilierForm


class GestionBiensView(LoginRequiredMixin, ListView):
    """
    Vue pour gérer les biens immobiliers de l'utilisateur connecté
    """
    model = BienImmobilier
    template_name = 'immobilier/gestion_biens/liste_biens.html'
    context_object_name = 'biens'
    paginate_by = 10

    def get_queryset(self):
        # Ne retourner que les biens du propriétaire connecté
        return BienImmobilier.objects.filter(
            proprietaire=self.request.user
        ).order_by('-date_creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['onglet_actif'] = 'gestion_biens'
        return context


class CreerBienView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau bien immobilier
    """
    model = BienImmobilier
    form_class = BienImmobilierForm
    template_name = 'immobilier/gestion_biens/creer_bien.html'
    success_url = reverse_lazy('immobilier:gestion_biens')

    def form_valid(self, form):
        form.instance.proprietaire = self.request.user
        messages.success(self.request, _('Le bien a été ajouté avec succès !'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['onglet_actif'] = 'gestion_biens'
        return context


class ModifierBienView(LoginRequiredMixin, UpdateView):
    """
    Vue pour modifier un bien immobilier existant
    """
    model = BienImmobilier
    form_class = BienImmobilierForm
    template_name = 'immobilier/gestion_biens/modifier_bien.html'
    context_object_name = 'bien'

    def get_queryset(self):
        # Ne permettre de modifier que les biens du propriétaire connecté
        return BienImmobilier.objects.filter(proprietaire=self.request.user)

    def get_success_url(self):
        messages.success(self.request, _('Le bien a été mis à jour avec succès !'))
        return reverse_lazy('immobilier:gestion_biens')


class SupprimerBienView(LoginRequiredMixin, DeleteView):
    """
    Vue pour supprimer un bien immobilier
    """
    model = BienImmobilier
    template_name = 'immobilier/gestion_biens/supprimer_bien.html'
    success_url = reverse_lazy('immobilier:gestion_biens')
    context_object_name = 'bien'

    def get_queryset(self):
        # Ne permettre de supprimer que les biens du propriétaire connecté
        return BienImmobilier.objects.filter(proprietaire=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Le bien a été supprimé avec succès !'))
        return super().delete(request, *args, **kwargs)
