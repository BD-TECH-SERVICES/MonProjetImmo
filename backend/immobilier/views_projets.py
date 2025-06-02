from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse

from .models import ProjetImmobilier, Conversation, Message, EtapeProjet, EtapeProjetInstance, TypeProfessionnel
from .forms_projets import ContacterParticulierForm
from .forms_projet import ProjetImmobilierForm

class ListeProjetsProfessionnelView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ProjetImmobilier
    template_name = 'immobilier/professionnel/liste_projets.html'
    context_object_name = 'projets'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'user_type') and self.request.user.user_type == 'professionnel'

    def get_queryset(self):
        # Récupérer tous les projets non supprimés
        return ProjetImmobilier.objects.all().select_related('utilisateur').order_by('-date_creation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['professionnel'] = getattr(self.request.user, 'profil_pro', None)
        return context


class ContacterParticulierView(LoginRequiredMixin, FormView):
    form_class = ContacterParticulierForm
    template_name = 'immobilier/professionnel/contacter_particulier.html'
    
    def get_success_url(self):
        return reverse_lazy('immobilier:liste_conversations')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projet = get_object_or_404(ProjetImmobilier, id=self.kwargs['projet_id'])
        context['projet'] = projet
        return context
    
    def form_valid(self, form):
        projet = get_object_or_404(ProjetImmobilier, id=self.kwargs['projet_id'])
        
        # Vérifier que l'utilisateur n'est pas le propriétaire du projet
        if self.request.user == projet.utilisateur:
            messages.error(self.request, _("Vous ne pouvez pas vous envoyer de message à vous-même."))
            return self.form_invalid(form)
        
        try:
            # Si l'utilisateur est un professionnel, l'associer au projet
            if self.request.user.user_type == 'professionnel' and not projet.professionnel_selectionne:
                projet.professionnel_selectionne = self.request.user
                projet.save(update_fields=['professionnel_selectionne'])
            
            # Créer ou récupérer la conversation
            conversation, created = Conversation.objects.get_or_create(
                projet=projet,
                professionnel=self.request.user if self.request.user.user_type == 'professionnel' else None,
                particulier=self.request.user if self.request.user.user_type == 'particulier' else projet.utilisateur
            )
            
            # Créer le message
            Message.objects.create(
                conversation=conversation,
                expediteur=self.request.user,
                contenu=form.cleaned_data['message']
            )
            
            messages.success(self.request, _('Votre message a été envoyé avec succès.'))
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, _(f"Une erreur est survenue: {str(e)}"))
            return self.form_invalid(form)


class ChargerEtapesView(View):
    """Vue pour charger les étapes en fonction du type de projet sélectionné"""
    
    def get(self, request, *args, **kwargs):
        type_projet = request.GET.get('type_projet')
        
        if not type_projet or type_projet not in dict(ProjetImmobilier.TYPE_PROJET_CHOICES):
            return HttpResponse('')
        
        # Récupérer les étapes pour le type de projet sélectionné
        etapes = EtapeProjet.objects.filter(
            type_projet=type_projet
        ).order_by('ordre')
        
        # Créer une instance du formulaire pour accéder au champ etape_actuelle
        form = ProjetImmobilierForm()
        form.fields['etape_actuelle'].queryset = etapes
        
        context = {
            'etapes': etapes,
            'field': form['etape_actuelle'],
            'widget': form.fields['etape_actuelle'].widget
        }
        
        return render(request, 'immobilier/partials/etapes_projet.html', context)
