from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EspacioForm, HorarioEspacioForm
from .models import Espacio, HorarioEspacio
from .services import actualizar_espacio, eliminar_horario, guardar_horario


class EspacioListView(LoginRequiredMixin, ListView):
    model = Espacio
    template_name = "espacios/list.html"
    context_object_name = "espacios"


class EspacioDetailView(LoginRequiredMixin, DetailView):
    model = Espacio
    template_name = "espacios/detail.html"
    context_object_name = "espacio"


class EspacioCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "usuarios.gestionar_espacios"
    model = Espacio
    form_class = EspacioForm
    template_name = "espacios/form.html"
    success_url = reverse_lazy("espacios:list")


class EspacioUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "usuarios.gestionar_espacios"
    model = Espacio
    form_class = EspacioForm
    template_name = "espacios/form.html"
    success_url = reverse_lazy("espacios:list")

    def form_valid(self, form):
        try:
            self.object = actualizar_espacio(
                espacio_id=self.object.pk,
                datos=form.cleaned_data,
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class HorarioCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "usuarios.gestionar_espacios"
    form_class = HorarioEspacioForm
    template_name = "espacios/horario_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.espacio = get_object_or_404(Espacio, pk=kwargs["espacio_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "espacio": self.espacio}

    def get_success_url(self):
        return reverse_lazy("espacios:detail", args=[self.espacio.pk])

    def form_valid(self, form):
        try:
            self.object = guardar_horario(
                espacio_id=self.espacio.pk,
                datos=form.cleaned_data,
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class HorarioUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "usuarios.gestionar_espacios"
    model = HorarioEspacio
    form_class = HorarioEspacioForm
    template_name = "espacios/horario_form.html"

    def get_success_url(self):
        return reverse_lazy("espacios:detail", args=[self.object.espacio_id])

    def form_valid(self, form):
        try:
            self.object = guardar_horario(
                espacio_id=self.object.espacio_id,
                horario_id=self.object.pk,
                datos=form.cleaned_data,
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class HorarioDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "usuarios.gestionar_espacios"
    model = HorarioEspacio
    template_name = "espacios/horario_confirm_delete.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            espacio_id = eliminar_horario(horario_id=self.object.pk)
        except ValidationError as error:
            messages.error(request, error.messages[0])
            return redirect("espacios:detail", pk=self.object.espacio_id)
        messages.success(request, "El horario fue eliminado correctamente.")
        return redirect("espacios:detail", pk=espacio_id)

    def get_success_url(self):
        return reverse_lazy("espacios:detail", args=[self.object.espacio_id])

