from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import *

class ConnexionForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


User = get_user_model()

class UserForm(UserCreationForm):
    """User creation form using the email as username."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ParticulierForm(forms.ModelForm):
    class Meta:
        model = Particulier
        exclude = ['user']  # Le champ user sera défini dans la vue


class ProfessionnelForm(forms.ModelForm):
    class Meta:
        model = Professionnel
        exclude = ['user']  # Idem ici

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['titre', 'description', 'metier'] 