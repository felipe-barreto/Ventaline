from django.db.models.fields import CommaSeparatedIntegerField
from django.core.exceptions import ValidationError
from django.http.request import RAISE_ERROR
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView 
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.base_user import BaseUserManager
from .forms import ExtendedUserCreationForm, ClienteCreationForm, AgregarComentarioForm
from Tablas.models import Cliente as c, Compra_Producto, Chofer as cho
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
from Tablas.models import Suspendido
import pytz

def home(request):
    try:
        if request.user.chofer:
            viajes_ordenados = sorted(list(viajes.objects.all()),key=lambda a: a.fecha_hora)
            viajes_del_chofer = []
            for viaje in viajes_ordenados:
                if (viaje.ruta.combi.chofer == request.user.chofer) and ((viaje.estado != "Finalizado") and (viaje.estado != "Suspendido")):
                    viajes_del_chofer.append(viaje)
            context =  {'viajes': viajes_del_chofer,"fecha_de_hoy":date.today()}
            return render(request, 'chofer_home.html', context)
    except:
        viajes_ordenados = sorted(list(filter(lambda each: each.viaje_disponible(), viajes.objects.all())),key=lambda a: a.fecha_hora)
        ultimos_viajes = list(islice(viajes_ordenados, 0, 10))
        ultimos_comentarios = list(islice(reversed(comentarios.objects.all()), 0, 5)) #obtengo los ultimos 5 comentarios
        context =  {'comentarios': ultimos_comentarios, 'viajes': ultimos_viajes}
        try: 
            #verifica si tiene suspension y si corresponde sacarsela
            if request.user.cliente:
                if request.user.cliente.suspendido:
                    fin_suspension = request.user.cliente.ultima_fecha_suspension() + timedelta(days=15)
                    if fin_suspension <= date.today():
                        request.user.cliente.suspendido = False
                        request.user.cliente.save()
                    else:
                        context['fin_suspension'] = fin_suspension
        except:
            pass
        return render(request, 'home.html', context)

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
            cliente.cantidad_de_caracteres_de_la_contrase??a = "*"*(len(form.cleaned_data.get('password1')))
            nuevo_suspendido = Suspendido(fecha_suspension=date(1900,1,1))
            nuevo_suspendido.save()
            cliente.save()
            cliente.fechas_de_suspension.add(nuevo_suspendido)
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

def perfil_contrase??a(request,error=None):
    contexto = {"error":error}
    return render(request,"perfil_contrase??a.html",contexto)

def perfil_contrase??a_editar(request):
    error = None
    contrase??a1 = request.POST["contrase??a_ingresada_1"]
    contrase??a2 = request.POST["contrase??a_ingresada_2"]
    if contrase??a1 == contrase??a2:
        if len(contrase??a1) >= 8:
            cliente = "Inicializo porque sino no anda"
            clientes = c.objects.all()
            for cl in clientes:
                if cl.usuario.id == request.user.id:
                    cliente = cl

            usuario_modificado = CustomUser.objects.get(id = request.user.id)
            usuario_modificado.set_password(contrase??a1)
            usuario_modificado.save()           
            cliente.usuario = usuario_modificado
            cliente.cantidad_de_caracteres_de_la_contrase??a = "*"*(len(contrase??a1))
            cliente.save()
            contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d')}
            return render(request,"perfil.html",contexto)
        else:
            error = "La contrase??a tiene que tener m??nimo 8 caracteres"
    else:
        error = "No ha ingresado la misma contrase??a dos veces"
    contexto = {"error":error}
    return render(request,"perfil_contrase??a.html",contexto)

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
            lis.append([prod.nombre, request.POST['cant_producto'], producto, prod.precio])
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
    precio_pasajes = int(request.session['compra']['precio'])
    precio_total = precio_pasajes
    precio_productos = 0
    for prod in request.session['prods_sel']:
        p = Producto.objects.get(nombre=prod[0])
        precio_productos += int((p.precio*int(prod[1])))
    precio_total += precio_productos
    subtotal = precio_total
    if request.user.cliente.gold:
        descuento = (precio_total*0.1)
        precio_total = (precio_total*0.9)
    compra = Compra(viaje=v,precio=precio_total,cliente=request.user.cliente,asientos=request.session['compra']['asientos'],estado='Pendiente')
    if request.user.cliente.gold:
        context = {'compra': compra, 'prods_sel': request.session['prods_sel'], 'precio_pasajes': precio_pasajes, 'precio_productos': precio_productos, 'subtotal': subtotal, 'descuento': descuento}
    else:
        context = {'compra': compra, 'prods_sel': request.session['prods_sel'], 'precio_pasajes': precio_pasajes, 'precio_productos': precio_productos, 'subtotal': subtotal}
    if request.method == 'POST':
        if request.POST.get('confirmar'):
            compra.save()
            for prod in request.session['prods_sel']:
                compra_prod = Compra_Producto(compra=compra, producto=(Producto.objects.get(nombre=prod[0])), cantidad= int(prod[1]))
                compra_prod.save()
            if v.asientos_vendidos_que_no_fueron_cancelados == "No hay asientos vendidos todav??a":
                v.asientos_vendidos_que_no_fueron_cancelados = str(request.session['compra']['asientos']) + "/" + str(v.ruta.combi.cant_asientos)
            else:
                cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
                cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
                cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) + int(request.session['compra']['asientos'])
                v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
            v.dinero_recaudado = v.dinero_recaudado + compra.precio
            v.save()
            return redirect('mis_compras')
        else:
            return redirect('home')
    return render(request, 'compra_viaje_confirmar.html', context)

