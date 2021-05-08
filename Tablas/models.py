from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from Tablas import softdeletion as sd

# Create your models here.

class Cliente(sd.SoftDeletionModel):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20,validators=[sd.validar_dni_cliente])
    email = models.EmailField(max_length=40,unique=True)
    contraseña = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    gold = models.BooleanField()
    tarjeta_cod_seguridad = models.CharField(max_length=3)
    tarjeta_fecha_vencimiento = models.DateField()
    tarjeta_nombre_titular = models.CharField(max_length=40)
    tarjeta_numero = models.CharField(max_length=16)

    def __str__(self):
        return 'Email: %s, Nombre: %s, Apellido: %s'%(self.email, self.nombre, self.apellido)
    
class Chofer(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=40,unique=True)
    contraseña = models.CharField(max_length=15)
    telefono = models.CharField(max_length=15)
    class Meta: 
        verbose_name = "chofer"
        verbose_name_plural = "choferes"
    
    def __str__(self):
        return 'Email: %s, Nombre: %s, Apellido: %s'%(self.email, self.nombre, self.apellido)
    
class Combi(models.Model):
    modelo = models.CharField(max_length=15)
    patente = models.CharField(max_length=10,unique=True)
    cant_asientos = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=[('Cómoda','Cómoda'), ('Súper-cómoda','Súper-cómoda')])
    chofer = models.ForeignKey(Chofer,on_delete=models.PROTECT)

    def __str__(self):
        return 'Patente: %s, Tipo: %s, Cantidad de asientos: %s'%(self.patente, self.tipo, self.cant_asientos)
    
class Producto(models.Model):
    nombre = models.CharField(max_length=20,unique=True)
    tipo = models.CharField(max_length=20)
    precio = models.IntegerField()

    def __str__(self):
        return 'Nombre: %s, Tipo: %s, Precio: %s'%(self.nombre,self.tipo,self.precio)
    
class Lugar(models.Model):
    provincia = models.CharField(max_length=20)
    nombre_ciudad = models.CharField(max_length=20)
    observaciones = models.CharField(max_length=40,null=True,blank=True)
    class Meta: 
        verbose_name = "lugar"
        verbose_name_plural = "lugares"
        unique_together=('provincia','nombre_ciudad',)
    
    def __str__(self):
        return 'Ciudad: %s, Provincia: %s'%(self.nombre_ciudad,self.provincia)
    
class Ruta(models.Model):
    ciudad_origen = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_origen")
    ciudad_destino = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_destino")
    combi = models.ForeignKey(Combi,on_delete=models.PROTECT)
    datos_adicionales = models.CharField(max_length=40,null=True,blank=True)
    class Meta:
        unique_together=('ciudad_origen','ciudad_destino',)

    def clean(self):
        if (self.ciudad_origen == self.ciudad_destino):
            raise ValidationError(_('La ciudad origen y destino deben ser distintas'))
    
    def __str__(self):
        return 'Origen: (%s, %s), Destino: (%s, %s) Combi: (%s)'%(self.ciudad_origen.nombre_ciudad,self.ciudad_origen.provincia,self.ciudad_destino.nombre_ciudad,self.ciudad_destino.provincia,self.combi)
    
class Viaje(models.Model):
    ruta = models.ForeignKey(Ruta,on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    precio = models.IntegerField()

    class Meta:
        unique_together=('ruta','fecha_hora',)
    
    def __str__(self):
        return 'Ruta: ( %s ), Fecha: %s, Precio: %s'%(self.ruta,self.fecha_hora,self.precio)
