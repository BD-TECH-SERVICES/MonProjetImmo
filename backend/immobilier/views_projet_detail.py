from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import ProjetImmobilier, EtapeProjet, EtapeProjetInstance


class DetailProjetView(LoginRequiredMixin, DetailView):
    model = ProjetImmobilier
    template_name = 'immobilier/espace_particulier/detail_projet.html'
    context_object_name = 'projet'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projet = self.object
        
        # Récupérer la conversation avec le professionnel si elle existe
        conversation = projet.get_conversation_avec_professionnel()
        
        # Si aucune conversation n'est trouvée avec le professionnel sélectionné,
        # chercher s'il existe une conversation liée au projet
        if not conversation:
            from .models import Conversation
            conversations = Conversation.objects.filter(
                projet=projet,
                particulier=self.request.user
            ).order_by('-date_modification')
            
            if conversations.exists():
                conversation = conversations.first()
                # Si une conversation existe mais que le professionnel n'est pas associé au projet,
                # nous l'ajoutons au contexte pour l'afficher dans la section "Professionnel"
                context['professionnel_conversation'] = conversation.professionnel
        
        if conversation:
            # Compter les messages non lus
            context['messages_non_lus'] = conversation.messages.filter(lu=False).exclude(expediteur=self.request.user).count()
            context['conversation'] = conversation
        
        # Récupérer toutes les étapes du type de projet
        etapes = EtapeProjet.objects.filter(
            type_projet=projet.type_projet
        ).order_by('ordre')
        
        # Récupérer les instances d'étapes pour ce projet
        etapes_instances = {
            instance.etape_id: instance 
            for instance in projet.etapes_instance.all()
        }
        
        # Préparer les données des étapes pour le template
        etapes_data = []
        etape_actuelle_trouvee = False
        
        for etape in etapes:
            instance = etapes_instances.get(etape.id)
            
            # Déterminer le statut de l'étape
            if instance and instance.est_terminee:
                statut = 'terminee'
            elif projet.etape_actuelle and etape.id == projet.etape_actuelle.id:
                statut = 'en_cours'
                etape_actuelle_trouvee = True
            elif not etape_actuelle_trouvee and not (instance and instance.est_terminee):
                statut = 'a_venir'
            else:
                statut = 'a_venir'
            
            # Créer l'instance si elle n'existe pas encore
            if not instance and statut in ['en_cours', 'a_venir']:
                instance = EtapeProjetInstance.objects.create(
                    projet=projet,
                    etape=etape,
                    date_debut=timezone.now(),  # Toujours définir une date de début
                    est_terminee=(statut == 'terminee')
                )
            
            etapes_data.append({
                'etape': etape,
                'instance': instance,
                'statut': statut,
                'professionnels': etape.professionnels_associes.all()
            })
        
        context.update({
            'etapes': etapes_data,
            'progression': projet.get_avancement(),
            'peut_avancer': projet.peut_avancer(),
            'peut_reculer': projet.peut_reculer()
        })
        
        return context


class ChangerEtapeView(LoginRequiredMixin, UpdateView):
    model = ProjetImmobilier
    fields = []  # Aucun champ à mettre à jour via le formulaire
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        
        if action == 'avancer' and self.object.peut_avancer():
            self.object.avancer_etape()
            messages.success(request, _("L'étape a été mise à jour avec succès."))
        elif action == 'reculer' and self.object.peut_reculer():
            self.object.reculer_etape()
            messages.success(request, _("Vous êtes revenu à l'étape précédente."))
        else:
            messages.error(request, _("Action non autorisée."))
        
        return redirect('immobilier:detail_projet', pk=self.object.pk)
