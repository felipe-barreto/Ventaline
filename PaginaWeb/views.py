from django.db.models.fields import CommaSeparatedIntegerField
from django.core.exceptions import ValidationError
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ExtendedUserCreationForm, ClienteCreationForm, AgregarComentarioForm
from Tablas.models import Cliente as c
from Tablas.models import Comentario as comentarios
from django.views.generic import CreateView, UpdateView
from Tablas.models import CustomUser
from django.urls import reverse_lazy
from datetime import datetime, date, timedelta
from itertools import islice
from django.utils.dateparse import parse_date

def home(request):
    ultimos_comentarios = list(islice(reversed(comentarios.objects.all()), 0, 5)) #obtengo los ultimos 5 comentarios
    context =  {'comentarios': ultimos_comentarios}
    return render(request, 'home.html', context)

def registrar(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        cliente_form = ClienteCreationForm(request.POST)
        if form.is_valid() and cliente_form.is_valid():
            user = form.save()
            cliente = cliente_form.save(commit=False)
            cliente.usuario = user
            cliente.save()
            
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email , password=password)
            login(request, user)
            return redirect('home')
    else:
        form = ExtendedUserCreationForm()
        cliente_form = ClienteCreationForm()
    context = {'form': form, 'cliente_form': cliente_form}
    return render(request, 'registrar.html', context)

def perfil(request):
    se_ingreso_nombre = False
    se_eligio_cambiar_el_nombre = False
    cambiar_nombre = False
    se_ingreso_apellido = False
    se_eligio_cambiar_el_apellido = False
    cambiar_apellido = False
    se_ingreso_dni = False
    se_eligio_cambiar_el_dni = False
    cambiar_dni = False
    ya_existe_el_dni = False
    se_ingreso_fecha_de_nacimiento = False
    se_eligio_cambiar_la_fecha_de_nacimiento = False
    cambiar_fecha_de_nacimiento = False
    es_menor_de_edad = False
    if request.method == "POST":
        try:
            nuevo_nombre = request.POST["nombre_ingresado"]
            se_eligio_cambiar_el_nombre = True
            if nuevo_nombre != "": # EL ÚNICO CONTROL QUE PUSE ES QUE NO PONGA NADA EN EL FORMULARIO. DESPUÉS SE PODRÍAN PONER MÁS CONTROLES
                se_ingreso_nombre = True
                cambiar_nombre = True
        except:
            pass
        try:
            nuevo_apellido = request.POST["apellido_ingresado"]
            se_eligio_cambiar_el_apellido = True
            if nuevo_apellido != "": # EL ÚNICO CONTROL QUE PUSE ES QUE NO PONGA NADA EN EL FORMULARIO. DESPUÉS SE PODRÍAN PONER MÁS CONTROLES
                se_ingreso_apellido = True
                cambiar_apellido = True
        except:
            pass
        try:
            nuevo_dni = request.POST["dni_ingresado"]
            se_eligio_cambiar_el_dni = True
            if nuevo_dni != "": # DESPUÉS SE PODRÍAN PONER MÁS CONTROLES
                se_ingreso_dni = True
                clientes = c.objects.all()
                for cl in clientes:
                    if cl.usuario.id != request.user.id and cl.dni == nuevo_dni:
                        ya_existe_el_dni = True
                if not ya_existe_el_dni:
                    cambiar_dni = True
        except:
            pass
        try:
            nueva_fecha_de_nacimiento = request.POST["fecha_de_nacimiento_ingresada"]
            se_eligio_cambiar_la_fecha_de_nacimiento = True
            if nueva_fecha_de_nacimiento != "": # DESPUÉS SE PODRÍAN PONER MÁS CONTROLES
                se_ingreso_fecha_de_nacimiento = True
                nueva_fecha_de_nacimiento = parse_date(nueva_fecha_de_nacimiento)
                if (date.today() - timedelta(days=(18*365))) < nueva_fecha_de_nacimiento:
                    es_menor_de_edad = True
                else:
                    cambiar_fecha_de_nacimiento = True
        except:
            pass

    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl
   
    if cambiar_nombre:
        usuario_modificado = CustomUser.objects.get(id = request.user.id)
        usuario_modificado.first_name = nuevo_nombre
        usuario_modificado.save()
        cliente.usuario = usuario_modificado

    if cambiar_apellido:
        usuario_modificado = CustomUser.objects.get(id = request.user.id)
        usuario_modificado.last_name = nuevo_apellido
        usuario_modificado.save()
        cliente.usuario = usuario_modificado

    if cambiar_dni:
        cliente_modificado = c.objects.get(id = cliente.id)
        cliente_modificado.dni = nuevo_dni
        cliente_modificado.save()
        cliente = cliente_modificado

    if cambiar_fecha_de_nacimiento:
        cliente_modificado = c.objects.get(id = cliente.id)
        cliente_modificado.fecha_nacimiento = nueva_fecha_de_nacimiento
        cliente_modificado.save()
        cliente = cliente_modificado

    if se_eligio_cambiar_el_nombre and not se_ingreso_nombre:
        error = "No se ingresó nombre"
        contexto = {"error":error}
        return render(request,"perfil_nombre.html",contexto)

    if se_eligio_cambiar_el_apellido and not se_ingreso_apellido:
        error = "No se ingresó apellido"
        contexto = {"error":error}
        return render(request,"perfil_apellido.html",contexto)
    
    if se_eligio_cambiar_el_dni and not se_ingreso_dni:
        error = "No se ingresó dni"
        contexto = {"error":error}
        return render(request,"perfil_dni.html",contexto)
    
    if ya_existe_el_dni:
        error = "Dni repetido"
        contexto = {"error":error}
        return render(request,"perfil_dni.html",contexto)

    if se_eligio_cambiar_la_fecha_de_nacimiento and not se_ingreso_fecha_de_nacimiento:
        error = "No se ingresó fecha de nacimiento"
        contexto = {"error":error}
        return render(request,"perfil_fecha_de_nacimiento.html",contexto)

    if es_menor_de_edad:
        error = "Es menor de edad"
        contexto = {"error":error}
        return render(request,"perfil_fecha_de_nacimiento.html",contexto)

    contexto = {"cliente":cliente}
    return render(request,"perfil.html",contexto)

def perfil_nombre(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_nombre.html",contexto)

def perfil_apellido(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_apellido.html",contexto)

def perfil_dni(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_dni.html",contexto)

def perfil_fecha_de_nacimiento(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_fecha_de_nacimiento.html",contexto)

class AgregarComentarioView(CreateView):
    model = comentarios
    form_class =  AgregarComentarioForm
    template_name = 'agregar_comentario.html'

    def form_valid(self, form):
        form.instance.autor = self.request.user.cliente
        form.instance.fecha_de_creacion = datetime.today()
        return super().form_valid(form)

    success_url = reverse_lazy('home')

class ModificarComentarioView(UpdateView):
    model = comentarios
    template_name = 'modificar_comentario.html'
    fields = ('contenido',)