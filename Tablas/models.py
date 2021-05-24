from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from Tablas import softdeletion as sd
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, User
from datetime import date, datetime, timedelta

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
        return self.email

##################################################################################################
#Clases
##################################################################################################

class Cliente(sd.SoftDeletionModel):
    usuario = models.OneToOneField(CustomUser,on_delete=models.DO_NOTHING, related_name='cliente')
    dni = models.CharField(max_length=20,validators=[sd.validar_dni_cliente])
    #email = models.EmailField(max_length=40,validators=[sd.validar_email_cliente])
    fecha_nacimiento = models.DateField()
    gold = models.BooleanField(default=False)
    tarjeta_cod_seguridad = models.CharField(max_length=3,null=True,blank=True)
    tarjeta_fecha_vencimiento = models.DateField(null=True,blank=True,)
    tarjeta_nombre_titular = models.CharField(max_length=40,null=True,blank=True)
    tarjeta_numero = models.CharField(max_length=16,null=True,blank=True)

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

        if (self.gold == False)and ((self.tarjeta_cod_seguridad!=None) or (self.tarjeta_fecha_vencimiento!=None) or (self.tarjeta_numero!=None) or (self.tarjeta_nombre_titular!=None)):
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
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20,validators=[sd.validar_dni_chofer])
    email = models.EmailField(max_length=40,validators=[sd.validar_email_chofer])
    contraseña = models.CharField(max_length=15)
    telefono = models.CharField(max_length=15)
    class Meta: 
        verbose_name = "chofer"
        verbose_name_plural = "choferes"
    
    def __str__(self):
        return 'Email: %s, Nombre: %s, Apellido: %s'%(self.email, self.nombre, self.apellido)
    
class Combi(sd.SoftDeletionModel):
    modelo = models.CharField(max_length=15)
    patente = models.CharField(max_length=10,validators=[sd.validar_patente_combi])
    cant_asientos = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=[('Cómoda','Cómoda'), ('Súper-cómoda','Súper-cómoda')])
    chofer = models.ForeignKey(Chofer,on_delete=models.PROTECT)

    def __str__(self):
        return 'Patente: %s, Tipo: %s, Cantidad de asientos: %s'%(self.patente, self.tipo, self.cant_asientos)

    def delete(self):
        nuevo_chofer = Chofer(nombre=self.chofer.nombre,apellido=self.chofer.apellido,dni=self.chofer.dni,email=self.chofer.email,contraseña=self.chofer.contraseña,telefono=self.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        self.chofer = nuevo_chofer
        return super(Combi,self).delete()
    
class Producto(sd.SoftDeletionModel):
    nombre = models.CharField(max_length=20,validators=[sd.validar_nombre_producto])
    tipo = models.CharField(max_length=20)
    precio = models.IntegerField()

    def __str__(self):
        return 'Nombre: %s, Tipo: %s, Precio: %s'%(self.nombre,self.tipo,self.precio)
    
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
        nuevo_chofer = Chofer(nombre=self.combi.chofer.nombre,apellido=self.combi.chofer.apellido,dni=self.combi.chofer.dni,email=self.combi.chofer.email,contraseña=self.combi.chofer.contraseña,telefono=self.combi.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
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
        nuevo_chofer = Chofer(nombre=self.ruta.combi.chofer.nombre,apellido=self.ruta.combi.chofer.apellido,dni=self.ruta.combi.chofer.dni,email=self.ruta.combi.chofer.email,contraseña=self.ruta.combi.chofer.contraseña,telefono=self.ruta.combi.chofer.telefono,is_deleted=True,deleted_at=timezone.now())
        nuevo_chofer.save()
        nueva_combi = Combi(modelo=self.ruta.combi.modelo,patente=self.ruta.combi.patente,cant_asientos=self.ruta.combi.cant_asientos,tipo=self.ruta.combi.tipo,chofer=nuevo_chofer,is_deleted=True,deleted_at=timezone.now())
        nueva_combi.save()
        nueva_ruta = Ruta(ciudad_origen=nuevo_origen,ciudad_destino=nuevo_destino,combi=nueva_combi,datos_adicionales=self.ruta.datos_adicionales,is_deleted=True,deleted_at=timezone.now())
        nueva_ruta.save()
        self.ruta = nueva_ruta
        return super(Viaje,self).delete()

class Comentario(sd.SoftDeletionModel):
    autor = models.ForeignKey(Cliente, related_name="comentarios", on_delete=models.DO_NOTHING)
    contenido =  models.TextField(max_length=400)
    fecha_de_creacion =  models.DateTimeField()