def compra_viaje_tarjeta(request, viaje):
    help_text=None
    if request.method == 'POST':
        if request.POST.get('siguiente'):
            if len(str(request.POST['num_tarjeta']))<16:
                help_text = 'El n??mero de tarjeta debe ser de 16 d??gitos'
            elif len(str(request.POST['cod_tarjeta']))<3:
                help_text = 'El c??digo de tarjeta debe ser de 3 d??gitos'
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
            v = viajes.objects.get(id=c.viaje.id)
            cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
            cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
            cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) - int(c.asientos)
            v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
            precio_a_devolver = c.precio
            if (divmod(((c.viaje.fecha_hora.replace(tzinfo=None) - datetime.now()).total_seconds()),3600)[0]) <= 48:
                precio_a_devolver = precio_a_devolver / 2
            v.dinero_recaudado = v.dinero_recaudado - precio_a_devolver
            v.save()
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
    return render(request,'eliminar_cuenta_confirmar.html')

def tiene_viajes(request):
    cliente = "Inicializo porque sino no anda"
    clientes = c.objects.all()
    for cl in clientes:
        if cl.usuario.id == request.user.id:
            cliente = cl

    tiene_viajes_sin_hacer = False
    compras = Compra.objects.all()
    for com in compras:
        if (com.cliente.usuario.id == request.user.id) and (com.estado == "Pendiente"):
            tiene_viajes_sin_hacer = True
    
    if tiene_viajes_sin_hacer:
        contexto = {"cliente":cliente,"fecha_nacimiento":cliente.fecha_nacimiento.strftime('%Y-%m-%d'),"tiene_viajes":True}
        return render(request,"perfil.html",contexto)
    else:
        direccion = "eliminar_cuenta/" + str(cliente.pk)
        return redirect(direccion)

def chofer_perfil(request):
    chofer = "Inicializo porque sino no anda"
    choferes = cho.objects.all()
    for c in choferes:
        if c.usuario.id == request.user.id:
            chofer = c

    contexto = {"chofer":chofer}
    return render(request,"chofer_perfil.html",contexto)

def chofer_perfil_editar(request):
    editado_correctamente = True

    chofer = "Inicializo porque sino no anda"
    choferes = cho.objects.all()
    for c in choferes:
        if c.usuario.id == request.user.id:
            chofer = c


    nuevo_nombre = request.POST["nombre_ingresado"]
    nuevo_apellido = request.POST["apellido_ingresado"]
    nuevo_dni = request.POST["dni_ingresado"]

    usuario_modificado = CustomUser.objects.get(id = request.user.id)
    usuario_modificado.first_name = nuevo_nombre
    usuario_modificado.last_name = nuevo_apellido
    usuario_modificado.save()

    chofer_modificado = cho.objects.get(id = chofer.id)
    chofer_modificado.usuario = usuario_modificado

    error_con_dni = None
    for c in choferes:
        if c.usuario.id != request.user.id and c.dni == nuevo_dni:
            error_con_dni = "Ya existe el dni"
            editado_correctamente = False
    if error_con_dni != "Ya existe el dni":
        chofer_modificado.dni = nuevo_dni

    chofer_modificado.save()

    contexto = {"chofer":chofer_modificado,"error_con_dni":error_con_dni,"editado":editado_correctamente}
    return render(request,"chofer_perfil.html",contexto)

class CambiarContrase??aChofer(PasswordChangeView):
    from_class= PasswordChangeForm
    success_url =  reverse_lazy('chofer_perfil_contrase??a_confirmar')

