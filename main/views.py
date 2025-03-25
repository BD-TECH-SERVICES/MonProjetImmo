
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import *
from main.models import *
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse





def inscription_page(request):
    return render(request, 'blog/inscription.html')  #
def about(request):
    return render(request, 'about.html')



from django.contrib.auth import get_user_model


def index(request):
    return render(request, 'test/index.html')

def parcours(request):
    return render(request, 'test/parcours.html')

def profession(request):
    return render(request, 'test/profession.html')


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







import logging

# Configuration du logger
logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    logger.info(f"👤 Utilisateur connecté : {request.user} (ID: {request.user.id})")

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
        projets = Projet.objects.all()  # 🔹 On récupère uniquement les projets maintenant

        logger.info(f"✅ Dashboard chargé pour {request.user} (ID {request.user.id})")
        logger.info(f"📌 Nombre de projets affichés : {projets.count()}")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du Dashboard : {str(e)}")
        return HttpResponse(f"Erreur interne : {e}", status=500)

    return render(request, 'blog/dashboard.html', {
        'projets': projets,
        'debug_info': f"Utilisateur : {request.user}, Professionnel : {professionnel}, Projets : {projets.count()}"
    })

from django.contrib import messages
@login_required
def conversation(request):
    """ Vue pour afficher et envoyer des messages """
    receiver_id = 1  # ID de l'utilisateur cible (à modifier si nécessaire)
    try:
        receiver = User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur cible n'existe pas.")
        return redirect("dashboard")

    # Récupérer les messages envoyés par l'utilisateur actuel
    messages_list = Message.objects.filter(sender=request.user).order_by('timestamp')

    # Gestion de l'envoi de message
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=request.user, content=content)
            return redirect('conversation')  # Recharge la page après l'envoi

    return render(request, 'blog/conversation.html', {'messages': messages_list, 'receiver': receiver})

@login_required
def start_or_continue_conversation(request, user_id):
    """ Vérifie si une conversation existe déjà, sinon la crée et redirige vers la discussion """
    receiver = get_object_or_404(User, id=user_id)  # Récupère l'utilisateur cible

    # Vérifier si des messages existent déjà entre les deux utilisateurs
    existing_messages = Message.objects.filter(
        sender=request.user, receiver=receiver  # 🚨 ERREUR : Django ne trouve pas "receiver"
    ) | Message.objects.filter(
        sender=receiver, receiver=request.user
    )


    if not existing_messages.exists():
        # Si aucun message n'existe encore, créer une conversation avec un premier message
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content="Bonjour, je suis intéressé par votre projet !"
        )

    # Redirige vers la conversation (qu'elle existe ou qu'elle vienne d'être créée)
    return redirect('conversation_with', user_id=user_id)

@login_required
def conversation_with(request, user_id):
    """ Affiche la conversation entre l'utilisateur connecté et un autre utilisateur """
    other_user = get_object_or_404(User, id=user_id)
    conversation_id = get_conversation_id(request.user, other_user)
    # Récupérer tous les messages entre les deux utilisateurs
    messages_list = Message.objects.filter(conversation_id=conversation_id)

    # Gestion de l'envoi d'un nouveau message
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


from django.db.models import Q

@login_required
def dashboard_conversations(request):
    """ Affiche toutes les conversations de l'utilisateur connecté """
    
    # Récupérer toutes les conversations où l'utilisateur est impliqué
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)  # Récupérer tous les messages où l'utilisateur est impliqué
    ).values_list('sender', 'receiver')

    # Extraire les ID uniques des interlocuteurs
    user_ids = set()
    for sender_id, receiver_id in conversations:
        if sender_id != request.user.id:
            user_ids.add(sender_id)
        if receiver_id != request.user.id:
            user_ids.add(receiver_id)

    # Récupérer les utilisateurs correspondants
    conversation_users = User.objects.filter(id__in=user_ids)

    return render(request, 'blog/dashboard_conversations.html', {'conversations': conversation_users})

def get_conversation_id(user1, user2):
    """ Génère un identifiant unique pour une conversation entre deux utilisateurs """
    return f"{min(user1.id, user2.id)}-{max(user1.id, user2.id)}"

@login_required
def roadmap(request):
    return render(request, 'blog/roadmap.html')



@login_required
def creer_projet(request, metier=None):
    # Vérifie si l'utilisateur a un attribut 'particulier'
    if not hasattr(request.user, 'particulier'):
        return redirect('blog/dashboard')

    if metier:
        # Filtrer les choix de métiers en fonction de l'étape de la roadmap
        metiers_choices = [choice for choice in Projet.METIERS_CHOICES if choice[0] == metier]
    else:
        metiers_choices = Projet.METIERS_CHOICES

    if request.method == "POST":
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.utilisateur = request.user.particulier
            projet.save()
            return redirect('creer_projet')  # Remplacez par l'URL de succès appropriée
    else:
        form = ProjetForm()
        form.fields['metier'].choices = metiers_choices

    return render(request, 'blog/creer_projet.html', {'form': form})
