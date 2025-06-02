from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ProfilProfessionnel, DocumentProfessionnel

class ProfilProfessionnelForm(forms.ModelForm):
    class Meta:
        model = ProfilProfessionnel
        fields = [
            'type_entreprise', 'nom_entreprise', 'siret', 'description',
            'site_web', 'telephone', 'annee_creation', 'adresse',
            'code_postal', 'ville', 'cgu_acceptees'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'cgu_acceptees': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout des classes Bootstrap aux champs
        for field in self.fields.values():
            if field.widget.__class__ not in [
                forms.CheckboxInput, 
                forms.RadioSelect, 
                forms.CheckboxSelectMultiple
            ]:
                field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
    
    def clean_siret(self):
        siret = self.cleaned_data.get('siret')
        if siret and not siret.isdigit():
            raise forms.ValidationError(_("Le numéro SIRET ne doit contenir que des chiffres."))
        return siret

class DocumentProfessionnelForm(forms.ModelForm):
    class Meta:
        model = DocumentProfessionnel
        fields = ['type_document', 'fichier', 'date_expiration']
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_document'].widget.attrs.update({'class': 'form-select'})
        self.fields['fichier'].widget.attrs.update({'class': 'form-control'})
    
    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        if fichier:
            # Vérification de la taille du fichier (max 5MB)
            if fichier.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier ne doit pas dépasser 5 Mo."))
            # Vérification de l'extension
            ext = fichier.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']:
                raise forms.ValidationError(_("Type de fichier non pris en charge. Utilisez PDF, JPG, PNG ou DOC."))
        return fichier
