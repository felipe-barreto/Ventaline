from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ExtendedUserCreationForm, ClienteCreationForm
from Tablas.models import Cliente as c

def home(request):
    return render(request, 'home.html')

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