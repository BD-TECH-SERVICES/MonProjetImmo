

from django import forms
from django.contrib.auth.models import User
from main.models import *
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
class ParticulierForm(forms.ModelForm):
    class Meta:
        model = Particulier
        fields = ['nom', 'prenom', 'email', 'date_naissance']
        widgets = {
                'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            }
class ProfessionnelForm(forms.ModelForm):
    class Meta:
        model = Professionnel
        fields = ['nom_societe', 'siret', 'email_pro', 'secteur_activite']


class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['titre', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['titre', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre du projet',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ajoutez une description détaillée...',
                'style': 'resize: none;'
            }),
        }
        labels = {
            'titre': '📌 Titre du Projet',
            'description': '📝 Description',
        }

    def clean_titre(self):
        """Validation du titre (ex: éviter les doublons)"""
        titre = self.cleaned_data.get('titre')
        if Projet.objects.filter(titre=titre).exists():
            raise forms.ValidationError("⚠️ Un projet avec ce titre existe déjà.")
        return titre