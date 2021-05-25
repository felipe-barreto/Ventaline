from django.db.models.fields import CommaSeparatedIntegerField
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ExtendedUserCreationForm, ClienteCreationForm, AgregarComentarioForm
from Tablas.models import Cliente as c
from Tablas.models import Comentario as comentarios
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from PaginaWeb.modificar_perfil import ModificarNombre
from django import forms
from datetime import datetime
from itertools import islice

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
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl
    contexto = {"cliente":cliente}
    return render(request,"perfil.html",contexto)

def perfil_nombre(request):
    return render(request,"perfil_nombre.html")

@method_decorator(login_required, name="dispatch")
class NombreUpdate(UpdateView):
    form_class = ModificarNombre
    success_url = reverse_lazy("perfil")

    def get_object(self):
        return self.request.user

    def get_form(self, form_class=None):
        form = super(NombreUpdate,self).get_form()
        form.fields["nombre"].widget = forms.TextInput(attrs={"class":"form-control mb-2", "placeholder":"Ingrese su nuevo nombre"})
        print(form.fields["nombre"])
        return form

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