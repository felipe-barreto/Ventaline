from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from Tablas import models as m

#CLASES PARA SOFT DELETION

class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)

class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class SoftDeletionModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()

#FUNCIONES DE VALIDACION

def validar_dni_cliente(value):
    clientes = m.Cliente.objects.all()
    for c in clientes:
        if c.dni == value:
            raise ValidationError('Ya hay un cliente con este dni, por favor ingrese otro')

def validar_email_cliente(value):
    clientes = m.Cliente.objects.all()
    for c in clientes:
        if c.email == value:
            raise ValidationError('Ya hay un cliente con este email, por favor ingrese otro')

def validar_dni_chofer(value):
    choferes = m.Chofer.objects.all()
    for c in choferes:
        if c.dni == value:
            raise ValidationError('Ya hay un chofer con este dni, por favor ingrese otro')

def validar_email_chofer(value):
    choferes = m.Chofer.objects.all()
    for c in choferes:
        if c.email == value:
            raise ValidationError('Ya hay un chofer con este email, por favor ingrese otro')

def validar_patente_combi(value):
    combis = m.Combi.objects.all()
    for c in combis:
        if c.patente == value:
            raise ValidationError('Ya hay una combi con esta patente, por favor ingrese otra')

def validar_nombre_producto(value):
    productos = m.Producto.objects.all()
    for p in productos:
        if p.nombre == value:
            raise ValidationError('Ya hay un producto con este nombre, por favor ingrese otro')