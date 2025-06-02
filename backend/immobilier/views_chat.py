from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse

from .models import Conversation, Message, ProjetImmobilier, User
from .forms import MessageForm

class ListeConversationsView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des conversations de l'utilisateur
    """
    model = Conversation
    template_name = 'immobilier/chat/liste_conversations.html'
    context_object_name = 'conversations'
    paginate_by = 10
    
    def get_queryset(self):
        # Pour les professionnels : voir toutes leurs conversations
        if self.request.user.est_professionnel:
            return Conversation.objects.filter(
                professionnel=self.request.user
            ).select_related('projet', 'projet__utilisateur').order_by('-date_modification')
        
        # Pour les particuliers : voir les conversations sur leurs projets
        return Conversation.objects.filter(
            projet__utilisateur=self.request.user
        ).select_related('projet', 'professionnel').order_by('-date_modification')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_professionnel'] = self.request.user.est_professionnel
        return context


class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher une conversation et envoyer des messages
    """
    model = Conversation
    template_name = 'immobilier/chat/conversation_detail.html'
    context_object_name = 'conversation'
    form_class = MessageForm
    
    def get_queryset(self):
        # Vérifier que l'utilisateur a le droit de voir cette conversation
        if self.request.user.est_professionnel:
            return Conversation.objects.filter(professionnel=self.request.user)
        return Conversation.objects.filter(projet__utilisateur=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        
        # Marquer les messages comme lus
        messages_non_lus = self.object.messages.filter(lu=False).exclude(expediteur=self.request.user)
        messages_non_lus.update(lu=True)
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = self.object
            message.expediteur = request.user
            message.save()
            
            # Mettre à jour la date de modification de la conversation
            self.object.date_modification = timezone.now()
            self.object.save(update_fields=['date_modification'])
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'contenu': message.contenu,
                        'date_creation': message.date_creation.strftime('%d/%m/%Y %H:%M'),
                        'expediteur': message.expediteur.get_full_name() or message.expediteur.username
                    }
                })
            
            return redirect('immobilier:conversation_detail', pk=self.object.pk)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        return self.render_to_response(self.get_context_data(form=form))


class NouvelleConversationView(LoginRequiredMixin, View):
    """
    Vue pour démarrer une nouvelle conversation avec un professionnel
    """
    def post(self, request, projet_id, *args, **kwargs):
        projet = get_object_or_404(ProjetImmobilier, id=projet_id)
        
        # Vérifier que l'utilisateur est bien le propriétaire du projet
        if projet.utilisateur != request.user:
            messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
            return redirect('immobilier:espace_particulier')
        
        # Récupérer le professionnel (à partir du formulaire)
        professionnel_id = request.POST.get('professionnel_id')
        if not professionnel_id:
            messages.error(request, "Veuillez sélectionner un professionnel.")
            return redirect('immobilier:espace_particulier')
        
        try:
            professionnel = User.objects.get(id=professionnel_id, user_type='professionnel')
        except User.DoesNotExist:
            messages.error(request, "Professionnel introuvable.")
            return redirect('immobilier:espace_particulier')
        
        # Créer ou récupérer la conversation
        conversation, created = Conversation.objects.get_or_create(
            projet=projet,
            professionnel=professionnel
        )
        
        # Rediriger vers la conversation
        return redirect('immobilier:conversation_detail', pk=conversation.id)


class ListeProfessionnelsView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des professionnels pour démarrer une conversation
    """
    model = User
    template_name = 'immobilier/chat/liste_professionnels.html'
    context_object_name = 'professionnels'
    paginate_by = 20
    
    def get_queryset(self):
        # Récupérer uniquement les professionnels vérifiés
        return User.objects.filter(
            user_type='professionnel',
            is_active=True,
            profil_pro__isnull=False
        ).select_related('profil_pro').order_by('first_name', 'last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projet_id'] = self.kwargs.get('projet_id')
        return context
