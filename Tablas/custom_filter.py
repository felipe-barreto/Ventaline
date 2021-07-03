from rangefilter.filter import DateRangeFilter
from .models import Suspendido, Compra
from datetime import date

class ClientesCoronavirusFiltro(DateRangeFilter):
    parameter_name = 'Los_clientes_que_fueron_sospechosos_de_tener_coronavirus'
    
    def queryset(self, request, queryset):
        if not self.used_parameters:
            return queryset
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data and (validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__gte'] or validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__lte']):
                clientes = []
                for elemento in range(queryset.count()):
                    clientes.append(queryset[elemento])
                clientes_covid = []
                for cl in clientes:
                    ids_a_suspendidos = cl.fechas_de_suspension.all()
                    for un_id in ids_a_suspendidos:
                        suspendido = Suspendido.objects.get(id=un_id.id)
                        if suspendido.fecha_suspension != date(1900,1,1):
                            if validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__gte'] == None:
                                # DESDE VACÍO
                                if suspendido.fecha_suspension <= validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__lte']:
                                    clientes_covid.append(cl.id)
                            elif validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__lte'] == None:
                                # HASTA VACÍO
                                if validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__gte'] <= suspendido.fecha_suspension:
                                    clientes_covid.append(cl.id)
                            elif validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__gte'] <= suspendido.fecha_suspension <= validated_data['Los_clientes_que_fueron_sospechosos_de_tener_coronavirus__range__lte']:
                                clientes_covid.append(cl.id)
                return queryset.filter(id__in=clientes_covid)
        return queryset

class ViajesVendidosFiltro(DateRangeFilter):
    parameter_name = 'Los_viajes_vendidos'
    
    def queryset(self, request, queryset):
        if not self.used_parameters:
            return queryset
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data and (validated_data['Los_viajes_vendidos__range__gte'] or validated_data['Los_viajes_vendidos__range__lte']):
                viajes = []
                for elemento in range(queryset.count()):
                    viajes.append(queryset[elemento])
                compras = Compra.objects.all()
                viajes_vendidos = []
                for v in viajes:
                    for c in compras:
                        if v.id == c.viaje.id:
                            if validated_data['Los_viajes_vendidos__range__gte'] == None:
                                # DESDE VACÍO
                                if (v.fecha_hora).date() <= validated_data['Los_viajes_vendidos__range__lte']:
                                    viajes_vendidos.append(v.id)
                            elif validated_data['Los_viajes_vendidos__range__lte'] == None:
                                # HASTA VACÍO
                                if validated_data['Los_viajes_vendidos__range__gte'] <= (v.fecha_hora).date():
                                    viajes_vendidos.append(v.id)
                            elif validated_data['Los_viajes_vendidos__range__gte'] <= (v.fecha_hora).date() <= validated_data['Los_viajes_vendidos__range__lte']:
                                viajes_vendidos.append(v.id)
                return queryset.filter(id__in=viajes_vendidos)
        return queryset