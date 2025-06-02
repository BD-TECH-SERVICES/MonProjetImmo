from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ProjetImmobilier, EtapeProjet

class ProjetImmobilierForm(forms.ModelForm):
    etape_actuelle = forms.ModelChoiceField(
        queryset=EtapeProjet.objects.none(),
        label=_("Où en êtes-vous dans votre projet ?"),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = ProjetImmobilier
        fields = [
            'type_projet', 'type_bien', 'budget_min', 'budget_max',
            'surface_min', 'surface_max', 'secteur_geographique', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000', 'placeholder': _('Budget minimum')}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1000', 'placeholder': _('Budget maximum')}),
            'surface_min': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': _('Surface minimale (m²)')}),
            'surface_max': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': _('Surface maximale (m²)')}),
            'secteur_geographique': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ville, quartier, code postal...')}),
            'type_projet': forms.Select(attrs={'class': 'form-select', 'hx-get': '/projet/charger_etapes/', 'hx-trigger': 'change', 'hx-target': '#etapes-container'}),
            'type_bien': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mettre à jour les classes des champs
        self.fields['type_bien'].widget.attrs.update({'class': 'form-select'})
        
        # Si une instance existe, filtrer les étapes en fonction du type de projet
        if self.instance and self.instance.pk and hasattr(self.instance, 'type_projet'):
            self.fields['etape_actuelle'].queryset = EtapeProjet.objects.filter(
                type_projet=self.instance.type_projet
            ).order_by('ordre')
        
        # Ajout des classes Bootstrap aux champs
        for field_name, field in self.fields.items():
            if field_name != 'etape_actuelle' and 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super().clean()
        surface_min = cleaned_data.get('surface_min')
        surface_max = cleaned_data.get('surface_max')
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        type_projet = cleaned_data.get('type_projet')
        
        # Vérifier que la surface maximale est supérieure ou égale à la surface minimale
        if surface_min is not None and surface_max is not None and surface_min > surface_max:
            self.add_error('surface_max', _('La surface maximale doit être supérieure ou égale à la surface minimale.'))
        
        # Vérifier que le budget maximum est supérieur ou égal au budget minimum
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            self.add_error('budget_max', _('Le budget maximum doit être supérieur ou égal au budget minimum.'))
        
        # Si c'est un projet d'achat, vérifier que les budgets sont renseignés
        if type_projet == ProjetImmobilier.ACHAT:
            if not budget_min:
                self.add_error('budget_min', _('Veuillez renseigner un budget minimum pour un projet d\'achat.'))
            if not budget_max:
                self.add_error('budget_max', _('Veuillez renseigner un budget maximum pour un projet d\'achat.'))
        
        return cleaned_data
    
    def save(self, commit=True):
        # Sauvegarder d'abord le projet
        projet = super().save(commit=commit)
        
        # Mettre à jour l'étape actuelle
        etape = self.cleaned_data.get('etape_actuelle')
        if etape:
            projet.etape_actuelle = etape
            if commit:
                projet.save()
        
        return projet