def chofer_perfil_contrase??a_confirmar(request):
    return render(request,"chofer_perfil_contrase??a_confirmar.html")

def chofer_viaje_asistencia(request,viaje):
    v = viajes.objects.get(id=viaje)
    compras = Compra.objects.filter(viaje=v)

    if request.method == 'POST':
        if request.POST.get('iniciar_viaje'):
            for compra in compras:
                if compra.estado == 'Pendiente':
                    return redirect('chofer_viaje_confirmar_inicio', viaje, 1)
            return redirect('chofer_viaje_confirmar_inicio', viaje, 0)
        if request.POST.get('finalizar_viaje'):
            return redirect('chofer_viaje_confirmar_finalizar', viaje)

        elif request.POST.get('suspender_viaje'):
            return redirect('chofer_viaje_confirmar_suspender', viaje)

        elif request.POST.get('vender_pasajes'):
            return redirect('chofer_viaje_vender',viaje)
        
    no_hay_pasajeros = False
    if Compra.objects.filter(viaje=v).count() == 0:
        no_hay_pasajeros = True
    context = {'viaje': v, 'compras': compras,"no_hay_pasajeros":no_hay_pasajeros}
    return render(request,"chofer_viaje_asistencia.html",context)

def chofer_pasajero_sintomas(request, compra, pasaje):
    c = Compra.objects.get(id=compra)
    if request.method == 'POST':
        if request.POST.get('ingresar'):
            
            cant_sintomas = 0
            if request.POST['cabeza'] == 'si':
                cant_sintomas += 1
            if request.POST['garganta'] == 'si':
                cant_sintomas += 1
            if request.POST['muscular'] == 'si':
                cant_sintomas += 1
            if request.POST['vomitos'] == 'si':
                cant_sintomas += 1
            if request.POST['gusto'] == 'si':
                cant_sintomas += 1
            if request.POST['olfato'] == 'si':
                cant_sintomas += 1
            if request.POST['estrecho'] == 'si':
                cant_sintomas += 1

            if int(request.POST['temperatura']) >= 38 or cant_sintomas >= 2:#combinacion que da covid
                c.estado = 'Rechazada'
                c.save()
                return redirect("chofer_pasajero_suspender", compra)
            else:
                if int(pasaje) == int(c.asientos):
                    c.estado = 'Aceptada'
                    c.save()
                    return redirect("chofer_viaje_asistencia", c.viaje.id)
                else:
                    return redirect("chofer_pasajero_sintomas", compra, (int(pasaje)+1) )
    context = {'pasaje': int(pasaje), 'compra':c}
    return render(request,"chofer_pasajero_sintomas.html",context)

def chofer_pasajero_suspender(request, compra):
    comp = Compra.objects.get(id=compra)
    if request.method == 'POST':
        if request.POST.get('aceptar'):
            return redirect("chofer_viaje_asistencia", comp.viaje.id)
    cliente = comp.cliente  
    cliente.suspendido = True
    nuevo_suspendido = Suspendido(fecha_suspension=date.today())
    nuevo_suspendido.save()
    cliente.fechas_de_suspension.add(nuevo_suspendido)

    compras_cliente = list(filter(lambda each: each.viaje.viaje_futuro(), list(cliente.compras.all()) ))
    limite_suspension = date.today() + timedelta(days=15)
    if comp in compras_cliente:
        compras_cliente.remove(comp)
    compras_cancelar = []
    for c in compras_cliente:
        if limite_suspension>c.viaje.fecha_hora.date():
            compras_cancelar.append(c)
    v = viajes.objects.get(id=comp.viaje.id)
    cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
    cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
    cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) - int(comp.asientos)
    v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
    v.dinero_recaudado = v.dinero_recaudado - comp.precio
    v.save()
    for compra_cancelar in compras_cancelar:
        for p in compra_cancelar.compra_producto.all():
            p.delete()
        v = viajes.objects.get(id=compra_cancelar.viaje.id)
        cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
        cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
        cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) - int(compra_cancelar.asientos)
        v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
        v.dinero_recaudado = v.dinero_recaudado - compra_cancelar.precio
        v.save()
        compra_cancelar.delete()

    cliente.save()
    context = {'cliente': cliente}
    return render(request,"chofer_pasajero_suspender.html",context)

