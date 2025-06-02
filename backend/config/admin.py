from django.contrib import admin
from django.urls import path, reverse
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect

# Configuration personnalisée de l'administration
class CustomAdminSite(admin.AdminSite):
    def logout(self, request, extra_context=None):
        """
        Logout the user and redirect to the home page.
        """
        from django.contrib.auth import logout
        logout(request)
        return HttpResponseRedirect(reverse('immobilier:accueil'))

# Utilisation de la classe d'administration personnalisée
admin.site = CustomAdminSite(name='admin')
admin.autodiscover()
