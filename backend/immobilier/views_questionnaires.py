from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import ProjetImmobilier
from .forms import ProjetImmobilierForm

class QuestionnaireAchatView(LoginRequiredMixin, TemplateView):
    """
    Vue pour le questionnaire d'achat immobilier
    """
    template_name = 'immobilier/espace_particulier/questionnaire_achat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Questionnaire Achat Immobilier'
        return context
    
    def post(self, request, *args, **kwargs):
        # Récupérer les données du formulaire
        form_data = request.POST.dict()
        
        try:
            # Créer un nouveau projet avec les données du formulaire
            projet = ProjetImmobilier(
                utilisateur=request.user,
                type_projet=form_data.get('type_projet', '').lower(),
                type_bien=form_data.get('type_bien', ''),
                type_professionnel=form_data.get('type_pro', ''),
                etape_actuelle='en_cours',
                statut='nouveau',
                date_creation=timezone.now()
            )
            
            # Sauvegarder le projet
            projet.save()
            
            # Enregistrer les détails supplémentaires dans les réponses du questionnaire
            for key, value in form_data.items():
                if key not in ['csrfmiddlewaretoken', 'type_projet', 'type_bien', 'type_pro']:
                    ReponseQuestionnaire.objects.create(
                        projet=projet,
                        question=key,
                        reponse=value,
                        date_reponse=timezone.now()
                    )
            
            # Rediriger vers le tableau de bord avec un message de succès
            messages.success(request, 'Votre projet a été créé avec succès !')
            return redirect('espace_particulier')
            
        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur
            messages.error(request, f"Une erreur est survenue lors de la création du projet : {str(e)}")
            return self.get(request, *args, **kwargs)
        
        # Rediriger vers la page de détail du projet
        messages.success(request, 'Votre projet d\'achat a été créé avec succès !')
        return redirect('immobilier:espace_particulier')


class QuestionnaireVenteView(LoginRequiredMixin, TemplateView):
    """
    Vue pour le questionnaire de vente immobilière
    """
    template_name = 'immobilier/espace_particulier/questionnaire_vente.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Questionnaire Vente Immobilière'
        return context
    
    def post(self, request, *args, **kwargs):
        # Traitement des réponses du formulaire
        # Cette méthode sera appelée lors de la soumission du formulaire
        
        # Récupérer les données du formulaire
        form_data = request.POST.dict()
        
        # Créer un nouveau projet avec les données du formulaire
        projet = ProjetImmobilier(
            utilisateur=request.user,
            type_projet='vente',
            etape_actuelle='questionnaire_complete',
            # Ajouter d'autres champs du modèle selon les réponses
        )
        
        # Sauvegarder le projet
        projet.save()
        
        # Rediriger vers la page de détail du projet
        messages.success(request, 'Votre projet de vente a été créé avec succès !')
        return redirect('immobilier:espace_particulier')
