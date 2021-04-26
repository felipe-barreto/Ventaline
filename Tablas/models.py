from django.db import models

# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    dni = models.CharField(max_length=20,unique=True)
    email = models.EmailField(max_length=40,unique=True)
    contraseña = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    gold = models.BooleanField()
    tarjeta_cod_seguridad = models.CharField(max_length=3)
    tarjeta_fecha_vencimiento = models.DateField()
    tarjeta_nombre_titular = models.CharField(max_length=40)
    tarjeta_numero = models.CharField(max_length=16)
    
class Chofer(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    email = models.EmailField(max_length=40,unique=True)
    contraseña = models.CharField(max_length=15)
    telefono = models.CharField(max_length=15)
    class Meta: 
        verbose_name = "chofer"
        verbose_name_plural = "choferes"
    
class Combi(models.Model):
    modelo = models.CharField(max_length=15)
    patente = models.CharField(max_length=10,unique=True)
    cant_asientos = models.IntegerField()
    tipo = models.CharField(max_length=15, choices=[('Cómoda','Cómoda'), ('Súper-cómoda','Súper-cómoda')])
    chofer = models.ForeignKey(Chofer,on_delete=models.PROTECT)
    
class Producto(models.Model):
    nombre = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20)
    precio = models.IntegerField()
    
class Lugar(models.Model):
    provincia = models.CharField(max_length=20)
    nombre_ciudad = models.CharField(max_length=20)
    observaciones = models.CharField(max_length=40)
    class Meta: 
        verbose_name = "lugar"
        verbose_name_plural = "lugares"
    
class Ruta(models.Model):
    ciudad_origen = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_origen")
    ciudad_destino = models.ForeignKey(Lugar,on_delete=models.PROTECT,related_name="ciudad_destino")
    combi = models.ForeignKey(Combi,on_delete=models.PROTECT)
    datos_adicionales = models.CharField(max_length=40)
    
class Viaje(models.Model):
    ruta = models.ForeignKey(Ruta,on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    precio = models.IntegerField()
