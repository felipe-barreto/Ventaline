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
from PaginaWeb.views import buscar_viaje, compra_cancelar, compra_detalle,compra_viaje_confirmar, compra_viaje_asientos, compra_viaje_productos, compra_viaje_tarjeta,\
    home, mis_comentarios, mis_compras, registrar, perfil, perfil_editar, perfil_contraseña, perfil_contraseña_editar, perfil_tipo_gold, perfil_tipo_gold_editar,\
    perfil_tipo_pasar_a_comun, perfil_tipo_pasar_a_comun_confirmar, perfil_tipo_comun, perfil_tipo_comun_editar, AgregarComentarioView, ModificarComentarioView,\
    EliminarComentarioView, EliminarCuentaView, eliminar_cuenta_confirmar
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),
    path('mis_comentarios/', mis_comentarios, name='mis_comentarios'),
    path('mis_compras/', mis_compras, name='mis_compras'),
    path('registrar/', registrar, name='registrar'),
    path("soychofer/", auth_views.LoginView.as_view(template_name = 'chofer_login.html'), name="soychofer"),
    path('login/', auth_views.LoginView.as_view(template_name = 'login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'logout.html'), name='logout'),
    path('perfil/', perfil, name='perfil'),
    path('perfil/editar/', perfil_editar, name='perfil_editar'),
    path('perfil/contraseña/', perfil_contraseña, name='perfil_contraseña'),
    path('perfil/contraseña/editar/', perfil_contraseña_editar, name='perfil_contraseña_editar'),
    path('perfil/tipo/gold/', perfil_tipo_gold, name='perfil_tipo_gold'),
    path('perfil/tipo/gold/editar/', perfil_tipo_gold_editar, name='perfil_tipo_gold_editar'),
    path('perfil/tipo/pasar_a_comun/', perfil_tipo_pasar_a_comun, name='perfil_tipo_pasar_a_comun'),
    path('perfil/tipo/pasar_a_comun/confirmar/', perfil_tipo_pasar_a_comun_confirmar, name='perfil_tipo_pasar_a_comun_confirmar'),
    path('perfil/tipo/comun/', perfil_tipo_comun, name='perfil_tipo_comun'),
    path('perfil/tipo/comun/editar/', perfil_tipo_comun_editar, name='perfil_tipo_comun_editar'),
    path('agregar_comentario/', AgregarComentarioView.as_view(template_name = 'agregar_comentario.html'), name='agregar_comentario'),
    path('editar_comentario/<int:pk>', ModificarComentarioView.as_view(), name='modificar_comentario'),
    path('eliminar_comentario/<int:pk>', EliminarComentarioView.as_view(), name='eliminar_comentario'),
    path('buscar_viaje/', buscar_viaje, name='buscar_viaje'),
    path('compra_viaje_asientos/<int:viaje>', compra_viaje_asientos, name='compra_viaje_asientos'),
    path('compra_viaje_productos/<int:viaje>/<int:producto>', compra_viaje_productos, name='compra_viaje_productos'),
    path('compra_viaje_confirmar/<int:viaje>', compra_viaje_confirmar, name='compra_viaje_confirmar'),
    path('compra_viaje_tarjeta/<int:viaje>', compra_viaje_tarjeta, name='compra_viaje_tarjeta'),
    path('compra_detalle/<int:compra>',compra_detalle, name='compra_detalle'),
    path('compra_cancelar/<int:compra>',compra_cancelar, name='compra_cancelar'),
    path('eliminar_cuenta/<int:pk>', EliminarCuentaView.as_view(), name='eliminar_cuenta'),
    path('eliminar_cuenta_confirmar/', eliminar_cuenta_confirmar, name='eliminar_cuenta_confirmar'),
]
