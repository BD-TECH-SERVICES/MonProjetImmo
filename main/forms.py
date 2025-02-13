

from django import forms
from django.contrib.auth.models import User
from main.models import Particulier, Professionnel

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
