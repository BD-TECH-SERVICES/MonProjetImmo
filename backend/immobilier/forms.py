from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.forms import ModelChoiceField
from .models import (
    BienImmobilier, TypeBien, Message, ProjetImmobilier,
    EtapeProjet, EtapeProjetInstance, TypeEtape
)

class BienImmobilierForm(forms.ModelForm):
    class Meta:
        model = BienImmobilier
        fields = [
            'titre', 'description', 'type_bien', 'type_transaction',
            'prix', 'surface', 'nombre_pieces', 'adresse', 'code_postal',
            'ville', 'image_principale'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_pieces': forms.NumberInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'type_bien': forms.Select(attrs={'class': 'form-select'}),
            'type_transaction': forms.Select(attrs={'class': 'form-select'}),
            'image_principale': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des labels si nécessaire
        self.fields['type_bien'].queryset = TypeBien.objects.all()
        self.fields['type_bien'].label = "Type de bien"
        self.fields['type_transaction'].label = "Type de transaction"
        self.fields['image_principale'].required = False


class MessageForm(forms.ModelForm):
    """
    Formulaire pour l'envoi de messages dans le chat
    """
    class Meta:
        model = Message
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tapez votre message ici...',
                'required': True
            })
        }
        labels = {
            'contenu': ''
        }


class ProjetImmobilierForm(forms.ModelForm):
    class Meta:
        model = ProjetImmobilier
        fields = [
            'type_projet', 'type_bien', 'nombre_pieces', 'surface',
            'surface_min', 'surface_max', 'secteur_geographique',
            'avec_exterieur', 'surface_exterieur', 'avec_garage',
            'proximite_transports', 'budget_min', 'budget_max',
            'travaux_envisages', 'caracteristiques', 'date_achat',
            'exposition', 'description'
        ]
        widgets = {
            'type_projet': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'type_bien': forms.Select(attrs={'class': 'form-select'}),
            'nombre_pieces': forms.NumberInput(attrs={'class': 'form-control'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control'}),
            'surface_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'surface_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'secteur_geographique': forms.TextInput(attrs={'class': 'form-control'}),
            'avec_exterieur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'surface_exterieur': forms.NumberInput(attrs={'class': 'form-control'}),
            'avec_garage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'proximite_transports': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'travaux_envisages': forms.Select(attrs={'class': 'form-select'}),
            'caracteristiques': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_achat': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exposition': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'type_projet': _('Type de projet'),
            'type_bien': _('Type de bien'),
            'nombre_pieces': _('Nombre de pièces'),
            'surface': _('Surface (m²)'),
            'surface_min': _('Surface minimale (m²)'),
            'surface_max': _('Surface maximale (m²)'),
            'secteur_geographique': _('Secteur géographique'),
            'avec_exterieur': _('Avec extérieur'),
            'surface_exterieur': _('Surface extérieure (m²)'),
            'avec_garage': _('Avec garage'),
            'proximite_transports': _('Proximité des transports'),
            'budget_min': _('Budget minimum (€)'),
            'budget_max': _('Budget maximum (€)'),
            'travaux_envisages': _('Travaux envisagés'),
            'caracteristiques': _('Caractéristiques du bien'),
            'date_achat': _("Date d'achat"),
            'exposition': _('Exposition'),
            'description': _('Description complémentaire'),
        }
        help_texts = {
            'proximite_transports': _('Tram, métro, bus, gares à proximité'),
            'surface_exterieur': _('Renseignez la surface si extérieur'),
            'exposition': _('Exposition du jardin ou du séjour si pas d\'extérieur'),
        }


class EtapeProjetForm(forms.ModelForm):
    """
    Formulaire pour sélectionner l'étape actuelle d'un projet immobilier
    """
    etape_actuelle = forms.ModelChoiceField(
        queryset=EtapeProjet.objects.none(),  # Sera rempli dans __init__
        label=_("Sélectionnez votre étape actuelle"),
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = ProjetImmobilier
        fields = ['etape_actuelle']

    def __init__(self, *args, **kwargs):
        type_projet = kwargs.pop('type_projet', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les étapes en fonction du type de projet
        if type_projet:
            self.fields['etape_actuelle'].queryset = EtapeProjet.objects.filter(
                type_projet=type_projet
            ).order_by('ordre')
        
        # Si une instance est fournie, pré-sélectionner l'étape actuelle
        if self.instance and self.instance.etape_actuelle:
            self.fields['etape_actuelle'].initial = self.instance.etape_actuelle
            
        # Masquer les champs non pertinents selon le type de projet
        if self.instance and hasattr(self.instance, 'type_projet'):
            if self.instance.type_projet == ProjetImmobilier.ACHAT:
                if 'caracteristiques' in self.fields:
                    self.fields['caracteristiques'].widget = forms.HiddenInput()
                if 'date_achat' in self.fields:
                    self.fields['date_achat'].widget = forms.HiddenInput()
            elif self.instance.type_projet == ProjetImmobilier.VENTE:  # Vente
                if 'avec_exterieur' in self.fields:
                    self.fields['avec_exterieur'].widget = forms.HiddenInput()
                if 'surface_exterieur' in self.fields:
                    self.fields['surface_exterieur'].widget = forms.HiddenInput()
                if 'avec_garage' in self.fields:
                    self.fields['avec_garage'].widget = forms.HiddenInput()
                if 'proximite_transports' in self.fields:
                    self.fields['proximite_transports'].widget = forms.HiddenInput()
                if 'budget_min' in self.fields:
                    self.fields['budget_min'].widget = forms.HiddenInput()
                if 'budget_max' in self.fields:
                    self.fields['budget_max'].widget = forms.HiddenInput()
                if 'travaux_envisages' in self.fields:
                    self.fields['travaux_envisages'].widget = forms.HiddenInput()

    def save(self, commit=True):
        projet = super().save(commit=False)
        etape = self.cleaned_data.get('etape_actuelle')
        
        if etape:
            projet.etape_actuelle = etape
            
            # Créer ou mettre à jour l'instance d'étape du projet
            etape_instance, created = projet.etapes_instance.get_or_create(
                etape=etape,
                defaults={
                    'est_terminee': False,
                    'date_debut': timezone.now()
                }
            )
            
            # Si l'étape est terminée, mettre à jour la date de fin
            if hasattr(projet, 'etapes_terminees') and etape in projet.etapes_terminees() and not etape_instance.est_terminee:
                etape_instance.est_terminee = True
                etape_instance.date_fin = timezone.now()
                etape_instance.save()
        
        if commit:
            projet.save()
        
        return projet

    def clean(self):
        cleaned_data = super().clean()
        # Nous ne validons que le champ etape_actuelle pour ce formulaire
        # car c'est le seul champ présent dans le formulaire
        return cleaned_data
