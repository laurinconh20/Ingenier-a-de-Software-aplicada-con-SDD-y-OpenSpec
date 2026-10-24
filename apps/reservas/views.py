"""Presentación web del módulo de reservas."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView

from apps.espacios.models import Espacio

from .forms import (
    AprobacionForm,
    CancelacionAdministrativaForm,
    CancelacionPropiaForm,
    ConsultaDisponibilidadForm,
    HistorialFiltroForm,
    RechazoForm,
    SolicitudReservaForm,
)
from .models import Reserva
from .services import (
    aprobar_reserva,
    cancelar_reserva_administrativa,
    cancelar_reserva_propia,
    crear_solicitud,
    esta_disponible,
    rechazar_reserva,
)


class SolicitudCreateView(PermissionRequiredMixin, FormView):
    permission_required = "usuarios.crear_solicitudes"
    form_class = SolicitudReservaForm
    template_name = "reservas/form.html"
    success_url = reverse_lazy("reservas:list")

    def get_initial(self):
        initial = super().get_initial()
        espacio_id = self.request.GET.get("espacio")
        if espacio_id:
            espacio = Espacio.objects.filter(pk=espacio_id, activo=True).first()
            if espacio:
                initial["espacio"] = espacio
        return initial

    def form_valid(self, form):
        crear_solicitud(solicitante=self.request.user, **form.cleaned_data)
        messages.success(self.request, "La solicitud fue registrada en estado pendiente.")
        return super().form_valid(form)


class SolicitudListView(LoginRequiredMixin, ListView):
    template_name = "reservas/list.html"
    context_object_name = "reservas"
    paginate_by = 25

    def get_queryset(self):
        queryset = (
            self.request.user.reservas.select_related("espacio")
            .prefetch_related("eventos__responsable")
            .all()
        )
        estado = self.request.GET.get("estado")
        if estado in Reserva.Estado.values:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_paginate_by(self, queryset):
        return _tamano_pagina(self.request)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            estados=Reserva.Estado.choices,
            estado_actual=self.request.GET.get("estado", ""),
            **kwargs,
        )


class SolicitudDetailView(LoginRequiredMixin, DetailView):
    template_name = "reservas/detail.html"
    context_object_name = "reserva"

    def get_queryset(self):
        return (
            self.request.user.reservas.select_related("espacio")
            .prefetch_related("eventos__responsable")
            .all()
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            cancelacion_form=CancelacionPropiaForm(), **kwargs
        )


class DisponibilidadView(LoginRequiredMixin, FormView):
    form_class = ConsultaDisponibilidadForm
    template_name = "reservas/disponibilidad.html"

    def get_initial(self):
        initial = super().get_initial()
        espacio_id = self.request.GET.get("espacio")
        if espacio_id:
            espacio = Espacio.objects.filter(pk=espacio_id, activo=True).first()
            if espacio:
                initial["espacio"] = espacio
        return initial

    def form_valid(self, form):
        disponible = esta_disponible(**form.cleaned_data)
        return self.render_to_response(
            self.get_context_data(form=form, disponible=disponible)
        )


class DecisionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "usuarios.decidir_reservas"
    model = Reserva
    template_name = "reservas/decision.html"
    context_object_name = "reserva"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            aprobacion_form=AprobacionForm(),
            rechazo_form=RechazoForm(),
            cancelacion_form=CancelacionAdministrativaForm(),
            **kwargs,
        )


class AprobarView(PermissionRequiredMixin, View):
    permission_required = "usuarios.decidir_reservas"

    def post(self, request, pk):
        form = AprobacionForm(request.POST)
        if form.is_valid():
            try:
                aprobar_reserva(
                    reserva_id=pk,
                    actor=request.user,
                    observacion=form.cleaned_data["observacion"],
                )
                messages.success(request, "La solicitud fue aprobada.")
            except ValidationError as error:
                messages.error(request, error.messages[0])
        else:
            messages.error(request, "La observación no puede superar 1.000 caracteres.")
        return redirect("reservas:decision", pk=pk)


class RechazarView(PermissionRequiredMixin, View):
    permission_required = "usuarios.decidir_reservas"

    def post(self, request, pk):
        form = RechazoForm(request.POST)
        if form.is_valid():
            try:
                rechazar_reserva(
                    reserva_id=pk, actor=request.user, motivo=form.cleaned_data["motivo"]
                )
                messages.success(request, "La solicitud fue rechazada.")
            except ValidationError as error:
                messages.error(request, error.messages[0])
        else:
            messages.error(request, "El motivo debe contener entre 1 y 1.000 caracteres.")
        return redirect("reservas:decision", pk=pk)


class CancelarPropiaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        form = CancelacionPropiaForm(request.POST)
        if form.is_valid():
            try:
                cancelar_reserva_propia(
                    reserva_id=pk,
                    actor=request.user,
                    motivo=form.cleaned_data["motivo"],
                )
                messages.success(request, "La reserva fue cancelada.")
            except ValidationError as error:
                messages.error(request, error.messages[0])
        else:
            messages.error(request, "El motivo no puede superar 1.000 caracteres.")
        return redirect("reservas:detail", pk=pk)


class CancelarAdministrativaView(PermissionRequiredMixin, View):
    permission_required = "usuarios.cancelar_reservas"

    def post(self, request, pk):
        form = CancelacionAdministrativaForm(request.POST)
        if form.is_valid():
            try:
                cancelar_reserva_administrativa(
                    reserva_id=pk,
                    actor=request.user,
                    motivo=form.cleaned_data["motivo"],
                )
                messages.success(request, "La reserva fue cancelada.")
            except ValidationError as error:
                messages.error(request, error.messages[0])
        else:
            messages.error(request, "El motivo debe contener entre 1 y 1.000 caracteres.")
        return redirect("reservas:decision", pk=pk)


def _tamano_pagina(request):
    try:
        solicitado = int(request.GET.get("tamano", 25))
    except (TypeError, ValueError):
        return 25
    return min(max(solicitado, 1), 100)


class HistorialGlobalView(PermissionRequiredMixin, ListView):
    permission_required = "usuarios.consultar_historial_global"
    model = Reserva
    template_name = "reservas/historial_global.html"
    context_object_name = "reservas"
    paginate_by = 25

    def get_queryset(self):
        queryset = Reserva.objects.select_related(
            "espacio", "solicitante"
        ).prefetch_related("eventos__responsable")
        self.filtro = HistorialFiltroForm(self.request.GET)
        if not self.filtro.is_valid():
            return queryset.none()
        datos = self.filtro.cleaned_data
        if datos.get("estado"):
            queryset = queryset.filter(estado=datos["estado"])
        if datos.get("espacio"):
            queryset = queryset.filter(espacio=datos["espacio"])
        if datos.get("solicitante"):
            queryset = queryset.filter(solicitante=datos["solicitante"])
        if datos.get("desde"):
            limite_desde = datetime.combine(
                datos["desde"], time.min, tzinfo=ZoneInfo(settings.TIME_ZONE)
            )
            queryset = queryset.filter(inicio__gte=limite_desde)
        if datos.get("hasta"):
            limite_hasta = datetime.combine(
                datos["hasta"] + timedelta(days=1),
                time.min,
                tzinfo=ZoneInfo(settings.TIME_ZONE),
            )
            queryset = queryset.filter(inicio__lt=limite_hasta)
        return queryset

    def get_paginate_by(self, queryset):
        return _tamano_pagina(self.request)

    def get_context_data(self, **kwargs):
        return super().get_context_data(filtro=self.filtro, **kwargs)

