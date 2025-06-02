from django import forms
from django.utils.translation import gettext_lazy as _

class ContacterParticulierForm(forms.Form):
    """Formulaire pour envoyer un message à un particulier"""
    message = forms.CharField(
        label=_('Votre message'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Décrivez votre offre ou posez vos questions au particulier...')
        }),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        # Supprimer l'instance des kwargs pour éviter l'erreur
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({'class': 'form-control'})
