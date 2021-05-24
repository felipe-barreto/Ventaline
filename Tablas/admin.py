from django.contrib import admin
import Tablas.models as tablas

# Register your models here.

class ClientesAdmin(admin.ModelAdmin):
    list_display=("usuario","dni","fecha_nacimiento","gold","tarjeta_cod_seguridad","tarjeta_fecha_vencimiento","tarjeta_nombre_titular","tarjeta_numero")
    #search_fields=('nombre','apellido','dni','email')
    fields = ("usuario","dni","fecha_nacimiento","gold","tarjeta_cod_seguridad","tarjeta_fecha_vencimiento","tarjeta_nombre_titular","tarjeta_numero")


    def has_add_permission(self,request):
        return False

    def has_change_permission(self,request,obj=None):
        return False
    
    def has_delete_permission(self,request,obj=None):
        return False

class ChoferesAdmin(admin.ModelAdmin):
    list_display=("nombre","apellido","dni","email","contraseña","telefono")
    fields = ("nombre","apellido","dni","email","contraseña","telefono",)
    #search_fields=('nombre','apellido',)

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['email','contraseña','is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

class CombisAdmin(admin.ModelAdmin):
    list_display=("modelo","patente","cant_asientos","tipo","chofer")
    fields = ("modelo","patente","cant_asientos","tipo","chofer")
    #search_fields=('patente',)
    #list_filter=('tipo',)

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['cant_asientos','is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

class ProductosAdmin(admin.ModelAdmin):
    list_display=("nombre","tipo","precio")
    fields = ("nombre","tipo","precio")
    #search_fields=('nombre',)

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

class LugaresAdmin(admin.ModelAdmin):
    list_display=("provincia","nombre_ciudad","observaciones")
    #search_fields=('nombre_ciudad',)
    fields = ("provincia","nombre_ciudad","observaciones")

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['provincia','nombre_ciudad','is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

class RutasAdmin(admin.ModelAdmin):
    list_display=("ciudad_origen","ciudad_destino","combi","datos_adicionales")
    fields = ("ciudad_origen","ciudad_destino","combi","datos_adicionales")

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['ciudad_origen','ciudad_destino','combi','is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

class ViajesAdmin(admin.ModelAdmin):
    list_display=("ruta","fecha_hora","precio","datos_adicionales")
    fields = ("ruta","fecha_hora","precio","datos_adicionales")

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['ruta','fecha_hora','precio','is_deleted','deleted_at']
        else:
            return ['is_deleted','deleted_at']

admin.site.register(tablas.Cliente, ClientesAdmin)
admin.site.register(tablas.Chofer, ChoferesAdmin)
admin.site.register(tablas.Combi, CombisAdmin)
admin.site.register(tablas.Producto, ProductosAdmin)
admin.site.register(tablas.Lugar, LugaresAdmin)
admin.site.register(tablas.Ruta, RutasAdmin)
admin.site.register(tablas.Viaje, ViajesAdmin)
admin.site.register(tablas.Comentario)