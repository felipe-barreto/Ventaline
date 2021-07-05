from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.fields import IntegerField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.translation import gettext_lazy as _
from Tablas import softdeletion as sd
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, User
from datetime import date, datetime, timedelta, tzinfo
from django.urls import reverse
import pytz

# Create your models here.

##################################################################################################
#User customizado
##################################################################################################

# src/users/model.py
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser,sd.SoftDeletionModel):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return "Nombre: " + self.first_name + ". Apellido: " + self.last_name + ". Email: " + str(self.email) + "."

    def save(self, **kwargs):
        if ("pbkdf2" not in self.password):
            self.set_password(self.password)
        super(CustomUser, self).save(**kwargs)

##################################################################################################
#Clases
##################################################################################################

class Suspendido(sd.SoftDeletionModel):
    fecha_suspension = models.DateField(null=True,blank=True)

class Cliente(sd.SoftDeletionModel):
    usuario = models.OneToOneField(CustomUser,on_delete=models.DO_NOTHING, related_name='cliente')
    dni = models.CharField(max_length=20,validators=[sd.validar_dni_cliente])
    cantidad_de_caracteres_de_la_contraseña = models.CharField(max_length=50,null=True,blank=True)
    fecha_nacimiento = models.DateField()
    gold = models.BooleanField(default=False)
    tarjeta_cod_seguridad = models.CharField(max_length=3,null=True,blank=True)
    tarjeta_fecha_vencimiento = models.DateField(null=True,blank=True,)
    tarjeta_nombre_titular = models.CharField(max_length=40,null=True,blank=True)
    tarjeta_numero = models.CharField(max_length=16,null=True,blank=True)
    suspendido = models.BooleanField(default=False)
    fechas_de_suspension = ManyToManyField(Suspendido)
    Los_clientes_que_fueron_sospechosos_de_tener_coronavirus = models.BooleanField(default=False) # ESTO ES SOLO PARA QUE SE VEA LINDA LA PÁGINA

    def __str__(self):
        return 'Email: %s'%(self.usuario,)
    
    def delete(self):
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.usuario.email in u.email:
                coincidencias += 1 
        self.usuario.email = self.usuario.email + str(coincidencias)
        self.usuario.delete()
        return super(Cliente,self).delete()
    
    def clean(self):

        if (date.today() - timedelta(days=(18*365))) < self.fecha_nacimiento:
            raise ValidationError('Debes ser mayor de edad para poder registrarte')

        if (self.gold == False) and ((self.tarjeta_cod_seguridad!=None) or (self.tarjeta_fecha_vencimiento!=None) or (self.tarjeta_numero!=None) or (self.tarjeta_nombre_titular!=None)):
            raise ValidationError('Si quiere ingresar una tarjeta debe ser gold')
        
        if (self.gold) and ((self.tarjeta_cod_seguridad==None) or (self.tarjeta_fecha_vencimiento==None) or (self.tarjeta_numero==None) or (self.tarjeta_nombre_titular==None)):
            raise ValidationError('Debe completar todos los campos de la tarjeta')

        if self.gold and ((len(self.tarjeta_numero)<16)):
            raise ValidationError('El número de la tarjeta debe ser de 16 caracteres')
        
        if self.gold and ((len(self.tarjeta_cod_seguridad)<3)):
            raise ValidationError('El código de seguridad de la tarjeta debe ser de 3 caracteres')
        
        if self.gold and (self.tarjeta_fecha_vencimiento<=date.today()):
            raise ValidationError('La tarjeta está vencida')

    
class Chofer(sd.SoftDeletionModel):
    usuario = models.OneToOneField(CustomUser,on_delete=models.DO_NOTHING, related_name='chofer',limit_choices_to={'chofer':None,'cliente':None,'is_staff':False})
    dni = models.CharField(max_length=20,validators=[sd.validar_dni_chofer])
    telefono = models.CharField(max_length=15)
    class Meta: 
        verbose_name = "chofer"
        verbose_name_plural = "choferes"
    
    def __str__(self):
        return 'Email: %s, Nombre: %s, Apellido: %s'%(self.usuario.email, self.usuario.first_name, self.usuario.last_name)

    def delete(self):
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.usuario.email in u.email:
                coincidencias += 1 
        self.usuario.email = self.usuario.email + str(coincidencias)
        self.usuario.delete()
        return super(Chofer,self).delete()
    
