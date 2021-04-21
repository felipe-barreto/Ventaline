from django.db import models

# Create your models here.

class Clientes(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20)
    email = models.EmailField(max_length=40)
    contraseña = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    gold = models.BooleanField()
    tarjeta_cod_seguridad = models.CharField(max_length=3)
    tarjeta_fecha_vencimiento = models.DateField()
    tarjeta_nombre_titular = models.CharField(max_length=40)
    tarjeta_numero = models.CharField(max_length=16)
    
class Choferes(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    email = models.EmailField(max_length=40)
    contraseña = models.CharField(max_length=15)
    telefono = models.CharField(max_length=15)
    
class Combis(models.Model):
    modelo = models.CharField(max_length=15)
    patente = models.CharField(max_length=10)
    cant_asientos = models.IntegerField()
    tipo = models.CharField(max_length=15)
    chofer = models.IntegerField()
    
class Productos(models.Model):
    nombre = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)
    precio = models.IntegerField()
    
class Lugares(models.Model):
    provincia = models.CharField(max_length=20)
    nombre_ciudad = models.CharField(max_length=20)
    obervaciones = models.CharField(max_length=40)
    
class Rutas(models.Model):
    ciudad_origen = models.CharField(max_length=20)
    ciudad_destino = models.CharField(max_length=20)
    combi = models.IntegerField()
    datos_adicionales = models.CharField(max_length=40)
    
class Viajes(models.Model):
    ruta = models.IntegerField()
    fecha_hora = models.DateTimeField()
    precio = models.IntegerField()