def chofer_viaje_confirmar_inicio(request, viaje, estado):
    v = viajes.objects.get(id=viaje)
    compras = Compra.objects.filter(viaje=v)
    if request.method == 'POST':
        if request.POST.get('iniciar'):
            for compra in compras:
                if compra.estado == 'Pendiente':
                    compra.estado = 'Ausente'
                    compra.save()
            v.estado = 'Iniciado'
            v.save()
        return redirect('chofer_viaje_asistencia', viaje)
    if estado == 1:
        context = {'help_text': 'Todav??a hay pasajeros cuyos s??ntomas no han sido subidos al sistema, estos pasajeros ser??n contados como ausentes en el viaje y no se les reembolsar?? el dinero'}
    else:
        context = {'help_text': 'Los s??ntomas de todos los pasajeros han sido ingresados al sistema correctamente'}
    return render(request, "chofer_viaje_confirmar_inicio.html", context)

def chofer_viaje_confirmar_finalizar(request, viaje):
    v = viajes.objects.get(id=viaje)
    if request.method == 'POST':
        if request.POST.get('finalizar'):
            v.estado = 'Finalizado'
            v.save()
        return redirect('chofer_viaje_asistencia', viaje)
    return render(request, "chofer_viaje_confirmar_finalizar.html")

def chofer_viaje_confirmar_suspender(request,viaje):
    v = viajes.objects.get(id=viaje)
    compras = Compra.objects.filter(viaje=v)
    if request.method == 'POST':
        if request.POST.get('suspender'):
            for compra in compras:
                if compra.estado != 'Rechazada':
                    compra.estado = 'Suspendida'
                    v = viajes.objects.get(id=compra.viaje.id)
                    cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
                    cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
                    cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) - int(compra.asientos)
                    v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
                    v.dinero_recaudado = v.dinero_recaudado - compra.precio
                    v.save()
                    compra.save()
            v.estado = 'Suspendido'
            v.save()
        return redirect('chofer_viaje_asistencia', viaje)
    return render(request, "chofer_viaje_confirmar_suspender.html")

def chofer_viaje_vender(request, viaje):
    v = viajes.objects.get(id=viaje)
    context = {"viaje":v}
    if request.method == 'POST':
        if request.POST.get('ingresar'):
            email = BaseUserManager.normalize_email(request.POST['email'])
            print (email)
            users = CustomUser.objects.all()
            for user in users:
                if user.email == email:
                    if not user.cliente.suspendido:
                        return redirect('chofer_viaje_vender_ya_registrado',viaje=viaje, id_user=user.id, cant_pasajes= int(request.POST['cant_pasajes']))
                    else:
                        context = {"viaje":v, "suspendido":True}
                        return render(request, "chofer_viaje_vender.html", context)
            if ('@' in email) and ('.com' in email):
                return redirect('chofer_viaje_vender_no_registrado',viaje,str(email),int(request.POST['cant_pasajes']))
        if request.POST.get('cancelar'):
            return redirect("chofer_viaje_asistencia", viaje)
    return render(request, "chofer_viaje_vender.html", context) 

def chofer_viaje_vender_no_registrado(request,viaje,email,cant_pasajes):
    v = viajes.objects.get(id=viaje)
    if request.method == "POST":
        if request.POST.get('ingresar'):
            nueva_fecha_de_nacimiento = request.POST['fecha_de_nacimiento']
            nueva_fecha_de_nacimiento = parse_date(nueva_fecha_de_nacimiento)
            nuevo_dni = request.POST["dni"]
            if c.objects.filter(dni=nuevo_dni):
                context = {"email":email, "viaje": v, "cant_pasajes":cant_pasajes, "error_dni":True}
                return render(request, 'chofer_viaje_vender_no_registrado.html',context)
            try:
                if (date.today() - timedelta(days=(18*365))) < nueva_fecha_de_nacimiento:
                    context = {"email":email, "viaje": v, "cant_pasajes":cant_pasajes, "menor":True}
                    return render(request, 'chofer_viaje_vender_no_registrado.html',context) 
            except:
                context = {"email":email, "viaje": v, "cant_pasajes":cant_pasajes, "fecha":True}
                return render(request, 'chofer_viaje_vender_no_registrado.html',context) 
            if nuevo_dni !="":
                nuevo_usuario = CustomUser(first_name = "Pendiente", last_name = "Pendiente", password = str(nuevo_dni)+"V", email = email)
                nuevo_usuario.save()
                nuevo_cliente = c(usuario = nuevo_usuario, dni = nuevo_dni, fecha_nacimiento = nueva_fecha_de_nacimiento, cantidad_de_caracteres_de_la_contrase??a= "*"*(len(nuevo_dni)+1))
                nuevo_cliente.save()
                return redirect('chofer_pasajero_sintomas_sin_compra', viaje,nuevo_usuario.id, cant_pasajes,1)
        if request.POST.get('cancelar'):
            return redirect("chofer_viaje_asistencia", viaje)
    context = {"email":email, "viaje": v, "cant_pasajes":cant_pasajes}
    return render(request, 'chofer_viaje_vender_no_registrado.html',context)

