"""Ventaline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from PaginaWeb.views import buscar_viaje, home, registrar, perfil, perfil_nombre, perfil_apellido, perfil_dni, perfil_fecha_de_nacimiento, AgregarComentarioView, ModificarComentarioView
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('registrar/', registrar, name='registrar'),
    path('login/', auth_views.LoginView.as_view(template_name = 'login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'logout.html'), name='logout'),
    path('perfil/', perfil, name='perfil'),
    path('perfil/nombre/', perfil_nombre, name='perfil_nombre'),
    path('perfil/apellido/', perfil_apellido, name='perfil_apellido'),
    path('perfil/dni/', perfil_dni, name='perfil_dni'),
    path('perfil/fecha_de_nacimiento/', perfil_fecha_de_nacimiento, name='perfil_fecha_de_nacimiento'),
    path('agregar_comentario/', AgregarComentarioView.as_view(template_name = 'agregar_comentario.html'), name='agregar_comentario'),
    path('editar_comentario/<int:pk>', ModificarComentarioView.as_view(), name='modificar_comentario'),
    path('buscar_viaje/', buscar_viaje, name='buscar_viaje'),
]
