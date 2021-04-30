from django.contrib import admin
import Tablas.models as tablas
# Register your models here.

class ClientesAdmin(admin.ModelAdmin):
    list_display=("nombre","apellido","dni","email","contraseña","gold","tarjeta_numero")
    #search_fields=('nombre','apellido','dni','email')

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['email','contraseña']
        else:
            return []

class ChoferesAdmin(admin.ModelAdmin):
    list_display=("nombre","apellido","dni","email","contraseña","telefono")
    #search_fields=('nombre','apellido',)

    def get_readonly_fields(self, request,obj):
        if obj:
            return ['email','contraseña']
        else:
            return []

class CombisAdmin(admin.ModelAdmin):
    list_display=("modelo","patente","cant_asientos","tipo","chofer")
    #search_fields=('patente',)
    #list_filter=('tipo',)

class ProductosAdmin(admin.ModelAdmin):
    list_display=("nombre","tipo","precio")
    #search_fields=('nombre',)

class LugaresAdmin(admin.ModelAdmin):
    list_display=("provincia","nombre_ciudad","observaciones")
    #search_fields=('nombre_ciudad',)

class RutasAdmin(admin.ModelAdmin):
    list_display=("ciudad_origen","ciudad_destino","combi","datos_adicionales")

class ViajesAdmin(admin.ModelAdmin):
    list_display=("ruta","fecha_hora","precio")

admin.site.register(tablas.Cliente, ClientesAdmin)
admin.site.register(tablas.Chofer, ChoferesAdmin)
admin.site.register(tablas.Combi, CombisAdmin)
admin.site.register(tablas.Producto, ProductosAdmin)
admin.site.register(tablas.Lugar, LugaresAdmin)
admin.site.register(tablas.Ruta, RutasAdmin)
admin.site.register(tablas.Viaje, ViajesAdmin)