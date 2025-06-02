from django import template
from django.db.models import Q
from ..models import Message

register = template.Library()

@register.filter(name='unread_messages_count')
def unread_messages_count(user):
    """
    Retourne le nombre de messages non lus pour l'utilisateur connecté
    """
    if not user.is_authenticated:
        return 0
    
    if user.est_professionnel:
        # Pour les professionnels : compter les messages non lus dans leurs conversations
        return Message.objects.filter(
            conversation__professionnel=user,
            lu=False
        ).exclude(expediteur=user).count()
    else:
        # Pour les particuliers : compter les messages non lus dans leurs conversations
        return Message.objects.filter(
            conversation__projet__utilisateur=user,
            lu=False
        ).exclude(expediteur=user).count()
