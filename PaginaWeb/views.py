from django.db.models.fields import CommaSeparatedIntegerField
from django.core.exceptions import ValidationError
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ExtendedUserCreationForm, ClienteCreationForm, AgregarComentarioForm
from Tablas.models import Cliente as c, Compra_Producto
from Tablas.models import Comentario as comentarios
from django.views.generic import CreateView, UpdateView
from Tablas.models import CustomUser
from django.urls import reverse_lazy
from datetime import datetime, date, timedelta
from itertools import islice
from django.utils.dateparse import parse_date
from Tablas.models import Viaje as viajes
from Tablas.models import Compra
from Tablas.models import Producto
import pytz

def home(request):
    viajes_ordenados = sorted(list(filter(lambda each: each.viaje_disponible(), viajes.objects.all())),key=lambda a: a.fecha_hora)
    ultimos_viajes = list(islice(viajes_ordenados, 0, 10))
    ultimos_comentarios = list(islice(reversed(comentarios.objects.all()), 0, 5)) #obtengo los ultimos 5 comentarios
    context =  {'comentarios': ultimos_comentarios, 'viajes': ultimos_viajes}
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
    se_ingreso_contraseña = False
    se_eligio_cambiar_la_contraseña = False
    cambiar_contraseña = False
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
            nueva_contraseña = request.POST["contraseña_ingresada"]
            se_eligio_cambiar_la_contraseña = True
            if nueva_contraseña != "": # EL ÚNICO CONTROL QUE PUSE ES QUE NO PONGA NADA EN EL FORMULARIO. DESPUÉS SE PODRÍAN PONER MÁS CONTROLES
                se_ingreso_contraseña = True
                cambiar_contraseña = True
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

    if cambiar_contraseña:
        usuario_modificado = CustomUser.objects.get(id = request.user.id)
        usuario_modificado.set_password(nueva_contraseña)
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

    if se_eligio_cambiar_la_contraseña and not se_ingreso_contraseña:
        error = "No se ingresó contraseña"
        contexto = {"error":error}
        return render(request,"perfil_contraseña.html",contexto)
    
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

def perfil_contraseña(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_contraseña.html",contexto)

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


def buscar_viaje(request):
    lista_viajes = list(sorted(list(filter(lambda each: each.viaje_disponible(), viajes.objects.all())),key=lambda a: a.fecha_hora))
    #each.viaje_futuro() va a pasar a ser each.viaje_disponible ya que hay que tener en cuenta los viajes llenos
    if request.method == 'POST':
        if request.POST['ciudad_origen']:
            lista_viajes = list(filter(lambda x: x.ruta.ciudad_origen.contiene(request.POST['ciudad_origen']), lista_viajes))
        
        if request.POST['ciudad_destino']:
            lista_viajes = list(filter(lambda x: x.ruta.ciudad_destino.contiene(request.POST['ciudad_destino']), lista_viajes))
        
        if request.POST['fecha_salida']:
            fecha = datetime.strptime(str(request.POST['fecha_salida']), '%Y-%m-%d')
            lista_viajes = list(filter(lambda x: x.fecha_coincide(fecha), lista_viajes))

    context = {'viajes': lista_viajes,}
    return render(request, 'buscar_viaje.html', context)

def compra_viaje_asientos(request, viaje):
    v = viajes.objects.get(id=viaje)
    if request.method == 'POST':
        if request.POST.get('siguiente'):
            precio = int(request.POST['cant_pasajes'])*v.precio
            compra_dic = {'precio':precio, 'asientos':request.POST['cant_pasajes']}
            request.session['compra'] = compra_dic
            return redirect('compra_viaje_productos', viaje, 0)
        else:
            return redirect('home')
    context = {'viaje': v,}
    return render(request, 'compra_viaje_asientos.html', context)

def compra_viaje_productos(request, viaje, producto):
    context = {'viaje':viaje, 'productos':list(Producto.objects.all()),}
    if request.method == 'POST':
        if request.POST.get('agregar'):
            prod = Producto.objects.get(id=producto)
            lis = list(request.session['prods_sel'])
            lis.append([prod.nombre, request.POST['cant_producto'], producto])
            request.session['prods_sel'] = lis
            #request.session['prods_sel'].extend([[prod.nombre, request.POST['cant_producto']]])
        elif request.POST.get('buscar'):
            context['productos'] = list(filter(lambda x: x.contiene(request.POST['nombre_producto']), list(Producto.objects.all())))
        elif request.POST.get('siguiente'):
            if request.user.cliente.gold:
                return redirect('compra_viaje_confirmar', viaje)
            else:
                return redirect('compra_viaje_tarjeta', viaje)
        else:
            return redirect('home')
    elif request.method != 'POST' and producto==0:
        request.session['prods_sel'] = [] 
    else:
        prod_eliminar = Producto.objects.get(id=producto)
        lis = list(request.session['prods_sel'])
        for p in lis:
            if p[0]==prod_eliminar.nombre:
                lis.remove(p)
                break
        request.session['prods_sel'] = lis

    for p in request.session['prods_sel']:
        prod = Producto.objects.get(nombre=p[0])
        if prod in context['productos']:
            context['productos'].remove(prod)

    context['productos_seleccionados'] = request.session['prods_sel']
    return render(request, 'compra_viaje_productos.html', context)

def compra_viaje_confirmar(request, viaje):
    v = viajes.objects.get(id=viaje)
    precio_total=int(request.session['compra']['precio'])
    for prod in request.session['prods_sel']:
        p = Producto.objects.get(nombre=prod[0])
        precio_total += int((p.precio*int(prod[1])))
    if request.user.cliente.gold:
        precio_total = (precio_total*0.9)
    compra = Compra(viaje=v,precio=precio_total,cliente=request.user.cliente,asientos=request.session['compra']['asientos'])
    context = {'compra': compra, 'prods_sel': request.session['prods_sel']}
    if request.method == 'POST':
        if request.POST.get('confirmar'):
            compra.save()
            for prod in request.session['prods_sel']:
                compra_prod = Compra_Producto(compra=compra, producto=(Producto.objects.get(nombre=prod[0])), cantidad= int(prod[1]))
                compra_prod.save()
            return redirect('home')
        else:
            return redirect('home')
    return render(request, 'compra_viaje_confirmar.html', context)

def compra_viaje_tarjeta(request, viaje):
    help_text=None
    if request.method == 'POST':
        if request.POST.get('siguiente'):
            if len(str(request.POST['num_tarjeta']))<16:
                help_text = 'El número de tarjeta debe ser de 16 dígitos'
            elif len(str(request.POST['cod_tarjeta']))<3:
                help_text = 'El código de tarjeta debe ser de 3 dígitos'
            else:
                return redirect('compra_viaje_confirmar', viaje)
        else:
            return redirect('home')
    context = {'viaje_id': viaje, 'fecha_hoy': datetime.today().strftime('%Y-%m-%d'), 'help_text': help_text}
    return render(request, 'compra_viaje_tarjeta.html', context)