from django.db.models.fields import CommaSeparatedIntegerField
from django.core.exceptions import ValidationError
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import ExtendedUserCreationForm, ClienteCreationForm, AgregarComentarioForm
from Tablas.models import Cliente as c, Compra_Producto
from Tablas.models import Comentario as comentarios
from django.views.generic import CreateView, UpdateView, DeleteView
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
    try:
        if request.user.cliente:
            viajes_ordenados = sorted(list(filter(lambda each: each.viaje_disponible(), viajes.objects.all())),key=lambda a: a.fecha_hora)
            ultimos_viajes = list(islice(viajes_ordenados, 0, 10))
            ultimos_comentarios = list(islice(reversed(comentarios.objects.all()), 0, 5)) #obtengo los ultimos 5 comentarios
            context =  {'comentarios': ultimos_comentarios, 'viajes': ultimos_viajes}
            return render(request, 'home.html', context)
    except:
        viajes_ordenados = sorted(list(filter(lambda each: each.viaje_disponible(), viajes.objects.all())),key=lambda a: a.fecha_hora)
        viajes_del_chofer = []
        for viaje in viajes_ordenados:
            if viaje.ruta.combi.chofer == request.user.chofer:
                viajes_del_chofer.append (viaje)
        context =  {'viajes': viajes_del_chofer}
        return render(request, 'chofer_home.html', context)

def mis_comentarios(request):
    todos_los_comentarios = comentarios.objects.all()
    mis_comentarios=[]
    for c in todos_los_comentarios:
        if c.autor == request.user.cliente:
            mis_comentarios.append(c)
    context =  {'comentarios': mis_comentarios}
    return render(request, 'mis_comentarios.html', context)

