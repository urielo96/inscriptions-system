from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # #     path('',views.login_view, name='login_view'),
    path('', RedirectView.as_view(pattern_name='login'), name='index'),
    path('users/login/', views.login_users, name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('grupos/',views.vista_administrador, name='inscripcion'), 
    path('carga_users/',views.carga_users, name='carga_users'),
    path('crear_periodo/',views.crear_periodo, name='crear_periodo'),
]
