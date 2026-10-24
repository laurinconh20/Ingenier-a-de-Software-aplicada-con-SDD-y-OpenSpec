from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.espacios.models import Espacio
from apps.reservas.models import Reserva
from apps.usuarios.models import Usuario


class DashboardView(TemplateView):
    template_name = "home.html"
    recent_limit = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        if not usuario.is_authenticated:
            return context

        if usuario.has_perm("usuarios.gestionar_usuarios"):
            return self._contexto_administrador(context)
        if usuario.has_perm("usuarios.decidir_reservas"):
            return self._contexto_gestor(context)
        return self._contexto_solicitante(context)

    def _reservas_recientes(self, queryset):
        return list(
            queryset.select_related("espacio", "solicitante").order_by(
                "-fecha_creacion", "-pk"
            )[: self.recent_limit]
        )

    @staticmethod
    def _metricas_por_estado(queryset):
        resumen = queryset.aggregate(
            pendiente=Count("pk", filter=Q(estado=Reserva.Estado.PENDIENTE)),
            aprobada=Count("pk", filter=Q(estado=Reserva.Estado.APROBADA)),
            rechazada=Count("pk", filter=Q(estado=Reserva.Estado.RECHAZADA)),
            cancelada=Count("pk", filter=Q(estado=Reserva.Estado.CANCELADA)),
        )
        return {
            Reserva.Estado.PENDIENTE: resumen["pendiente"],
            Reserva.Estado.APROBADA: resumen["aprobada"],
            Reserva.Estado.RECHAZADA: resumen["rechazada"],
            Reserva.Estado.CANCELADA: resumen["cancelada"],
        }

    def _contexto_solicitante(self, context):
        queryset = Reserva.objects.filter(solicitante=self.request.user)
        recientes = self._reservas_recientes(queryset)
        context.update(
            dashboard_mode="solicitante",
            metricas=self._metricas_por_estado(queryset),
            reservas_recientes=recientes,
            dashboard_vacio=not recientes,
        )
        return context

    def _contexto_gestor(self, context):
        queryset = Reserva.objects.all()
        metricas = self._metricas_por_estado(queryset)
        recientes = self._reservas_recientes(queryset)
        context.update(
            dashboard_mode="gestor",
            metricas=metricas,
            pendientes_total=metricas[Reserva.Estado.PENDIENTE],
            reservas_total=sum(metricas.values()),
            reservas_recientes=recientes,
            dashboard_vacio=not recientes,
        )
        return context

    def _contexto_administrador(self, context):
        queryset = Reserva.objects.all()
        metricas = self._metricas_por_estado(queryset)
        recientes = self._reservas_recientes(queryset)
        context.update(
            dashboard_mode="administrador",
            metricas=metricas,
            pendientes_total=metricas[Reserva.Estado.PENDIENTE],
            reservas_total=sum(metricas.values()),
            usuarios_total=Usuario.objects.count(),
            espacios_total=Espacio.objects.count(),
            reservas_recientes=recientes,
            dashboard_vacio=not recientes,
        )
        return context
