from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def profile_view(request):
    """
    Vue pour afficher et gérer le profil utilisateur
    """
    context = {
        'user': request.user,
        'is_professionnel': hasattr(request.user, 'est_professionnel') and request.user.est_professionnel
    }
    return render(request, 'immobilier/profile/profile.html', context)

@login_required
def change_password(request):
    """
    Vue pour changer le mot de passe de l'utilisateur
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour maintenir la connexion
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès !')
            return redirect('immobilier:profile')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'immobilier/profile/change_password.html', {
        'form': form
    })
