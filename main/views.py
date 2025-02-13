
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import ParticulierForm, ProfessionnelForm, UserForm
from main.models import Particulier, Professionnel

def inscription_page(request):
    return render(request, 'blog/inscription.html')  #
def about(request):
    return render(request, 'about.html')



from django.contrib.auth import get_user_model


User = get_user_model()
def create_particulier_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        particulier_form = ParticulierForm(request.POST)  # Assurez-vous d'utiliser ParticulierForm ici
        if user_form.is_valid() and particulier_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])  # Définir le mot de passe
            user.user_type = 'particulier'
            user.save()

            particulier = particulier_form.save(commit=False)
            particulier.user = user  # Associe le profil à l'utilisateur
            particulier.save()

            login(request, user)
            return redirect('login')
    else:
        user_form = UserForm()
        particulier_form = ParticulierForm()

    return render(request, 'blog/create_particulier.html', {
        'user_form': user_form,
        'particulier_form': particulier_form,  # Bien passer ce formulaire au contexte
    })


def create_professionnel_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        professionnel_form = ProfessionnelForm(request.POST)
        if user_form.is_valid() and professionnel_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.user_type = 'professionnel'
            user.save()

            professionnel = professionnel_form.save(commit=False)
            professionnel.user = user
            professionnel.save()

            login(request, user)
            return redirect('login')
    else:
        user_form = UserForm()
        professionnel_form = ProfessionnelForm()  # Assurez-vous de l'initialisation ici

    return render(request, 'blog/create_professionnel.html', {
        'user_form': user_form,
        'professionnel_form': professionnel_form,  # Formulaire bien passé au contexte
    })
