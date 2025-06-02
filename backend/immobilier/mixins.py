from django.contrib.auth.mixins import AccessMixin
from django.urls import reverse_lazy

class LoginRequiredMixin(AccessMixin):
    """Vérifie que l'utilisateur est connecté et redirige vers la page de connexion personnalisée si nécessaire."""
    login_url = reverse_lazy('immobilier:login')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
