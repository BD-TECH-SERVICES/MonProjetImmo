
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import *
from main.models import *
from django.contrib.auth.decorators import login_required




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

@login_required
def mes_projets(request):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    projets = Projet.objects.filter(utilisateur=request.user.particulier)
    return render(request, 'blog/mes_projets.html', {'projets': projets})


@login_required
def creer_projet(request):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    if request.method == "POST":
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.utilisateur = request.user.particulier
            projet.save()
            return redirect('mes_projets')
    else:
        form = ProjetForm()

    return render(request, 'blog/creer_projet.html', {'form': form})


@login_required
def mes_cartes(request):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    cartes = Carte.objects.filter(utilisateur=request.user.particulier)
    return render(request, 'blog/mes_cartes.html', {'cartes': cartes})


@login_required
def creer_carte(request):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    if request.method == "POST":
        form = CarteForm(request.POST, utilisateur=request.user.particulier)
        if form.is_valid():
            carte = form.save(commit=False)
            carte.utilisateur = request.user.particulier
            carte.save()
            form.save_m2m()
            return redirect('blog/mes_cartes')
    else:
        form = CarteForm(utilisateur=request.user.particulier)

    return render(request, 'cartes/creer_carte.html', {'form': form})


@login_required
def voir_cartes_utilisateurs(request):
    if not hasattr(request.user, 'professionnel'):
        return redirect('mes_projets')

    cartes = Carte.objects.all()
    return render(request, 'blog/cartes_utilisateurs.html', {'cartes': cartes})


import logging

# Configuration du logger
logger = logging.getLogger(__name__)


@login_required
def dashboard(request):

    user_data = {
        "username": request.user.username,
        "id": request.user.id,
        "user_type": getattr(request.user, "user_type", "Non défini"),
        "professionnel": hasattr(request.user, "professionnel")
    }

    # Vérifie si l'utilisateur a un profil professionnel
    professionnel = getattr(request.user, 'professionnel', None)

    if professionnel is None:
        logger.warning(f"⚠️ L'utilisateur {request.user} n'a PAS de profil `Professionnel` en base.")
        return JsonResponse({
            "error": "Vous devez être un professionnel pour voir ces données.",
            "user": user_data
        }, status=403)

    try:
        # Vérifier si un Dashboard existe
        dashboard, created = Dashboard.objects.get_or_create(professionnel=professionnel)
        cartes = Carte.objects.prefetch_related("projets").all()


        logger.info(f"✅ Dashboard chargé pour {request.user} (ID {request.user.id})")
        logger.info(f"📌 Nombre de cartes associées : {cartes.count()}")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du Dashboard : {str(e)}")
        return HttpResponse(f"Erreur interne : {e}", status=500)

    return render(request, 'blog/dashboard.html', {
        'cartes': cartes,
        'debug_info': f"Utilisateur : {request.user}, Professionnel : {professionnel}, Cartes : {cartes.count()}"
    })