def chofer_viaje_vender_ya_registrado(request,viaje,id_user,cant_pasajes):
    v = viajes.objects.get(id=viaje)
    usuario = CustomUser.objects.get(id=id_user)
    context = {"viaje": v, "usuario":usuario, "cant_pasajes":int(cant_pasajes)}
    if request.method == 'POST':
        if request.POST.get('continuar'):
            return redirect('chofer_pasajero_sintomas_sin_compra', viaje,usuario.id, cant_pasajes,1)
        if request.POST.get('cancelar'):
            return redirect("chofer_viaje_asistencia", viaje)
    return render (request, 'chofer_viaje_vender_ya_registrado.html',context)

def chofer_pasajero_sintomas_sin_compra(request,viaje,id_user,cant_pasajes,pasaje_actual):
    usuario = CustomUser.objects.get(id=id_user)
    v = viajes.objects.get(id=viaje)
    if request.method == 'POST':
        if request.POST.get('ingresar'):
            cant_sintomas = 0
            if request.POST['cabeza'] == 'si':
                cant_sintomas += 1
            if request.POST['garganta'] == 'si':
                cant_sintomas += 1
            if request.POST['muscular'] == 'si':
                cant_sintomas += 1
            if request.POST['vomitos'] == 'si':
                cant_sintomas += 1
            if request.POST['gusto'] == 'si':
                cant_sintomas += 1
            if request.POST['olfato'] == 'si':
                cant_sintomas += 1
            if request.POST['estrecho'] == 'si':
                cant_sintomas += 1

            if int(request.POST['temperatura']) >= 38 or cant_sintomas >= 2:#combinacion que da covid
                compra_rechazada =  Compra(viaje=v, precio=v.precio*cant_pasajes, cliente = usuario.cliente, asientos =cant_pasajes, estado = "Rechazada")
                compra_rechazada.save()
                return redirect("chofer_pasajero_suspender", compra_rechazada.id)
            else:
                if int(pasaje_actual) == int(cant_pasajes):
                    compra_aceptada =  Compra(viaje=v, precio=v.precio*cant_pasajes, cliente = usuario.cliente, asientos =cant_pasajes, estado = "Aceptada")
                    compra_aceptada.save()
                    if v.asientos_vendidos_que_no_fueron_cancelados == "No hay asientos vendidos todav??a":
                        v.asientos_vendidos_que_no_fueron_cancelados = str(compra_aceptada.asientos) + "/" + str(v.ruta.combi.cant_asientos)
                    else:
                        cantidad_actual_de_asientos = v.asientos_vendidos_que_no_fueron_cancelados.split("/")
                        cantidad_actual_de_asientos = cantidad_actual_de_asientos[0]
                        cantidad_actual_de_asientos = int(cantidad_actual_de_asientos) + int(compra_aceptada.asientos)
                        v.asientos_vendidos_que_no_fueron_cancelados = str(cantidad_actual_de_asientos) + "/" + str(v.ruta.combi.cant_asientos)
                    v.dinero_recaudado = v.dinero_recaudado + compra_aceptada.precio
                    v.save()
                    return redirect("chofer_viaje_vender_confirmar", compra_aceptada.id)
                else:
                    return redirect('chofer_pasajero_sintomas_sin_compra', viaje, usuario.id, cant_pasajes, (int(pasaje_actual)+1) )
    context = {"viaje":v, "pasaje": int(pasaje_actual), "cantidad_pasajes":int(cant_pasajes), "usuario":usuario}
    return render(request,"chofer_pasajero_sintomas_sin_compra.html",context)

def chofer_viaje_vender_confirmar(request, id_compra):
    compra = Compra.objects.get(id=id_compra)
    context = {"compra":compra}
    if request.method == 'POST':
        if request.POST.get('Volver'):
            return redirect("chofer_viaje_asistencia", compra.viaje.id)
    return render(request, "chofer_viaje_vender_confirmar.html",context)

def chofer_mis_viajes(request):
    viajes_ordenados = sorted(list(viajes.objects.all()),key=lambda a: a.fecha_hora)
    viajes_del_chofer = []
    for viaje in viajes_ordenados:
        if (viaje.ruta.combi.chofer == request.user.chofer) and ((viaje.estado == "Finalizado") or (viaje.estado=="Suspendido")):
            viajes_del_chofer.append(viaje)
    context =  {'viajes': viajes_del_chofer}
    return render(request, 'chofer_mis_viajes.html', context)