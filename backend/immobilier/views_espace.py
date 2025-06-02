from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from .models import ProjetImmobilier, Conversation, Message, EtapeProjet, EtapeProjetInstance
from .forms import ProjetImmobilierForm, EtapeProjetForm

class EspaceParticulierView(LoginRequiredMixin, ListView):
    model = ProjetImmobilier
    template_name = 'immobilier/espace_particulier/espace_particulier.html'
    context_object_name = 'projets'
    
    def get_queryset(self):
        return ProjetImmobilier.objects.filter(utilisateur=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le comptage des messages non lus
        context['total_messages_non_lus'] = Message.objects.filter(
            conversation__particulier=self.request.user,
            lu=False
        ).exclude(expediteur=self.request.user).count()
        
        # Récupérer les conversations récentes avec le nombre de messages non lus
        # Utiliser select_related pour optimiser les requêtes
        conversations = Conversation.objects.filter(
            particulier=self.request.user
        ).select_related('professionnel', 'projet').order_by('-date_modification')[:5]
        
        conversations_with_unread = []
        
        for conversation in conversations:
            unread_count = Message.objects.filter(
                conversation=conversation,
                lu=False
            ).exclude(expediteur=self.request.user).count()
            
            conversations_with_unread.append({
                'conversation': conversation,
                'unread_count': unread_count
            })
        
        # Ajouter des informations de débogage
        print(f"Nombre de conversations récupérées: {len(conversations_with_unread)}")
        context['conversations_recentes'] = conversations_with_unread
        return context

class CreerProjetView(LoginRequiredMixin, CreateView):
    model = ProjetImmobilier
    form_class = ProjetImmobilierForm
    template_name = 'immobilier/espace_particulier/creer_projet_clean.html'
    success_url = reverse_lazy('immobilier:espace_particulier')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passer l'utilisateur connecté au formulaire
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # Associer l'utilisateur connecté au projet
        form.instance.utilisateur = self.request.user
        
        # Définir l'étape initiale
        form.instance.etape_actuelle = 'initial'
        
        # Enregistrer le projet
        response = super().form_valid(form)
        
        # Ajouter un message de succès
        messages.success(self.request, 'Votre projet a été créé avec succès !')
        
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT') and 'data' in kwargs:
            # Créer une copie mutable des données POST
            data = kwargs['data'].copy()
            # Si le type de projet est fourni, filtrer les étapes en conséquence
            if 'type_projet' in data:
                kwargs['type_projet'] = data['type_projet']
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_creation'] = True
        return context

class ModifierProjetView(LoginRequiredMixin, UpdateView):
    model = ProjetImmobilier
    form_class = ProjetImmobilierForm
    template_name = 'immobilier/espace_particulier/modifier_projet.html'
    context_object_name = 'projet'
    
    def get_queryset(self):
        return ProjetImmobilier.objects.filter(utilisateur=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, _("Votre projet a été mis à jour avec succès !"))
        return reverse_lazy('immobilier:espace_particulier')

class DetailProjetView(LoginRequiredMixin, DetailView):
    model = ProjetImmobilier
    template_name = 'immobilier/espace_particulier/detail_projet.html'
    context_object_name = 'projet'
    
    def get_queryset(self):
        return ProjetImmobilier.objects.filter(utilisateur=self.request.user)

class SupprimerProjetView(LoginRequiredMixin, DeleteView):
    model = ProjetImmobilier
    template_name = 'immobilier/espace_particulier/supprimer_projet.html'
    context_object_name = 'projet'
    
    def get_queryset(self):
        return ProjetImmobilier.objects.filter(utilisateur=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, _("Le projet a été supprimé avec succès !"))
        return reverse_lazy('immobilier:espace_particulier')
    
    def post(self, request, *args, **kwargs):
        # S'assurer que l'utilisateur est bien le propriétaire
        self.object = self.get_object()
        if self.object.utilisateur != request.user:
            messages.error(request, _("Vous n'avez pas la permission de supprimer ce projet."))
            return redirect('immobilier:espace_particulier')
        return self.delete(request, *args, **kwargs)


class ChangerEtapeProjetView(LoginRequiredMixin, UpdateView):
    """
    Vue pour changer l'étape actuelle d'un projet
    """
    model = ProjetImmobilier
    form_class = EtapeProjetForm
    template_name = 'immobilier/espace_particulier/changer_etape.html'
    
    def get_queryset(self):
        return ProjetImmobilier.objects.filter(utilisateur=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['type_projet'] = self.object.type_projet
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projet'] = self.object
        context['etapes'] = EtapeProjet.objects.filter(
            type_projet=self.object.type_projet
        ).order_by('ordre')
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("L'étape du projet a été mise à jour avec succès !"))
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'etape_actuelle': self.object.etape_actuelle.titre if self.object.etape_actuelle else None,
                'etape_actuelle_id': self.object.etape_actuelle.id if self.object.etape_actuelle else None,
            })
        
        return response
    
    def get_success_url(self):
        return reverse('immobilier:detail_projet', kwargs={'pk': self.object.pk})


@login_required
@require_http_methods(["POST"])
def marquer_etape_terminee(request, pk, etape_id):
    """
    Vue pour marquer une étape comme terminée
    """
    projet = get_object_or_404(ProjetImmobilier, pk=pk, utilisateur=request.user)
    etape = get_object_or_404(EtapeProjet, pk=etape_id)
    
    # Vérifier que l'étape appartient bien au type de projet
    if etape.type_projet != projet.type_projet:
        return JsonResponse({'success': False, 'error': 'Étape invalide pour ce type de projet'}, status=400)
    
    # Mettre à jour ou créer l'instance d'étape
    etape_instance, created = projet.etapes_instance.get_or_create(
        etape=etape,
        defaults={
            'est_terminee': True,
            'date_debut': timezone.now(),
            'date_fin': timezone.now()
        }
    )
    
    if not created:
        etape_instance.est_terminee = True
        etape_instance.date_fin = timezone.now()
        etape_instance.save()
    
    return JsonResponse({
        'success': True,
        'etape_id': etape.id,
        'est_terminee': etape_instance.est_terminee,
        'date_fin': etape_instance.date_fin.strftime('%d/%m/%Y') if etape_instance.date_fin else None
    })


class ConversationsView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'immobilier/espace_particulier/conversations.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        # Récupérer toutes les conversations où l'utilisateur est le particulier
        return Conversation.objects.filter(
            particulier=self.request.user
        ).select_related('projet', 'professionnel', 'professionnel__profil_pro')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Marquer les messages comme lus quand l'utilisateur consulte la conversation
        Message.objects.filter(
            conversation__particulier=self.request.user,
            lu=False
        ).exclude(
            expediteur=self.request.user
        ).update(lu=True)
        return context


def redirection_apres_inscription(request):
    """
    Vue de redirection après inscription qui détermine où rediriger l'utilisateur
    en fonction de son type (particulier ou professionnel)
    """
    if not request.user.is_authenticated:
        return redirect('immobilier:login')
    
    if request.user.user_type == 'particulier':
        # Rediriger vers la création de projet pour les particuliers
        messages.info(request, _("Créez votre premier projet immobilier pour commencer."))
        return redirect('immobilier:creer_projet')
    else:
        # Pour les professionnels, vérifier s'ils ont un profil
        if hasattr(request.user, 'profil_pro'):
            return redirect('immobilier:espace_professionnel')
        messages.info(request, _("Complétez votre profil professionnel pour commencer."))
        return redirect('immobilier:creer_profil_pro')