def registrar(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        cliente_form = ClienteCreationForm(request.POST)
        if form.is_valid() and cliente_form.is_valid():
            user = form.save()
            cliente = cliente_form.save(commit=False)
            cliente.usuario = user
            cliente.cantidad_de_caracteres_de_la_contraseña = "*"*(len(form.cleaned_data.get('password1')))
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

    contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d')}
    return render(request,"perfil.html",contexto)

def perfil_editar(request):
    editado_correctamente = True

    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    nuevo_nombre = request.POST["nombre_ingresado"]
    nuevo_apellido = request.POST["apellido_ingresado"]
    nuevo_dni = request.POST["dni_ingresado"]
    nueva_fecha_de_nacimiento = request.POST["fecha_de_nacimiento_ingresada"]

    usuario_modificado = CustomUser.objects.get(id = request.user.id)
    usuario_modificado.first_name = nuevo_nombre
    usuario_modificado.last_name = nuevo_apellido
    usuario_modificado.save()

    cliente_modificado = c.objects.get(id = cliente.id)
    cliente_modificado.usuario = usuario_modificado

    error_con_dni = None
    for cl in clientes:
        if cl.usuario.id != request.user.id and cl.dni == nuevo_dni:
            error_con_dni = "Ya existe el dni"
            editado_correctamente = False
    if error_con_dni != "Ya existe el dni":
        cliente_modificado.dni = nuevo_dni

    error_con_fecha_de_nacimiento = None
    nueva_fecha_de_nacimiento = parse_date(nueva_fecha_de_nacimiento)
    if (date.today() - timedelta(days=(18*365))) < nueva_fecha_de_nacimiento:
        error_con_fecha_de_nacimiento = "Es menor de edad"
        editado_correctamente = False
    else:
        cliente_modificado.fecha_nacimiento = nueva_fecha_de_nacimiento

    cliente_modificado.save()

    contexto = {"cliente":cliente_modificado,"fecha_nacimiento":cliente_modificado.fecha_nacimiento.strftime('%Y-%m-%d'),
    "error_con_dni":error_con_dni,"error_con_fecha_de_nacimiento":error_con_fecha_de_nacimiento,"editado":editado_correctamente}
    return render(request,"perfil.html",contexto)

def perfil_contraseña(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_contraseña.html",contexto)

def perfil_contraseña_editar(request):
    error = None
    contraseña1 = request.POST["contraseña_ingresada_1"]
    contraseña2 = request.POST["contraseña_ingresada_2"]
    if contraseña1 == contraseña2:
        if len(contraseña1) >= 8:
            cliente = "Inicializo porque sino no anda"
            clientes = c.objects.all()
            for cl in clientes:
                if cl.usuario.id == request.user.id:
                    cliente = cl

            usuario_modificado = CustomUser.objects.get(id = request.user.id)
            usuario_modificado.set_password(contraseña1)
            usuario_modificado.save()           
            cliente.usuario = usuario_modificado
            contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d')}
            return render(request,"perfil.html",contexto)
        else:
            error = "La contraseña tiene que tener mínimo 8 caracteres"
    else:
        error = "No ha ingresado la misma contraseña dos veces"
    contexto = {"error":error}
    return render(request,"perfil_contraseña.html",contexto)

def perfil_tipo_gold(request,error=None):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    contexto = {"cliente":cliente,"error":error,"fecha_de_vencimiento":cliente.tarjeta_fecha_vencimiento.strftime('%Y-%m-%d')}
    return render(request,"perfil_tipo_gold.html",contexto)

def perfil_tipo_gold_editar(request,error=None):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    nuevo_codigo_de_seguridad = request.POST["codigo_de_seguridad"]
    nueva_fecha_de_vencimiento = request.POST["fecha_de_vencimiento"]
    nuevo_nombre_titular = request.POST["nombre_titular"]
    nuevo_numero = request.POST["numero"]

    nueva_fecha_de_vencimiento = parse_date(nueva_fecha_de_vencimiento)
    if date.today() < nueva_fecha_de_vencimiento:
        cliente_modificado = c.objects.get(id = cliente.id)
        cliente_modificado.tarjeta_cod_seguridad = nuevo_codigo_de_seguridad
        cliente_modificado.tarjeta_fecha_vencimiento = nueva_fecha_de_vencimiento
        cliente_modificado.tarjeta_nombre_titular = nuevo_nombre_titular
        cliente_modificado.tarjeta_numero = nuevo_numero
        cliente_modificado.save()
        cliente = cliente_modificado
    else:
        contexto = {"cliente":cliente,"error":"Tarjeta vencida","fecha_de_vencimiento":cliente.tarjeta_fecha_vencimiento.strftime('%Y-%m-%d')}
        return render(request,"perfil_tipo_gold.html",contexto)

    contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d')}
    return render(request,"perfil.html",contexto)

def perfil_tipo_pasar_a_comun(request):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl
    
    if request.POST.get('confirmar'):
        cliente_modificado = c.objects.get(id = cliente.id)
        cliente_modificado.gold = False
        cliente_modificado.save()

        contexto = {"cliente":cliente_modificado,"fecha_nacimiento":cliente_modificado.fecha_nacimiento.strftime('%Y-%m-%d')}
        return render(request,"perfil.html",contexto)
    else:
        contexto = {"cliente":cliente,"error":None,"fecha_de_vencimiento":cliente.tarjeta_fecha_vencimiento.strftime('%Y-%m-%d')}
        return render(request,"perfil_tipo_gold.html",contexto)

def perfil_tipo_pasar_a_comun_confirmar(request):
    return render(request,"perfil_tipo_pasar_a_comun.html")

def perfil_tipo_comun(request,error=None):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    contexto = {"cliente":cliente,"error":error}
    return render(request,"perfil_tipo_comun.html",contexto)

def perfil_tipo_comun_editar(request):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    nuevo_codigo_de_seguridad = request.POST["codigo_de_seguridad"]
    nueva_fecha_de_vencimiento = request.POST["fecha_de_vencimiento"]
    nuevo_nombre_titular = request.POST["nombre_titular"]
    nuevo_numero = request.POST["numero"]

    nueva_fecha_de_vencimiento = parse_date(nueva_fecha_de_vencimiento)
    if date.today() < nueva_fecha_de_vencimiento:
        cliente_modificado = c.objects.get(id = cliente.id)
        cliente_modificado.gold = True
        cliente_modificado.tarjeta_cod_seguridad = nuevo_codigo_de_seguridad
        cliente_modificado.tarjeta_fecha_vencimiento = nueva_fecha_de_vencimiento
        cliente_modificado.tarjeta_nombre_titular = nuevo_nombre_titular
        cliente_modificado.tarjeta_numero = nuevo_numero
        cliente_modificado.save()
        cliente = cliente_modificado
    else:
        cliente.tarjeta_cod_seguridad = nuevo_codigo_de_seguridad
        cliente.tarjeta_nombre_titular = nuevo_nombre_titular
        cliente.tarjeta_numero = nuevo_numero
        contexto = {"cliente":cliente,"error":"Tarjeta vencida","con_valores_por_defecto":True}
        return render(request,"perfil_tipo_comun.html",contexto)

    contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d')}
    return render(request,"perfil.html",contexto)

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

class EliminarComentarioView(DeleteView):
    model = comentarios
    template_name = 'eliminar_comentario.html'
    success_url = reverse_lazy('home')

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
            #if request.user.cliente.gold:
             #   return redirect('compra_viaje_confirmar', viaje)
            #else:
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
    compra = Compra(viaje=v,precio=precio_total,cliente=request.user.cliente,asientos=request.session['compra']['asientos'],estado='Pendiente')
    context = {'compra': compra, 'prods_sel': request.session['prods_sel']}
    if request.method == 'POST':
        if request.POST.get('confirmar'):
            compra.save()
            for prod in request.session['prods_sel']:
                compra_prod = Compra_Producto(compra=compra, producto=(Producto.objects.get(nombre=prod[0])), cantidad= int(prod[1]))
                compra_prod.save()
            return redirect('mis_compras')
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
        elif request.POST.get('tarjeta_gold'):
            return redirect('compra_viaje_confirmar', viaje)
        else:
            return redirect('home')
    context = {'viaje_id': viaje, 'fecha_hoy': datetime.today().strftime('%Y-%m-%d'), 'help_text': help_text, 'cliente': request.user.cliente}
    return render(request, 'compra_viaje_tarjeta.html', context)

def mis_compras(request):
    compras = []
    for c in Compra.all_objects.all():
        if c.cliente == request.user.cliente:
            compras.append(c)
    #context = {'compras': reversed(request.user.cliente.compras.all())}
    context = {'compras': reversed(compras)}
    return render(request, 'mis_compras.html', context)

def compra_detalle(request,compra):
    c = Compra.all_objects.get(id=compra)
    prods = []
    for cp in Compra_Producto.all_objects.all():
        if c == cp.compra:
            prods.append(cp)
    #prods = c.compra_producto.all()
    cancelar = (c.viaje.fecha_hora.replace(tzinfo=None) > datetime.now())and(c.estado == 'Pendiente')
    context = {'compra': c, 'productos': prods, 'cancelar': cancelar}
    return render(request, 'compra_detalle.html', context)

def compra_cancelar(request,compra):
    c = Compra.objects.get(id=compra)
    if request.method == 'POST':
        if request.POST.get('si'):
            for p in c.compra_producto.all():
                p.delete()
            c.delete()
        return redirect('mis_compras')
    horas = divmod(((c.viaje.fecha_hora.replace(tzinfo=None) - datetime.now()).total_seconds()),3600)[0]
    if horas>48:
        devolucion = '100%'
    else:
        devolucion = '50%'
    context = {'devolucion': devolucion}
    return render(request, 'compra_cancelar.html', context)

class EliminarCuentaView(DeleteView):
    model = c
    template_name = 'eliminar_cuenta.html'
    success_url = reverse_lazy('eliminar_cuenta_confirmar')

def eliminar_cuenta_confirmar(request):
    logout(request)
    return redirect('home')