class Combi(sd.SoftDeletionModel):
    modelo = models.CharField(max_length=15)
    patente = models.CharField(max_length=10,validators=[sd.validar_patente_combi])
    cant_asientos = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=[('Cómoda','Cómoda'), ('Súper-cómoda','Súper-cómoda')])
    chofer = models.ForeignKey(Chofer,on_delete=models.PROTECT)

    def __str__(self):
        return 'Patente: %s, Tipo: %s, Cantidad de asientos: %s'%(self.patente, self.tipo, self.cant_asientos)

    def delete(self):
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.chofer.usuario.email in u.email:
                coincidencias += 1 
        nuevo_usuario = CustomUser(email=(self.chofer.usuario.email + str(coincidencias)),password=self.chofer.usuario.password,first_name=self.chofer.usuario.first_name,last_name=self.chofer.usuario.last_name,is_deleted=True,deleted_at=timezone.now())
        nuevo_usuario.save()
        nuevo_chofer = Chofer(usuario=nuevo_usuario,dni=self.chofer.dni,telefono=self.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        self.chofer = nuevo_chofer
        return super(Combi,self).delete()
    
class Producto(sd.SoftDeletionModel):
    nombre = models.CharField(max_length=20,validators=[sd.validar_nombre_producto])
    tipo = models.CharField(max_length=20)
    precio = models.IntegerField()

    def __str__(self):
        return 'Nombre: %s, Tipo: %s, Precio: %s'%(self.nombre,self.tipo,self.precio)
    
    def contiene(self, str):
        return (str.lower() in self.nombre.lower())
    
class Lugar(sd.SoftDeletionModel):
    provincia = models.CharField(max_length=20)
    nombre_ciudad = models.CharField(max_length=20)
    observaciones = models.CharField(max_length=40,null=True,blank=True)
    class Meta: 
        verbose_name = "lugar"
        verbose_name_plural = "lugares"
    
    def __str__(self):
        return 'Ciudad: %s, Provincia: %s'%(self.nombre_ciudad,self.provincia)
    
    def clean(self):
        for l in Lugar.objects.all():
            if self != l:
                if ((l.provincia == self.provincia) and (l.nombre_ciudad==self.nombre_ciudad)):
                    raise ValidationError('Ya hay una con esta provincia y ciudad, por favor ingrese otra')
    
    def contiene(self, str):
        return (str.lower() in self.nombre_ciudad.lower())
    
class Ruta(sd.SoftDeletionModel):
    ciudad_origen = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_origen")
    ciudad_destino = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_destino")
    combi = models.ForeignKey(Combi,on_delete=models.PROTECT)
    datos_adicionales = models.CharField(max_length=40,null=True,blank=True)

    def clean(self):
        if (self.ciudad_origen == self.ciudad_destino):
            raise ValidationError(_('La ciudad origen y destino deben ser distintas'))
        for r in Ruta.objects.all():
            if self != r:
                if((self.ciudad_origen==r.ciudad_origen) and (self.ciudad_destino==r.ciudad_destino)):
                    raise ValidationError('Ya hay una ruta con este origen y destino')
    
    def __str__(self):
        return 'Origen: (%s, %s), Destino: (%s, %s) Combi: (%s)'%(self.ciudad_origen.nombre_ciudad,self.ciudad_origen.provincia,self.ciudad_destino.nombre_ciudad,self.ciudad_destino.provincia,self.combi)

    def delete(self):
        nuevo_origen = Lugar(provincia=self.ciudad_origen.provincia,nombre_ciudad=self.ciudad_origen.nombre_ciudad,observaciones=self.ciudad_origen.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_origen.save()
        self.ciudad_origen = nuevo_origen
        nuevo_destino = Lugar(provincia=self.ciudad_destino.provincia,nombre_ciudad=self.ciudad_destino.nombre_ciudad,observaciones=self.ciudad_destino.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_destino.save()
        self.ciudad_destino = nuevo_destino
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.combi.chofer.usuario.email in u.email:
                coincidencias += 1 
        nuevo_usuario = CustomUser(email=(self.combi.chofer.usuario.email + str(coincidencias)),password=self.combi.chofer.usuario.password,first_name=self.combi.chofer.usuario.first_name,last_name=self.combi.chofer.usuario.last_name,is_deleted=True,deleted_at=timezone.now())
        nuevo_usuario.save()
        nuevo_chofer = Chofer(usuario=nuevo_usuario,dni=self.combi.chofer.dni,telefono=self.combi.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        nueva_combi = Combi(modelo=self.combi.modelo,patente=self.combi.patente,cant_asientos=self.combi.cant_asientos,tipo=self.combi.tipo,chofer=nuevo_chofer,is_deleted=True,deleted_at=timezone.now())
        nueva_combi.save()
        self.combi = nueva_combi
        return super(Ruta,self).delete()
    
class Viaje(sd.SoftDeletionModel):
    ruta = models.ForeignKey(Ruta,on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    precio = models.IntegerField()
    datos_adicionales = models.CharField(max_length=40,null=True,blank=True)
    estado = models.TextField(max_length=30,null=True,blank=True,default='Pendiente')
    Los_viajes_vendidos = models.BooleanField(default=False) # ESTO ES SOLO PARA QUE SE VEA LINDA LA PÁGINA
    
    def __str__(self):
        return 'Ruta: ( %s ), Fecha: %s, Precio: %s'%(self.ruta,self.fecha_hora,self.precio)
    
    def clean(self):
        for v in Viaje.objects.all():
            if self != v:
                if ((self.ruta==v.ruta) and (self.fecha_hora==v.fecha_hora)):
                    raise ValidationError('Ya hay un viaje con esta ruta y fecha-hora')

    def delete(self):
        nuevo_origen = Lugar(provincia=self.ruta.ciudad_origen.provincia,nombre_ciudad=self.ruta.ciudad_origen.nombre_ciudad,observaciones=self.ruta.ciudad_origen.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_origen.save()
        nuevo_destino = Lugar(provincia=self.ruta.ciudad_destino.provincia,nombre_ciudad=self.ruta.ciudad_destino.nombre_ciudad,observaciones=self.ruta.ciudad_destino.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_destino.save()
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.ruta.combi.chofer.usuario.email in u.email:
                coincidencias += 1 
        nuevo_usuario = CustomUser(email=(self.ruta.combi.chofer.usuario.email + str(coincidencias)),password=self.ruta.combi.chofer.usuario.password,first_name=self.ruta.combi.chofer.usuario.first_name,last_name=self.ruta.combi.chofer.usuario.last_name,is_deleted=True,deleted_at=timezone.now())
        nuevo_usuario.save()
        nuevo_chofer = Chofer(usuario=nuevo_usuario,dni=self.ruta.combi.chofer.dni,telefono=self.ruta.combi.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        nueva_combi = Combi(modelo=self.ruta.combi.modelo,patente=self.ruta.combi.patente,cant_asientos=self.ruta.combi.cant_asientos,tipo=self.ruta.combi.tipo,chofer=nuevo_chofer,is_deleted=True,deleted_at=timezone.now())
        nueva_combi.save()
        nueva_ruta = Ruta(ciudad_origen=nuevo_origen,ciudad_destino=nuevo_destino,combi=nueva_combi,datos_adicionales=self.ruta.datos_adicionales,is_deleted=True,deleted_at=timezone.now())
        nueva_ruta.save()
        self.ruta = nueva_ruta
        return super(Viaje,self).delete()
    
    def viaje_futuro(self):
        res = self.fecha_hora.replace(tzinfo=None) - timedelta(hours=3)
        return (res>datetime.now())
    
    def asientos_disponibles(self):
        asientos_comprados = 0
        for c in self.compras.all():
            if c.estado != 'Rechazada':
                asientos_comprados += int(c.asientos)
        return self.ruta.combi.cant_asientos-asientos_comprados
    
    def viaje_disponible(self):
        return (self.viaje_futuro() and (self.asientos_disponibles()>0) and self.estado == 'Pendiente')
    
    def fecha_coincide(self,fecha):
        return (self.fecha_hora.date() == fecha.date())

    def dia_del_viaje(self):
        res = self.fecha_hora.replace(tzinfo=None) - timedelta(hours=3)
        return (res.date())

class Comentario(sd.SoftDeletionModel):
    autor = models.ForeignKey(Cliente, related_name="comentarios", on_delete=models.DO_NOTHING)
    contenido =  models.TextField(max_length=400)
    fecha_de_creacion =  models.DateTimeField()

    def get_absolute_url (self):
        return reverse('home')

class Compra(sd.SoftDeletionModel):
    viaje = ForeignKey(Viaje, related_name="compras", on_delete=models.PROTECT,null=True,blank=True)
    precio = IntegerField(null=True,blank=True)
    cliente = ForeignKey(Cliente, related_name="compras", on_delete=models.DO_NOTHING, null=True,blank=True)
    asientos = IntegerField(null=True,blank=True)
    estado = models.TextField(max_length=30,null=True,blank=True)

    def __str__(self):
        return 'Viaje: ( %s ) - Cliente: ( %s ) - Precio: ( %s )'%(self.viaje,self.cliente,self.precio)
    
    def delete(self):
        nuevo_origen = Lugar(provincia=self.viaje.ruta.ciudad_origen.provincia,nombre_ciudad=self.viaje.ruta.ciudad_origen.nombre_ciudad,observaciones=self.viaje.ruta.ciudad_origen.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_origen.save()
        nuevo_destino = Lugar(provincia=self.viaje.ruta.ciudad_destino.provincia,nombre_ciudad=self.viaje.ruta.ciudad_destino.nombre_ciudad,observaciones=self.viaje.ruta.ciudad_destino.observaciones,is_deleted=True,deleted_at=timezone.now())
        nuevo_destino.save()
        usuarios = CustomUser.all_objects.all()
        coincidencias = 0
        for u in usuarios:
            if self.viaje.ruta.combi.chofer.usuario.email in u.email:
                coincidencias += 1 
        nuevo_usuario = CustomUser(email=(self.viaje.ruta.combi.chofer.usuario.email + str(coincidencias)),password=self.viaje.ruta.combi.chofer.usuario.password,first_name=self.viaje.ruta.combi.chofer.usuario.first_name,last_name=self.viaje.ruta.combi.chofer.usuario.last_name,is_deleted=True,deleted_at=timezone.now())
        nuevo_usuario.save()
        nuevo_chofer = Chofer(usuario=nuevo_usuario,dni=self.viaje.ruta.combi.chofer.dni,telefono=self.viaje.ruta.combi.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        nueva_combi = Combi(modelo=self.viaje.ruta.combi.modelo,patente=self.viaje.ruta.combi.patente,cant_asientos=self.viaje.ruta.combi.cant_asientos,tipo=self.viaje.ruta.combi.tipo,chofer=nuevo_chofer,is_deleted=True,deleted_at=timezone.now())
        nueva_combi.save()
        nueva_ruta = Ruta(ciudad_origen=nuevo_origen,ciudad_destino=nuevo_destino,combi=nueva_combi,datos_adicionales=self.viaje.ruta.datos_adicionales,is_deleted=True,deleted_at=timezone.now())
        nueva_ruta.save()
        nuevo_viaje = Viaje(ruta=nueva_ruta,fecha_hora=self.viaje.fecha_hora,precio=self.viaje.precio,datos_adicionales=self.viaje.datos_adicionales,is_deleted=True,deleted_at=timezone.now())
        nuevo_viaje.save()
        self.viaje = nuevo_viaje
        self.estado = 'Cancelada'
        return super(Compra,self).delete()
    
class Compra_Producto(sd.SoftDeletionModel):
    compra = ForeignKey(Compra, related_name="compra_producto", on_delete=models.CASCADE, null=True, blank=True)
    producto = ForeignKey(Producto, related_name="compra_producto", on_delete=models.DO_NOTHING, null=True, blank=True)
    cantidad = IntegerField(null=True,blank=True)