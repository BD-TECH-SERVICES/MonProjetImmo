from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import (
    UserForm,
    ParticulierForm,
    ProfessionnelForm,
    ProjetForm,
    ConnexionForm,
)
from .models import Projet, Dashboard, Message, Projets
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def inscription_page(request):
    debug_message = ""

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        user_type = request.POST.get('user_type')

        if user_type == 'particulier':
            profile_form = ParticulierForm(request.POST)
            active_form = 'particulier'
        else:
            profile_form = ProfessionnelForm(request.POST)
            active_form = 'professionnel'

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])
            user.user_type = user_type
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)

            debug_message = "Redirection vers inscription_etape2"
            logger.debug(debug_message)
            return redirect('inscription_etape2')

        else:
            debug_message = "Formulaire invalide"
            logger.debug(debug_message)

    else:
        user_form = UserForm()
        profile_form = ParticulierForm()
        active_form = 'particulier'
        debug_message = "Chargement initial du formulaire"

    return render(request, 'blog/inscription.html', {
        'form': user_form,
        'form_pro': profile_form,
        'active_form': active_form,
        'debug_message': debug_message,
    })



def about(request):
    return render(request, 'about.html')

def nos_missions(request):
    return render(request, 'blog/nos_missions.html')

def credit(request):
    return render(request, 'blog/credit.html')

def index(request):
    return render(request, 'test/index.html')

@login_required
def parcours(request):
    if request.user.user_type != 'particulier':
        return redirect('dashboard')
    return render(request, 'test/parcours.html')

@login_required
def profession(request):
    if request.user.user_type != 'professionnel':
        return redirect('parcours')
    return render(request, 'test/profession.html')

@login_required
def mes_projets(request):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    projets = Projet.objects.filter(utilisateur=request.user.particulier)
    return render(request, 'blog/mes_projets.html', {'projets': projets})


@login_required
def conversation(request, receiver_id=None):
    if receiver_id is None:
        receiver_id = request.GET.get("receiver_id")
    if receiver_id is None:
        messages.error(request, "Aucun destinataire spécifié.")
        return redirect("dashboard_conversations")
    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur cible n'existe pas.")
        return redirect("dashboard_conversations")

    conversation_id = get_conversation_id(request.user, receiver)
    messages_list = Message.objects.filter(conversation_id=conversation_id).order_by('timestamp')

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                conversation_id=conversation_id,
                sender=request.user,
                receiver=receiver,
                content=content,
            )
            return redirect('conversation', receiver_id=receiver_id)

    return render(request, 'blog/conversation.html', {'messages': messages_list, 'receiver': receiver})

@login_required
def start_or_continue_conversation(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    existing_messages = Message.objects.filter(sender=request.user, receiver=receiver) | Message.objects.filter(sender=receiver, receiver=request.user)
    conversation_id = get_conversation_id(request.user, receiver)

    if not existing_messages.exists():
        Message.objects.create(
            conversation_id=conversation_id,
            sender=request.user,
            receiver=receiver,
            content="Bonjour, je suis intéressé par votre projet !",
        )

    return redirect('conversation_with', user_id=user_id)

@login_required
def conversation_with(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation_id = get_conversation_id(request.user, other_user)
    messages_list = Message.objects.filter(conversation_id=conversation_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                conversation_id=conversation_id,
                sender=request.user,
                receiver=other_user,
                content=content
            )
            return redirect('conversation_with', user_id=user_id)

    return render(request, 'blog/conversation.html', {'messages': messages_list, 'other_user': other_user})

def get_conversation_id(user1, user2):
    return f"{min(user1.id, user2.id)}-{max(user1.id, user2.id)}"

@login_required
def dashboard_conversations(request):
    conversations = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).values_list('sender', 'receiver')
    user_ids = set()
    for sender_id, receiver_id in conversations:
        if sender_id != request.user.id:
            user_ids.add(sender_id)
        if receiver_id != request.user.id:
            user_ids.add(receiver_id)

    conversation_users = User.objects.filter(id__in=user_ids)
    return render(request, 'blog/dashboard_conversations.html', {'conversations': conversation_users})

@login_required
def roadmap(request):
    return render(request, 'blog/roadmap.html')

@login_required
def creer_projet(request, metier=None):
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    metiers_choices = Projet.METIERS_CHOICES if not metier else [choice for choice in Projet.METIERS_CHOICES if choice[0] == metier]

    if request.method == "POST":
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.utilisateur = request.user.particulier
            projet.save()
            return redirect('creer_projet')
    else:
        form = ProjetForm()
        form.fields['metier'].choices = metiers_choices

    return render(request, 'blog/creer_projet.html', {'form': form})

def inscription_etape1(request):
    if request.method == "POST":
        for field in ['user_type', 'prenom', 'nom', 'email', 'telephone']:
            request.session[field] = request.POST.get(field)
        return redirect('inscription_etape2')
    return render(request, 'test/inscription.html')

def inscription_etape2(request):
    if request.method == "POST":
        request.session['projet_type'] = request.POST.get('projet_type')
        return redirect('inscription_etape3')
    return render(request, 'test/AcheterOuVendre.html')

def inscription_etape3(request):
    if request.method == "POST":
        projet = Projets(
            utilisateur=request.user,
            type_projet=request.session.get('projet_type'),
            type_bien=request.POST.get('bien_type'),
            nombre_pieces=request.POST.get('pieces'),
            superficie=request.POST.get('superficie'),
            budget=request.POST.get('budget'),
            localisation=request.POST.get('localisation'),
            exterieur=request.POST.get('exterieur') == 'on',
            garage=request.POST.get('garage') == 'on',
            transport=request.POST.get('transport'),
            travaux=request.POST.get('travaux'),
        )
        projet.save()
        return redirect('inscription_confirmation')
    return render(request, 'test/ProjetUser.html')

def inscription_confirmation(request):
    return render(request, 'test/Connection.html')

def custom_login_view(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('parcours')
    else:
        form = ConnexionForm()
    return render(request, 'blog/connexion.html', {'user_form': form})

@login_required
def dashboard(request):
    professionnel = getattr(request.user, 'professionnel', None)
    if not professionnel:
        return JsonResponse({'error': 'Accès réservé aux professionnels'}, status=403)

    projets = Projets.objects.all().order_by('-date_creation')

    # Exemple de calculs dynamiques (à adapter selon tes champs)
    nb_leads = projets.count()
    nb_rdv = projets.filter(statut="rendez-vous").count()
    nb_contrats = projets.filter(statut="contrat").count()

    taux_conversion = 0
    if nb_leads > 0:
        taux_conversion = round((nb_contrats / nb_leads) * 100)

    return render(request, 'blog/profession.html', {
        'projets': projets,
        'nb_leads': nb_leads,
        'nb_rdv': nb_rdv,
        'nb_contrats': nb_contrats,
        'taux_conversion': taux_conversion,
    })
