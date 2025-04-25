from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from main import views  
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from main.models import Particulier, Professionnel

from django.contrib.auth import views as auth_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path('conversations/', views.dashboard_conversations, name='dashboard_conversations'),
    path('conversation/', views.conversation, name='conversation'),
    path('conversation/avec/<int:user_id>/', views.conversation_with, name='conversation_with'),
    path('conversation/demarrer/<int:user_id>/', views.start_or_continue_conversation, name='start_conversation'),
    path('inscription/', views.inscription_page, name='inscription'),  
    path('create-particulier/', views.inscription_page, name='create_particulier'),
    path('create-professionnel/', views.inscription_page, name='create_professionnel'),


    path('about', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('creer_projet/<str:metier>/', views.creer_projet, name='creer_projet'),
    path('creer_projet', views.creer_projet, name='creer_projet'),
    path('mes_projets', views.mes_projets, name='mes_projets'),
    path('index', views.index, name='index'),
    path('parcours', views.parcours, name='parcours'),
    path('profession', views.profession, name='profession'),
    
    path('inscription/etape1/', views.inscription_etape1, name='inscription_etape1'),
    path('inscription/etape2/', views.inscription_etape2, name='inscription_etape2'),
    path('inscription/etape3/', views.inscription_etape3, name='inscription_etape3'),
    path('inscription/confirmation/', views.inscription_confirmation, name='inscription_confirmation'),
    
    path('', include(wagtail_urls)),



]
 



if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
