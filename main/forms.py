

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


class CarteForm(forms.ModelForm):
    class Meta:
        model = Carte
        fields = ['titre', 'projets']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'projets': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        utilisateur = kwargs.pop('utilisateur', None)
        super().__init__(*args, **kwargs)
        if utilisateur:
            self.fields['projets'].queryset = Projet.objects.filter(utilisateur=utilisateur)