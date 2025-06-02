# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, ProfilProfessionnel
import re

class UserRegistrationForm(forms.ModelForm):
    """
    Formulaire d'inscription pour les utilisateurs.
    Gère à la fois les inscriptions particuliers et professionnels.
    """
    first_name = forms.CharField(
        label=_('Prénom'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre prénom'),
            'required': 'required'
        })
    )
    
    last_name = forms.CharField(
        label=_('Nom'),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom'),
            'required': 'required'
        })
    )
    
    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Créez un mot de passe'),
            'required': 'required'
        }),
        help_text=_("Minimum 8 caractères")
    )
    
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirmez votre mot de passe'),
            'required': 'required'
        })
    )
    
    # Champs cachés
    user_type = forms.CharField(widget=forms.HiddenInput())
    
    # Champ username visible et obligatoire
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        max_length=150,
        required=True,
        help_text=_("Ce nom sera utilisé pour vous connecter à votre compte."),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Choisissez un nom d'utilisateur"),
            'required': 'required',
            'autocomplete': 'username'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _("Votre adresse email"),
                'autocomplete': 'email'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type', 'particulier')
        super().__init__(*args, **kwargs)
        self.fields['user_type'].initial = self.user_type
        
        # Configuration spécifique pour les professionnels
        if self.user_type == 'professionnel':
            from .models import EtapeProjet  # Import ici pour éviter les imports circulaires
            
            # Champ pour les étapes de projet prises en charge - Achat
            self.fields['etapes_achat'] = forms.ModelMultipleChoiceField(
                queryset=EtapeProjet.objects.filter(type_projet='achat').order_by('ordre'),
                label=_("Parcours Achat"),
                required=False,
                help_text=_("Sélectionnez les étapes du parcours achat que vous gérez"),
                widget=forms.CheckboxSelectMultiple(attrs={
                    'class': 'etape-checkbox',
                    'data-type': 'achat'
                })
            )
            
            # Champ pour les étapes de projet prises en charge - Vente
            self.fields['etapes_vente'] = forms.ModelMultipleChoiceField(
                queryset=EtapeProjet.objects.filter(type_projet='vente').order_by('ordre'),
                label=_("Parcours Vente"),
                required=False,
                help_text=_("Sélectionnez les étapes du parcours vente que vous gérez"),
                widget=forms.CheckboxSelectMultiple(attrs={
                    'class': 'etape-checkbox',
                    'data-type': 'vente'
                })
            )
            
            self.fields['nom_entreprise'] = forms.CharField(
                label=_("Nom de l'entreprise"),
                max_length=100,
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': _("Nom de l'entreprise"),
                    'required': 'required'
                })
            )
            self.fields['siret'] = forms.CharField(
                label=_("Numéro SIRET"),
                max_length=14,
                required=True,
                help_text=_("14 chiffres, sans espace"),
                validators=[
                    RegexValidator(
                        regex='^\d{14}$',
                        message=_("Le numéro SIRET doit contenir exactement 14 chiffres.")
                    )
                ],
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': _("Numéro SIRET à 14 chiffres"),
                    'pattern': '\d{14}',
                    'minlength': '14',
                    'maxlength': '14',
                    'required': 'required'
                })
            )
            self.fields['type_entreprise'] = forms.ChoiceField(
                label=_("Secteur d'activité"),
                choices=ProfilProfessionnel.TypeEntreprise.choices,
                required=True,
                widget=forms.Select(attrs={
                    'class': 'form-select',
                    'required': 'required'
                })
            )
            self.fields['description'] = forms.CharField(
                label=_("Description de l'activité"),
                required=True,
                help_text=_("Présentez votre entreprise de manière détaillée."),
                min_length=50,
                widget=forms.Textarea(attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': _("Décrivez votre entreprise, vos services, votre expérience..."),
                    'minlength': '50',
                    'required': 'required'
                })
            )
            
        # Ajout de la case à cocher CGU pour tous les utilisateurs
        self.fields['cgu_acceptees'] = forms.BooleanField(
            label=_("J'accepte les conditions générales d'utilisation"),
            required=True,
            widget=forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'required': 'required'
                })
            )
    
    # Champs communs Ã  tous les utilisateurs
    phone = forms.CharField(
        label=_("TÃ©lÃ©phone"),
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Votre numÃ©ro de tÃ©lÃ©phone")
        })
    )
    
    address = forms.CharField(
        label=_("Adresse personnelle"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Votre adresse complÃ¨te")
        })
    )
    
    zip_code = forms.CharField(
        label=_("Code postal"),
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("75000")
        })
    )
    
    city = forms.CharField(
        label=_("Ville"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Ville")
        })
    )
    
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=30,
        required=True,
        initial="Jean",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Votre prénom")
        })
    )
    
    last_name = forms.CharField(
        label=_("Nom"),
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Votre nom")
        })
    )
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "phone", "address", "zip_code", "city", "user_type")
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Choisissez un nom d'utilisateur")
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _("Votre adresse email")
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Vérifier que les mots de passe correspondent
        if password1 and password2 and password1 != password2:
            self.add_error('password2', _("Les mots de passe ne correspondent pas."))
            
        # Vérifier que l'email n'est pas déjà utilisé
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', _("Cette adresse email est déjà utilisée."))
            
        # Vérifier si un nom d'utilisateur a été fourni
        username = cleaned_data.get('username', '').strip()
        
        if not username:
            # Générer un nom d'utilisateur unique basé sur le prénom et le nom si aucun n'est fourni
            first_name = cleaned_data.get('first_name', '').strip().lower()
            last_name = cleaned_data.get('last_name', '').strip().lower()
            
            if first_name and last_name:
                base_username = f"{first_name}.{last_name}".lower()
                base_username = re.sub(r'[^a-z0-9.]', '', base_username)
                
                # Vérifier si le nom d'utilisateur existe déjà
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                    
                cleaned_data['username'] = username
        else:
            # Vérifier si le nom d'utilisateur est déjà utilisé
            if User.objects.filter(username=username).exists():
                self.add_error('username', _("Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre."))
            
        # Vérifier la complexité du mot de passe
        if len(password1) < 8:
            self.add_error('password1', _("Le mot de passe doit contenir au moins 8 caractères."))
            
        # Vérifier la présence de chiffres et de lettres
        if not any(char.isdigit() for char in password1):
            self.add_error('password1', _("Le mot de passe doit contenir au moins un chiffre."))
        if not any(char.isalpha() for char in password1):
            self.add_error('password1', _("Le mot de passe doit contenir au moins une lettre."))
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.user_type = self.cleaned_data["user_type"]
        
        if commit:
            user.save()
            
            # Création du profil professionnel si nécessaire
            if user.user_type == 'professionnel':
                ProfilProfessionnel.objects.create(
                    utilisateur=user,
                    type_entreprise=self.cleaned_data.get('type_entreprise'),
                    nom_entreprise=self.cleaned_data.get('nom_entreprise', ''),
                    siret=self.cleaned_data.get('siret', ''),
                    telephone=user.phone,
                    adresse=user.address,
                    code_postal=user.zip_code,
                    ville=user.city,
                    description=self.cleaned_data.get('description', '')
                )
        
        return user


class ProfessionnelRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription spécifique pour les professionnels.
    À utiliser en complément de UserRegistrationForm."""
    
    nom_entreprise = forms.CharField(
        max_length=100,
        required=True,
        initial="Mon Agence Immobilière",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Nom de l'entreprise"),
            'required': 'required'
        })
    )
    
    logo = forms.ImageField(
        label=_("Logo de l'entreprise"),
        required=False,
        help_text=_("Format recommandé : 200x200px, format PNG ou JPG"),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    site_web = forms.URLField(
        label=_("Site web"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.votresite.com'
        })
    )
    
    numero_tva = forms.CharField(
        label=_("Numéro de TVA intracommunautaire"),
        max_length=20,
        required=False,
        help_text=_("Format: FR + 2 caractères + 9 à 12 chiffres"),
        validators=[
            RegexValidator(
                regex='^FR[A-Za-z]{2}[0-9]{9,12}$',
                message=_("Format invalide. Exemple: FRXX123456789")
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'FRXX123456789',
            'pattern': '^FR[A-Za-z]{2}[0-9]{9,12}$',
            'title': _('Format: FR suivi de 2 lettres puis 9 à 12 chiffres')
        })
    )
    
    horaires = forms.CharField(
        label=_("Horaires d'ouverture"),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _("Lun-Ven: 9h-12h, 14h-18h\nSam: 9h-12h")
        })
    )
    
    # Réseaux sociaux
    facebook = forms.URLField(
        label=_("Page Facebook"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.facebook.com/votrepage'
        })
    )
    
    twitter = forms.URLField(
        label=_("Compte Twitter"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://twitter.com/votrecompte'
        })
    )
    
    linkedin = forms.URLField(
        label=_("Profil LinkedIn"),
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.linkedin.com/in/votrecommpte/'
        })
    )
    
    specialites = forms.CharField(
        label=_("Spécialités"),
        required=False,
        help_text=_("Listez vos spécialités séparées par des virgules"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _("Ex: Immobilier neuf, Location saisonnière, Gestion locative...")
        })
    )
    
    siret = forms.CharField(
        label=_("Numéro SIRET") + " *",
        max_length=14,
        required=True,
        help_text=_("14 chiffres, sans espace"),
        validators=[
            RegexValidator(
                regex='^\d{14}$',
                message=_("Le numéro SIRET doit contenir exactement 14 chiffres.")
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Numéro SIRET à 14 chiffres"),
            'pattern': '\d{14}',
            'required': 'required',
            'minlength': '14',
            'maxlength': '14'
        })
    )
    
    telephone = forms.CharField(
        label=_("Téléphone professionnel") + " *",
        max_length=20,
        required=True,
        initial="0612345678",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Ex: 0612345678"),
            'required': 'required',
            'pattern': '^[0-9]{10}$',
            'title': _('Veuillez entrer un numéro de téléphone valide (10 chiffres)')
        })
    )
    
    type_entreprise = forms.ChoiceField(
        label=_("Secteur d'activité") + " *",
        choices=ProfilProfessionnel.TypeEntreprise.choices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': 'required'
        })
    )
    
    adresse = forms.CharField(
        label=_("Adresse du siège social") + " *",
        required=True,
        initial="123 Avenue des Champs-Élysées",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Adresse complète du siège social"),
            'required': 'required'
        })
    )
    
    code_postal = forms.CharField(
        label=_("Code postal") + " *",
        max_length=5,
        required=True,
        initial="75008",
        validators=[
            RegexValidator(
                regex='^\d{5}$',
                message=_("Le code postal doit contenir exactement 5 chiffres.")
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Code postal"),
            'required': 'required',
            'pattern': '\d{5}',
            'maxlength': '5'
        })
    )
    
    ville = forms.CharField(
        label=_("Ville") + " *",
        required=True,
        initial="Paris",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Ville"),
            'required': 'required'
        })
    )
    
    description = forms.CharField(
        label=_("Description de l'activité") + " *",
        required=True,
        help_text=_("Minimum 50 caractères. Présentez votre entreprise de manière détaillée."),
        min_length=50,
        initial="Notre agence immobilière vous accompagne dans tous vos projets immobiliers avec professionnalisme et réactivité. Forts de 10 ans d'expérience, nous mettons notre expertise à votre service pour vous proposer les meilleures offres du marché.",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _("Décrivez votre entreprise, vos services, votre expérience..."),
            'required': 'required',
            'minlength': '50'
        })
    )
    
    cgu_acceptees = forms.BooleanField(
        label=_("J'accepte les conditions générales d'utilisation") + " *",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': 'required'
        })
    )
    
    class Meta:
        model = ProfilProfessionnel
        fields = [
            'nom_entreprise', 'siret', 'telephone',
            'adresse', 'code_postal', 'ville',
            'type_entreprise', 'description', 'cgu_acceptees', 'site_web'
        ]
        labels = {
            'nom_entreprise': _('Nom de l\'entreprise') + ' *',
            'siret': _('Numéro SIRET') + ' *',
            'telephone': _('Téléphone professionnel') + ' *',
            'adresse': _('Adresse du siège social') + ' *',
            'code_postal': _('Code postal') + ' *',
            'ville': _('Ville') + ' *',
            'type_entreprise': _("Secteur d'activité") + ' *',
            'description': _("Description de l'activité") + ' *',
            'site_web': _('Site web'),
            'cgu_acceptees': _("J'accepte les conditions générales d'utilisation") + ' *'
        }
    
    def clean_siret(self):
        siret = self.cleaned_data.get('siret')
        if siret and not siret.isdigit():
            raise forms.ValidationError(_("Le numéro SIRET ne doit contenir que des chiffres."))
        if siret and len(siret) != 14:
            raise forms.ValidationError(_("Le numéro SIRET doit contenir exactement 14 chiffres."))
        return siret
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if not telephone:
            raise forms.ValidationError(_("Ce champ est obligatoire."))
            
        # Nettoyer le numéro de téléphone (supprimer les espaces, tirets, etc.)
        telephone = ''.join(filter(str.isdigit, str(telephone)))
        
        # Vérifier la longueur du numéro (10 chiffres pour la France)
        if len(telephone) != 10:
            raise forms.ValidationError(_("Le numéro de téléphone doit contenir 10 chiffres."))
            
        # Vérifier que le numéro commence par 0
        if not telephone.startswith('0'):
            telephone = '0' + telephone
            
        # Vérifier le format du numéro (commence par 01-09)
        if not re.match(r'^0[1-9]', telephone):
            raise forms.ValidationError(_("Le numéro de téléphone n'est pas valide."))
            
        return telephone
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Valeurs par défaut pour les tests
        if not self.data:  # Seulement si le formulaire n'a pas été soumis
            self.fields['nom_entreprise'].initial = "Agence Test"
            self.fields['siret'].initial = "12345678901234"
            self.fields['telephone'].initial = "0612345678"
            self.fields['adresse'].initial = "1 Rue de Test"
            self.fields['code_postal'].initial = "75000"
            self.fields['ville'].initial = "Paris"
            self.fields['description'].initial = "Description de test pour l'agence immobilière"
            self.fields['type_entreprise'].initial = ProfilProfessionnel.TypeEntreprise.AGENCE
    
    def save(self, commit=True):
        # Créer l'utilisateur avec l'email comme username
        user = super().save(commit=False)
        
        # Utiliser l'email comme nom d'utilisateur
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data["password1"])
        
        # Définir le type d'utilisateur
        user.user_type = self.cleaned_data.get('user_type', 'particulier')
        
        # Sauvegarder l'utilisateur
        if commit:
            user.save()
            
            # Gestion du logo si fourni
            logo_file = self.cleaned_data.get('logo')
            logo_path = None
            
            if logo_file:
                # Création d'un nom de fichier unique
                fs = FileSystemStorage()
                filename = fs.save(f'logos/{user.username}_{logo_file.name}', logo_file)
                logo_path = fs.url(filename)
            
            profil_data = {
                'raison_sociale': self.cleaned_data.get('nom_entreprise', ''),
                'siret': self.cleaned_data.get('siret', ''),
                'telephone': self.cleaned_data.get('telephone', ''),
                'adresse': self.cleaned_data.get('adresse', ''),
                'code_postal': self.cleaned_data.get('code_postal', ''),
                'ville': self.cleaned_data.get('ville', ''),
                'type_entreprise': self.cleaned_data.get('type_entreprise', ProfilProfessionnel.TypeEntreprise.AUTRE),
                'description': self.cleaned_data.get('description', ''),
                'site_web': self.cleaned_data.get('site_web', '')
            }
            
            if logo_path:
                profil_data['logo'] = logo_path
            
            profil, created = ProfilProfessionnel.objects.update_or_create(
                utilisateur=user,
                defaults=profil_data
            )
        
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        # Validation des champs communs
        if not cleaned_data.get('first_name'):
            self.add_error('first_name', _("Le prénom est obligatoire"))
        if not cleaned_data.get('last_name'):
            self.add_error('last_name', _("Le nom est obligatoire"))
        if not cleaned_data.get('email'):
            self.add_error('email', _("L'adresse email est obligatoire"))
        if not cleaned_data.get('phone'):
            self.add_error('phone', _("Le numéro de téléphone est obligatoire"))
        if not cleaned_data.get('address'):
            self.add_error('address', _("L'adresse est obligatoire"))
        if not cleaned_data.get('zip_code'):
            self.add_error('zip_code', _("Le code postal est obligatoire"))
        if not cleaned_data.get('city'):
            self.add_error('city', _("La ville est obligatoire"))
        
        # Validation du format du code postal personnel
        zip_code = cleaned_data.get('zip_code', '')
        if zip_code and not zip_code.isdigit():
            self.add_error('zip_code', _("Le code postal ne doit contenir que des chiffres"))
        
        # Validation spécifique pour les professionnels
        if user_type == 'professionnel':
            # Champs obligatoires pour les professionnels
            required_fields = {
                'raison_sociale': _("La raison sociale est obligatoire"),
                'siret': _("Le numéro SIRET est obligatoire"),
                'telephone': _("Le téléphone professionnel est obligatoire"),
                'adresse': _("L'adresse du siège social est obligatoire"),
                'code_postal': _("Le code postal est obligatoire"),
                'ville': _("La ville est obligatoire"),
                'type_entreprise': _("Le secteur d'activité est obligatoire")
            }
            
            # Validation du format du SIRET
            siret = cleaned_data.get('siret', '')
            if siret and (not siret.isdigit() or len(siret) != 14):
                self.add_error('siret', _("Le numéro SIRET doit contenir exactement 14 chiffres"))
            
            # Validation du format du code postal
            code_postal = cleaned_data.get('code_postal', '')
            if code_postal and not code_postal.isdigit():
                self.add_error('code_postal', _("Le code postal ne doit contenir que des chiffres"))
            
            # Vérification des champs obligatoires
            for field, error_msg in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, error_msg)
        
        return cleaned_data

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur ou email"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _("Entrez votre nom d'utilisateur ou email"),
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _("Entrez votre mot de passe")
        }),
    )
    remember_me = forms.BooleanField(
        label=_("Se souvenir de moi"),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    error_messages = {
        'invalid_login': _(
            "Veuillez entrer un nom d'utilisateur/email et un mot de passe valides. "
            "Notez que ces champs sont sensibles à la casse."
        ),
        'inactive': _("Ce compte est inactif."),
    }
