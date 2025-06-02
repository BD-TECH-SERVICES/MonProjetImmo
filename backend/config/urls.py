"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

# Configuration personnalisée de l'admin
admin.site.site_header = "Administration de l'Agence Immobilière"
admin.site.site_title = "Agence Immobilière Admin"
admin.site.index_title = "Bienvenue dans l'administration"

# URLs de l'application principale - Mettre en premier pour priorité
urlpatterns = [
    path('', include('immobilier.urls', namespace='immobilier')),
    
    # URL de l'administration - accessible uniquement aux utilisateurs admin
    path('admin/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='admin_login'),
    path('admin/logout/', auth_views.LogoutView.as_view(next_page='immobilier:accueil'), name='admin_logout'),
    path('admin/', admin.site.urls),
    
    # Redirection pour les anciennes URLs de connexion
    path('connection/', RedirectView.as_view(url='/connexion/', permanent=True)),
    path('Connexion/', RedirectView.as_view(url='/connexion/', permanent=True)),
]

# Configuration pour servir les fichiers média et statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Gestion des erreurs personnalisées
handler400 = 'immobilier.views.handler400'
handler403 = 'immobilier.views.handler403'
handler404 = 'immobilier.views.handler404'
handler500 = 'immobilier.views.handler500'
