from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import (
    CorreoAuthenticationForm,
    PerfilForm,
    UsuarioAdminUpdateForm,
    UsuarioCreateForm,
)
from .models import Usuario


class IniciarSesionView(LoginView):
    authentication_form = CorreoAuthenticationForm
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True


class CerrarSesionView(LogoutView):
    next_page = reverse_lazy("home")


class UsuarioListView(PermissionRequiredMixin, ListView):
    permission_required = "usuarios.gestionar_usuarios"
    model = Usuario
    template_name = "usuarios/list.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("groups")


class UsuarioCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "usuarios.gestionar_usuarios"
    form_class = UsuarioCreateForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:list")


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PerfilForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        return self.request.user


class UsuarioUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "usuarios.gestionar_usuarios"
    model = Usuario
    form_class = UsuarioAdminUpdateForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:list")

